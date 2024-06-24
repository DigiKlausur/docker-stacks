# e2x DB Main Notebook

This Docker image is a customized version of the [e2x Desktop Notebook](../desktop-notebook) image, with the DB Main application installed.
It serves as an example on how to install applications on the desktop notebook.

## Build Args

The following build arg is available:

* `IMAGE_SOURCE`: The base image to use for the build. Defaults to `ghcr.io/digiklausur/docker-stacks/desktop-notebook:latest`.

## Description

This image is designed to serve as an example of a desktop notebook with an application installed.   
It includes:

* All features from the e2x Desktop Notebook image
* The DB Main application installed
* A desktop entry for DB Main
* A menu entry for DB Main
* Autostarting DB Main when the desktop is opened

## Versions

This images comes as a basic DB Main image or with `e2xgrader` installed and a specific mode activated.
For more information look at the [E2xGrader Notebook](../e2xgrader-notebook) image and the [e2xgrader](https://github.com/Digiklausur/e2xgrader) package.

* `dbmain-notebook`
    + Base DB Main image
* `dbmain-notebook-teacher`
    + Base DB Main image with `e2xgrader` teacher mode activated (includes grading tools)
* `dbmain-notebook-student`
    + Base DB Main image with `e2xgrader` student mode activated (includes extensions for students)
* `dbmain-notebook-exam`
    + Base DB Main image with `e2xgrader` student_exam mode activated (provides a restricted notebook for students in an exam)

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/dbmain-notebook:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build and Run

To build the image from the standard source, run:

`docker build -t dbmain-notebook:dev .`

To build the image from a custom source, run:

`docker build -t dbmain-notebook:dev . --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>"`

To run the image, use:

`docker run -p 8888:8888 dbmain-notebook:dev`