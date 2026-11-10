# e2x Julia Notebook

This Docker image installs Julia with a Julia kernel.   
This image is experimental.

## Description

This image adds Julia to the Jupyter Notebook

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/julia-notebook:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build

See [Building Locally](../../../README.md#building-locally).