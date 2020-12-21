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
  echo "-r, --reg                     container registry e.g. ghcr.io for GitHub container registry, default: docker hub"
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
      echo "-r, --reg                 container registry e.g. ghcr.io for GitHub container registry, default: docker hub"
      echo "-v, --version             image tag, default: github commit id"
      exit 0
      ;;
    -deployment)
      DEPLOYMENT="$2"
      shift
      shift
      ;;
    -reg)
      CONTAINER_REGISTRY="$2"
      shift
      shift
      ;;
    -version)
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

if [ -z "$VERSION" ]
then
  echo "Version is not set!. Using commit id as version"
  VERSION=$(git rev-parse --short HEAD)
fi

echo "Container registry/owner = $CONTAINER_REG_OWNER"

if [ -z "$DEPLOYMENT" ]
then
  VERSION=test
  docker build -t $CONTAINER_REG_OWNER/minimal-notebook:$VERSION minimal-notebook
  docker run -it --rm -d -p 8880:8888 $CONTAINER_REG_OWNER/minimal-notebook:$VERSION

  docker build -t $CONTAINER_REG_OWNER/notebook:$VERSION notebook
  docker run -it --rm -d -p 8881:8888 $CONTAINER_REG_OWNER/notebook:$VERSION

  docker build -t $CONTAINER_REG_OWNER/ngshare:$VERSION ngshare
  docker run -it --rm -d -p 8883:8888 $CONTAINER_REG_OWNER/ngshare:$VERSION

  # Build e2x k8s-hub
  cd hub
  for k8s_version in */; do
    K8S_VERSION=${k8s_version%/}
    echo "Building k8s-hub:$K8S_VERSION"
    docker build -t $CONTAINER_REG_OWNER/k8s-hub:$K8S_VERSION $K8S_VERSION
  done

  docker images
  docker ps

elif [ "$DEPLOYMENT" = "dev" ] 
then
  docker build -t $CONTAINER_REG_OWNER/minimal-notebook-$DEPLOYMENT:$VERSION minimal-notebook
  docker run -it --rm -d -p 8880:8888 $CONTAINER_REG_OWNER/minimal-notebook-$DEPLOYMENT:$VERSION

  docker build -t $CONTAINER_REG_OWNER/notebook-$DEPLOYMENT:$VERSION notebook
  docker run -it --rm -d -p 8881:8888 $CONTAINER_REG_OWNER/notebook-$DEPLOYMENT:$VERSION

  docker build -t $CONTAINER_REG_OWNER/ngshare-$DEPLOYMENT:$VERSION ngshare
  docker run -it --rm -d -p 8883:8888 $CONTAINER_REG_OWNER/ngshare-$DEPLOYEMTN:$VERSION

  # Build e2x k8s-hub
  cd hub
  for k8s_version in */; do
    K8S_VERSION=${k8s_version%/}
    echo "Building k8s-hub:$K8S_VERSION"
    docker build -t $CONTAINER_REG_OWNER/k8s-hub-$DEPLOYMENT:$K8S_VERSION $K8S_VERSION
  done

  docker images
  docker ps

elif [ "$DEPLOYMENT" = "prod" ] 
then
  docker build -t $CONTAINER_REG_OWNER/minimal-notebook:$VERSION minimal-notebook
  docker run -it --rm -d -p 8880:8888 $CONTAINER_REG_OWNER/minimal-notebook:$VERSION

  docker build -t $CONTAINER_REG_OWNER/notebook:$VERSION notebook
  docker run -it --rm -d -p 8881:8888 $CONTAINER_REG_OWNER/notebook:$VERSION

  docker build -t $CONTAINER_REG_OWNER/ngshare:$VERSION ngshare
  docker run -it --rm -d -p 8883:8888 $CONTAINER_REG_OWNER/ngshare:$VERSION

  # Build e2x k8s-hub
  cd hub
  for k8s_version in */; do
    K8S_VERSION=${k8s_version%/}
    echo "Building k8s-hub:$K8S_VERSION"
    docker build -t $CONTAINER_REG_OWNER/k8s-hub:$K8S_VERSION $K8S_VERSION
  done

  docker images
  docker ps
fi
