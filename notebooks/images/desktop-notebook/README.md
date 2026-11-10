# e2x Desktop Notebook

This Docker image is a customized version of the [e2x Minimal Notebook](../minimal-notebook) image, with an XFCE desktop installed.   
It is based on the [Jupyter Remote Desktop Proxy](https://github.com/jupyterhub/jupyter-remote-desktop-proxy) package.

## Description

This image adds a Desktop to the Jupyter Notebook image. The following changes have been made:

* User directories are moved to `/usr/local/xfce-userdirs` to hide the userdirs in the tree section of the notebook

## Usage

See [Images](../../../README.md#images), [Pull and Run](../../../README.md#pull-and-run)
and [Building Locally](../../../README.md#building-locally) in the main README.