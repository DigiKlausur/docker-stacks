# e2x SQL Notebook

This Docker image is a customized version of the [e2x Data Science Notebook](../datascience-notebook) image, with additional SQL libraries installed.

## Description

This image is designed to provide a Jupyter Notebook environment for SQL tasks, building on top of the e2x Data Science Notebook image. It includes:

* All features from the e2x Data Science Notebook image
* Jupyter SQL kernels / magics, including xeus-sql and ipython-sql

## Versions

This images comes as a basic SQL image or with `e2xgrader` installed and a specific mode activated.
For more information look at the [E2xGrader Notebook](../../e2xgrader) image and the [e2xgrader](https://github.com/Digiklausur/e2xgrader) package.

* `sql-notebook`
    + Base SQL image
* `sql-notebook-teacher`
    + Base SQL image with `e2xgrader` teacher mode activated (includes grading tools)
* `sql-notebook-student`
    + Base SQL image with `e2xgrader` student mode activated (includes extensions for students)
* `sql-notebook-exam`
    + Base SQL image with `e2xgrader` student_exam mode activated (provides a restricted notebook for students in an exam)

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/sql-notebook:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build

See [Building Locally](../../../README.md#building-locally).