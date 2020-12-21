# Build and deploy images

DEPLOYMENT=""
CONTAINER_REGISTRY=""
VERSION=""

if [ $# -eq 0 ]
then
  echo "Usage: bash build-and-deploy.sh"
  echo " "
  echo "options:"
  echo "-h, --help                    show brief help"
  echo "-d, --deployment              deployment (dev or prod), default: is empty or not published to registry"
  echo "-r, --registry                container registry e.g. ghcr.io for GitHub container registry, default: docker hub"
  echo "-v, --version                 image tag, default: github commit id"
  exit 0
fi

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "Usage: bash build-and-deploy.sh"
      echo " "
      echo "options:"
      echo "-h, --help                show brief help"
      echo "-d, --deployment          deployment (dev or prod), default: is empty or not published to registry"
      echo "-r, --registry            container registry e.g. ghcr.io for GitHub container registry, default: docker hub"
      echo "-v, --version             image tag, default: github commit id"
      exit 0
      ;;
    -d|--deployment)
      DEPLOYMENT="$2"
      shift
      shift
      ;;
    -r|--registry)
      CONTAINER_REGISTRY="$2"
      shift
      shift
      ;;
    -v|--version)
      VERSION="$2"
      shift
      shift
      ;;
    *)
      break
      ;;
  esac
done

if [ -z "$CONTAINER_REGISTRY" ]
then
  echo "Container registry is not set!. Using docker hub registry"
  CONTAINER_REG_OWNER=digiklausur
else
  echo "Using $CONTAINER_REGISTRY registry"
  OWNER=digiklausur/docker-stacks
  CONTAINER_REG_OWNER=$CONTAINER_REGISTRY/$OWNER
fi

echo "Container registry/owner = $CONTAINER_REG_OWNER"

if [ -z "$VERSION" ]
then
  echo "Version is not set!. Using commit id as version"
  VERSION=$(git rev-parse --short HEAD)
fi

echo "Image version: $VERSION"
echo "Deployment: $DEPLOYMENT"

sudo apt-get install -y -qq figlet
function fancy_print {
    echo "################################################################################"
    figlet -t $1
    echo "################################################################################"
}


function build_image {
  if [ "$1" = "dev" ]
  then
    IMAGE_SUFFIX="-dev"
  else
    IMAGE_SUFFIX=""
  fi

  docker build -t $CONTAINER_REG_OWNER/minimal-notebook$IMAGE_SUFFIX:$VERSION minimal-notebook
  docker tag $CONTAINER_REG_OWNER/minimal-notebook$IMAGE_SUFFIX:$VERSION $CONTAINER_REG_OWNER/minimal-notebook$IMAGE_SUFFIX:latest 
  docker run -it --rm -d -p 8880:8888 $CONTAINER_REG_OWNER/minimal-notebook$IMAGE_SUFFIX:$VERSION

  docker build -t $CONTAINER_REG_OWNER/notebook$IMAGE_SUFFIX:$VERSION notebook
  docker tag $CONTAINER_REG_OWNER/notebook$IMAGE_SUFFIX:$VERSION $CONTAINER_REG_OWNER/notebook$IMAGE_SUFFIX:latest
  docker run -it --rm -d -p 8881:8888 $CONTAINER_REG_OWNER/notebook$IMAGE_SUFFIX:$VERSION

  docker build -t $CONTAINER_REG_OWNER/ngshare$IMAGE_SUFFIX:$VERSION ngshare
  docker tag $CONTAINER_REG_OWNER/ngshare$IMAGE_SUFFIX:$VERSION $CONTAINER_REG_OWNER/ngshare$IMAGE_SUFFIX:latest
  docker run -it --rm -d -p 8883:8888 $CONTAINER_REG_OWNER/ngshare$IMAGE_SUFFIX:$VERSION

  # Build e2x k8s-hub
  cd hub
  for k8s_version in */; do
    K8S_VERSION=${k8s_version%/}
    echo "Building k8s-hub:$K8S_VERSION"
    docker build -t $CONTAINER_REG_OWNER/k8s-hub$IMAGE_SUFFIX:$K8S_VERSION $K8S_VERSION
  done
  cd ..
}

function push_image {
  if [ "$1" = "dev" ]
  then
    IMAGE_SUFFIX="-dev"
  else
    IMAGE_SUFFIX=""
  fi

  docker push $CONTAINER_REG_OWNER/minimal-notebook$IMAGE_SUFFIX:$VERSION
  docker push $CONTAINER_REG_OWNER/minimal-notebook$IMAGE_SUFFIX:latest
  docker push $CONTAINER_REG_OWNER/notebook$IMAGE_SUFFIX:$VERSION
  docker push $CONTAINER_REG_OWNER/notebook$IMAGE_SUFFIX:latest
  docker push $CONTAINER_REG_OWNER/ngshare$IMAGE_SUFFIX:$VERSION
  docker push $CONTAINER_REG_OWNER/ngshare$IMAGE_SUFFIX:latest

  cd hub
  for k8s_version in */; do
    K8S_VERSION=${k8s_version%/}
    docker push $CONTAINER_REG_OWNER/k8s-hub$IMAGE_SUFFIX:$K8S_VERSION
  done
  cd ..
}


if [ -z "$DEPLOYMENT" ]
then
  fancy_print "Building images"
  build_image

  docker images
  docker ps
fi

if [ "$DEPLOYMENT" = "dev" ] 
then
  fancy_print "Building $DEPLOYMENT images"
  build_image "dev"

  fancy_print "Pushing $DEPLOYMENT images"
  push_image "dev"

  docker images
  docker ps

elif [ "$DEPLOYMENT" = "prod" ] 
then
  fancy_print "Building $DEPLOYMENT images"
  build_image "prod"

  fancy_print "Pushing $DEPLOYMENT images"
  push_image "prod"
  
  docker images
  docker ps
fi
