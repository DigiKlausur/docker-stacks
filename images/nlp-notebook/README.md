# e2x Natural Language Processing Notebook

This Docker image is a customized version of the [e2x Machine Learning Notebook](../ml-notebook) image, with additional Python natural language processing libraries installed.

## Build Args

The following build arg is available:

* `IMAGE_SOURCE`: The base image to use for the build. Defaults to `ghcr.io/digiklausur/docker-stacks/ml-notebook:latest`.

## Description

This image is designed to provide a comprehensive Jupyter Notebook environment for Natural Language Processing tasks (cpu only), building on top of the e2x Data Science Notebook image. It includes:

* All features from the e2x Machine Learning Notebook image
* A collection of popular Python Natural Language Processing libraries, including transformers, nltk, spacy, gensim, and more

## Versions

This images comes as a basic natural language processing image or with `e2xgrader` installed and a specific mode activated.
For more information look at the [E2xGrader Notebook](../e2xgrader-notebook) image and the [e2xgrader](https://github.com/Digiklausur/e2xgrader) package.

* `nlp-notebook`
    + Base natural language processing image
* `nlp-notebook-teacher`
    + Base natural language processing image with `e2xgrader` teacher mode activated (includes grading tools)
* `nlp-notebook-student`
    + Base natural language processing image with `e2xgrader` student mode activated (includes extensions for students)
* `nlp-notebook-exam`
    + Base natural language processing image with `e2xgrader` student_exam mode activated (provides a restricted notebook for students in an exam)

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/nlp-notebook:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build and Run

To build the image from the standard source, run:

`docker build -t nlp-notebook:dev .`

To build the image from a custom source, run:

`docker build -t nlp-notebook:dev . --build-arg="IMAGE_SOURCE=<your_base_image>:<your_tag>"`

To run the image, use:

`docker run -p 8888:8888 nlp-notebook:dev`