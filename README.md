[![Build Status](https://api.travis-ci.org/DigiKlausur/docker-stacks.svg?branch=master)](https://travis-ci.org/DigiKlausur/docker-stacks)

## Single user images
The minimal single user image `minimal-notebook` is based on [jupyter/minimal-notebook](https://github.com/jupyter/docker-stacks/blob/master/minimal-notebook/Dockerfile).
* `notebook` image is used for teaching environment
* `restricted-notebook` is used for examination environment

## Run the images locally
```
docker run -it --rm -p 8888:8888 digiklausur/notebook:latest
``` 

