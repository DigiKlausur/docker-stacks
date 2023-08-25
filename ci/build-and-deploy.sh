# Build and deploy images
# Copyright e2x project, Hochschule-Bonn-Rhein-Sieg


DEPLOYMENT="dev"
CONTAINER_REGISTRY="ghcr.io"
VERSION=""
PUBLISH="none"
IMAGE="all"

show_help() {
  echo "Usage: bash build-and-deploy.sh"
  echo " "
  echo "options:"
  echo "-h, --help                    show brief help"
  echo "-d, --deployment              deployment (dev or prod), default: is empty or not published to registry"
  echo "-r, --registry                container registry e.g. ghcr.io for GitHub container registry, default: docker hub"
  echo "-v, --version                 image tag, default: github commit id"
  echo "-p, --publish                 option whether to publish <all> or <latest> (default: all), all means publish all tags"
  echo "-i, --image                   image to build minimal-notebook|datascience-notebook|notebook|exam-notebook (default: all)"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      show_help
      exit 0
      ;;
    -d|--deployment)
      DEPLOYMENT="$2"
      shift 2
      ;;
    -r|--registry)
      CONTAINER_REGISTRY="$2"
      shift 2
      ;;
    -v|--version)
      VERSION="$2"
      shift 2
      ;;
    -p|--publish)
      PUBLISH="$2"
      shift 2
      ;;
    -i|--image)
      IMAGE="$2"
      shift 2
      ;;
    *)
      echo "Invalid argument: $1"
      show_help
      exit 1
      ;;
  esac
done

if [ -z "$CONTAINER_REGISTRY" ]
then
  echo "Container registry is not set!. Using docker hub registry"
  CONTAINER_REG_OWNER=ghcr.io/digiklausur/docker-stacks
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

if [ "$DEPLOYMENT" = "dev" ]; then
  IMAGE_SUFFIX="-dev"
  E2XGRADER_BRANCH="dev"
elif [ "$DEPLOYMENT" = "prod" ]; then
  IMAGE_SUFFIX=""
  E2XGRADER_BRANCH="master"
else
  echo "Deployment argument is unknown $DEPLOYMENT"
  exit 1
fi

function build_and_publish_single_image {
  IMAGE_DIR=$1
  IMAGE_TAG=$2
  PORT=$3
  PUBLISH_IMAGE=$4
  BASE_IMAGE=$5

  echo "Image to build: $IMAGE_TAG"
  echo "Base image: $BASE_IMAGE"

  if [ -z "$BASE_IMAGE" ]; then
    if ! docker build -t $IMAGE_TAG $IMAGE_DIR; then
      echo "Docker build failed $IMAGE_TAG"
      exit 1
    fi
  else
    if ! docker build -t $IMAGE_TAG --build-arg IMAGE_SOURCE=$BASE_IMAGE $IMAGE_DIR; then
      echo "Docker build failed $IMAGE_TAG"
      exit 1
    fi
  fi

  if docker run -it --rm -d -p $PORT:8888 $IMAGE_TAG;
  then
    echo "$IMAGE_TAG is running";
  else
    echo "Failed to run $IMAGE_TAG" && exit 1;
  fi

  if [ "$PUBLISH_IMAGE" = true ]
  then
    echo "Pushing $IMAGE_TAG"
    docker push $IMAGE_TAG
  else
    echo "$IMAGE_TAG is NOT published"
  fi
}

function build_and_publish_all_tags {
  IMAGE=$1
  IMAGE_VERSION=$2
  IMAGE_DIR=$3
  CONTAINER_PORT=$4
  BASE_IMAGE=$5

  IMAGE_TAG=$IMAGE:$IMAGE_VERSION
  IMAGE_TAG_LATEST=$IMAGE:latest

  if [ -z "$BASE_IMAGE" ]; then
    BASE_IMAGE_VERSION=""
    BASE_IMAGE_LATEST=""
  else
    echo "Using base image: $BASE_IMAGE"
    BASE_IMAGE_VERSION=$BASE_IMAGE:$IMAGE_VERSION
    BASE_IMAGE_LATEST=$BASE_IMAGE:latest
  fi

  echo "#####################################"
  echo "Building and publishing image $IMAGE"
  echo "#####################################"
  if [ "$PUBLISH" = "latest" ]
  then
    build_and_publish_single_image $IMAGE_DIR $IMAGE_TAG_LATEST $CONTAINER_PORT true $BASE_IMAGE_LATEST 
  elif [ "$PUBLISH" = "version" ]
  then
    build_and_publish_single_image $IMAGE_DIR $IMAGE_TAG $CONTAINER_PORT true $BASE_IMAGE_VERSION
  elif [ "$PUBLISH" = "all" ]
  then
    build_and_publish_single_image $IMAGE_DIR $IMAGE_TAG_LATEST $CONTAINER_PORT true $BASE_IMAGE_LATEST
    build_and_publish_single_image $IMAGE_DIR $IMAGE_TAG $((CONTAINER_PORT+1)) true $BASE_IMAGE_VERSION
  elif [ "$PUBLISH" = "none" ]
  then
    build_and_publish_single_image $IMAGE_DIR $IMAGE_TAG $((CONTAINER_PORT+1)) false $BASE_IMAGE_VERSION
    build_and_publish_single_image $IMAGE_DIR $IMAGE_TAG_LATEST $CONTAINER_PORT false $BASE_IMAGE_LATEST
  fi
}

