# e2x WuS Notebook

This Docker image is a customized version of the [e2x Data Science Notebook](../datascience-notebook) image, with certain extensions specific to the WuS course at H-BRS installed.

## Description

This image is designed for the WuS (statistics) course, building on top of the e2x Data Science Notebook image. It includes:

* All features from the e2x Data Science Notebook image
* The `highlight_selected_word` notebook extension, which highlights all occurrences of the selected word
* Its own [`nbgrader_config.py`](configs/nbgrader_config.py):
    + Feedback marks cells that still need manual grading with the comment "Unbewertet"
    + Multiple choice questions are all-or-nothing: full points only if all correct and no incorrect answers are selected

## Versions

This images comes as a basic WuS image or with `e2xgrader` installed and a specific mode activated.
For more information look at the [E2xGrader Notebook](../../e2xgrader) image and the [e2xgrader](https://github.com/Digiklausur/e2xgrader) package.

* `wus-notebook`
    + Base WuS image
* `wus-notebook-teacher`
    + Base WuS image with `e2xgrader` teacher mode activated (includes grading tools)
* `wus-notebook-student`
    + Base WuS image with `e2xgrader` student mode activated (includes extensions for students)
* `wus-notebook-exam`
    + Base WuS image with `e2xgrader` student_exam mode activated (provides a restricted notebook for students in an exam)

## Usage

### Pull and Run

To pull and run the image use:

`docker run -p 8888:8888 ghcr.io/digiklausur/docker-stacks/wus-notebook:latest`

Available tags are `latest` and `dev`. Available registries are `quay.io` and `ghcr.io`.

### Build

See [Building Locally](../../../README.md#building-locally).