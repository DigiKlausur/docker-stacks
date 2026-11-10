# e2x WuS Notebook

This Docker image is a customized version of the [e2x Data Science Notebook](../datascience-notebook) image, with certain extensions specific to the WuS course at H-BRS installed.

## Description

This image is designed for the WuS (statistics) course, building on top of the e2x Data Science Notebook image. It includes:

* All features from the e2x Data Science Notebook image
* The `highlight_selected_word` notebook extension, which highlights all occurrences of the selected word
* Its own [`nbgrader_config.py`](configs/nbgrader_config.py):
    + Feedback marks cells that still need manual grading with the comment "Unbewertet"
    + Multiple choice questions are all-or-nothing: full points only if all correct and no incorrect answers are selected

## Usage

See [Images](../../../README.md#images), [Pull and Run](../../../README.md#pull-and-run)
and [Building Locally](../../../README.md#building-locally) in the main README.