# build minimal-notebook 
function build_minimal_notebook {
  declare -g MINIMAL_NOTEBOOK_TAG=$CONTAINER_REG_OWNER/minimal-notebook$IMAGE_SUFFIX 
  MINIMAL_NOTEBOOK_DIR=minimal-notebook
  build_and_publish_all_tags $MINIMAL_NOTEBOOK_TAG $VERSION $MINIMAL_NOTEBOOK_DIR 6000 "" 
}

# build datascience notebook
function build_datascience_notebook {
  declare -g DATASCIENCE_NOTEBOOK_TAG=$CONTAINER_REG_OWNER/datascience-notebook$IMAGE_SUFFIX 
  DATASCIENCE_NOTEBOOK_DIR=datascience-notebook
  build_and_publish_all_tags $DATASCIENCE_NOTEBOOK_TAG $VERSION $DATASCIENCE_NOTEBOOK_DIR 7000 $MINIMAL_NOTEBOOK_TAG 
}

# build notebook
function build_notebook {
  declare -g NOTEBOOK_TAG=$CONTAINER_REG_OWNER/notebook$IMAGE_SUFFIX 
  NOTEBOOK_DIR=notebook
  build_and_publish_all_tags $NOTEBOOK_TAG $VERSION $NOTEBOOK_DIR 8000 $DATASCIENCE_NOTEBOOK_TAG 

}

# build exam notebook
function build_exam_notebook {
  EXAM_NOTEBOOK_TAG=$CONTAINER_REG_OWNER/exam-notebook$IMAGE_SUFFIX 
  EXAM_NOTEBOOK_DIR=exam-notebook
  build_and_publish_all_tags $EXAM_NOTEBOOK_TAG $VERSION $EXAM_NOTEBOOK_DIR 8800 $NOTEBOOK_TAG 
}

function build_ngshare {
  NGSHARE_TAG=$CONTAINER_REG_OWNER/ngshare$IMAGE_SUFFIX 
  NGSHARE_DIR=ngshare
  build_and_publish_all_tags $NGSHARE_TAG $VERSION $NGSHARE_DIR 9000 "" 
}

function build_k8s_hub {
  # Build e2x k8s-hub
  cd hub
  HUB_PORT=9100
  for dir in */; do
    K8S_HUB_IMAGE_DIR=${dir%*/}
    K8S_VERSION=$K8S_HUB_IMAGE_DIR
    E2X_K8S_HUB_IMAGE_TAG=$CONTAINER_REG_OWNER/k8s-hub$IMAGE_SUFFIX:$K8S_VERSION
    build_and_publish_single_image $K8S_HUB_IMAGE_DIR $E2X_K8S_HUB_IMAGE_TAG $HUB_PORT true
    let "HUB_PORT+=1"
  done  
  cd .. 
}

# function to build all notebook related images
function build_all_notebook_images {
  build_minimal_notebook
  build_datascience_notebook
  build_notebook
  build_exam_notebook
}

function stop_docker_containers {
  # Get a list of running container IDs
  container_ids=$(docker ps -q)

  # Stop each container
  for container_id in $container_ids; do
    docker stop "$container_id"
  done
}

function main {
  echo "Building $IMAGE image"
  if [ "$IMAGE" = "all" ]; then 
    build_all_notebook_images
    build_k8s_hub
    build_ngshare
  else 
    if [ "$IMAGE" = "minimal-notebook" ]; then
      build_all_notebook_images
    elif [ "$IMAGE" = "datascience-notebook" ]; then
      build_datascience_notebook
      build_notebook
      build_exam_notebook
    elif [ "$IMAGE" = "notebook" ]; then
      build_notebook
      build_exam_notebook
    elif [ "$IMAGE" = "exam-notebook" ]; then
      build_exam_notebook
    elif [ "$IMAGE" = "hub" ]; then
      build_k8s_hub
    elif [ "$IMAGE" = "ngshare" ]; then
      build_ngshare
    else
      echo "Image $IMAGE is UNKNOWN, exiting..."
      exit 1
    fi 
  fi
}

# build and publish
main

# check docker images and containers
docker images
docker ps
stop_docker_containers
