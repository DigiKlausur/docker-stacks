# e2x Data Science Notebook

TThis Docker image is a customized version of the [e2x Data Science Notebook](../datascience-notebook) image, with certain extensions specific to the WuS course at H-BRS installed.

## Build Args

The following build arg is available:

* `IMAGE_SOURCE`: The base image to use for the build. Defaults to `ghcr.io/digiklausur/docker-stacks/datascience-notebook:latest`.

## Description

This image is designed to provide a comprehensive Jupyter Notebook environment for data science tasks, building on top of the e2x Minimal Notebook image. It includes:

* All features from the e2x Minimal Notebook image
* A collection of popular Python data science libraries, including NumPy, Pandas, SciPy, Matplotlib, Scikit-learn, and more

## Versions

This images comes as a basic data science image or with `e2xgrader` installed and a specific mode activated.
For more information look at the [E2xGrader Notebook](../e2xgrader-notebook) image and the [e2xgrader](https://github.com/Digiklausur/e2xgrader) package.

* `wus-notebook`
    + Base WuS science image
* `wus-notebook-teacher`
    + Base data science image with `e2xgrader` teacher mode activated (includes grading tools)
* `wus-notebook-student`
    + Base data science image with `e2xgrader` student mode activated (includes extensions for students)
* `wus-notebook-exam`
    + Base data science image with `e2xgrader` student_exam mode activated (provides a restricted notebook for students in an exam)

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/wus-notebook:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build and Run

To build the image from the standard source, run:

`docker build -t wus-notebook:dev .`

To build the image from a custom source, run:

`docker build -t wus-notebook:dev . --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>"`

To run the image, use:

`docker run -p 8888:8888 wus-notebook:dev`