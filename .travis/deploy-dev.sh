# Deploy Dev environment

env | grep DOCKER
echo "$DOCKER_TOKEN" | docker login --username "$DOCKER_USERNAME" --password-stdin
VERSION=$(git rev-parse --short HEAD)

make -C ../minimal-notebook build
docker run -it --rm -d -p 8880:8888 digiklausur/minimal-notebook:latest

make -C notebook build_dev
make push -C notebook push_dev
docker run -it --rm -d -p 8881:8888 digiklausur/notebook-dev:$VERSION

make -C restricted-notebook build_dev
make push -C restricted-notebook push_dev
docker run -it --rm -d -p 8882:8888 digiklausur/restricted-notebook-dev:$VERSION

make -C ../ngshare build_dev
make -C ../ngshare push_dev
docker run -it --rm -d -p 8883:8888 digiklausur/ngshare:$VERSION

make -C ../hub build_dev
make -C ../hub push_dev

docker ps
docker images
