# e2x Desktop Notebook

This Docker image is a customized version of the [e2x Minimal Notebook](../minimal-notebook) image, with an XFCE desktop installed.   
It is based on the [Jupyter Remote Desktop Proxy](https://github.com/jupyterhub/jupyter-remote-desktop-proxy) package.

## Build Args

The following build arg is available:

* `IMAGE_SOURCE`: The base image to use for the build. Defaults to `ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest`.

## Description

This image adds a Desktop to the Jupyter Notebook image. The following changes have been made:

* User directories are moved to `/usr/local/xfce-userdirs` to hide the userdirs in the tree section of the notebook

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/desktop-notebook:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build and Run

To build the image from the standard source, run:

`docker build -t desktop-notebook:dev .`

To build the image from a custom source, run:

`docker build -t desktop-notebook:dev . --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>"`

To run the image, use:

`docker run -p 8888:8888 desktop-notebook:dev`