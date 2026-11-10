# e2x Code Notebook

This Docker image installs a VS code server.   
This image is experimental.

## Description

This image adds a VS code server to the Jupyter Notebook

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/datascience-notebook-code:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build

See [Building Locally](../../../README.md#building-locally).