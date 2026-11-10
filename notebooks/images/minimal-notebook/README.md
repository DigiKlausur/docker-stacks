# e2x Minimal Notebook

This Docker image is a customized version of the official Jupyter Minimal Notebook image, based on Ubuntu 22.04.

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

See [Images](../../../README.md#images), [Pull and Run](../../../README.md#pull-and-run)
and [Building Locally](../../../README.md#building-locally) in the main README.