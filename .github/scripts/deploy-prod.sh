# Build and deploy prod environment

env | grep DOCKER
echo "$DOCKER_TOKEN" | docker login --username "$DOCKER_USERNAME" --password-stdin
VERSION=$(git rev-parse --short HEAD)

make -C minimal-notebook build
make -C minimal-notebook push
docker run -it --rm -d -p 8880:8888 digiklausur/minimal-notebook:$VERSION

make -C notebook build
make -C notebook push
docker run -it --rm -d -p 8881:8888 digiklausur/notebook:$VERSION

make -C restricted-notebook build
make -C restricted-notebook push
docker run -it --rm -d -p 8882:8888 digiklausur/restricted-notebook:$VERSION

make -C ngshare build
make -C ngshare push
docker run -it --rm -d -p 8883:8888 digiklausur/ngshare:$VERSION

make -C hub build
make -C hub push

docker ps
