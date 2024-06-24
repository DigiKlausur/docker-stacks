# e2x Minimal Notebook

This Docker image is a customized version of the official Jupyter Minimal Notebook image, based on Ubuntu 22.04.

## Build Args

The following build arg is available:

* `IMAGE_SOURCE`: The base image to use for the build. Defaults to `jupyter/minimal-notebook:notebook-6.5.4`.

## Description

This image is designed to provide a minimal Jupyter Notebook environment with additional tools and configurations. It includes:

* Additional packages: `ncdu`, `vim`, `zip`
* Configured with a default timezone of `Europe/Berlin`
* Default locale set to `en_US.UTF-8`
* IPython kernel config directory created with default permissions
* Git and Graphviz installed
* `execute_time` from Jupyter contrib extensions installed
* `nbresuse` for displaying resource usage in a notebook (see `requirements.txt`)

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build and Run

To build the image from the standard source, run:

`docker build -t minimal-notebook:dev .`

To build the image from a custom source, run:

`docker build -t minimal-notebook:dev . --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>"`

To run the image, use:

`docker run -p 8888:8888 minimal-notebook:dev`