# e2x Julia Notebook

This Docker image installs Julia with a Julia kernel.   
This image is experimental.

## Build Args

The following build arg is available:

* `IMAGE_SOURCE`: The base image to use for the build. Defaults to `ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest`.

## Description

This image adds Julia to the Jupyter Notebook

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/julia-notebook:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build and Run

To build the image from the standard source, run:

`docker build -t julia-notebook:dev .`

To build the image from a custom source, run:

`docker build -t julia-notebook:dev . --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>"`

To run the image, use:

`docker run -p 8888:8888 julia-notebook:dev`