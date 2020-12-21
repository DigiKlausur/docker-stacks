[<!--lint ignore no-dead-urls-->![Build Status](https://github.com/digiklausur/docker-stacks/workflows/CI%20to%20DockerHub/badge.svg)](https://github.com/digiklausur/docker-stacks/actions?workflow=CI+to+DockerHub)

# E2x Docker Stacks

## Branches
The `dev` branch will always reflect `digiklausur/{image_name}-dev:tag` on the docker hub, and the `master` branch reflects `digiklausur/{image_name}:tag`. The tag is based on the `commit id`, and tag `latest` is always built based on the latest commit. 

## Single user images
The minimal single user image `minimal-notebook` is based on [jupyter/minimal-notebook](https://github.com/jupyter/docker-stacks/blob/master/minimal-notebook/Dockerfile).
* `notebook` image is used for teaching environment
* `restricted-notebook` is used for examination environment

## Run the image locally
```
docker run -it --name notebook --rm -p 8888:8888 digiklausur/notebook:latest
``` 
* Attach host host directory to the container
  ```
  docker run -it --name notebook -v /home/myhome:/home/jovyan/myhome --rm -p 8888:8888 digiklausur/notebook:latest

  ```
* Run the container in the background
  ```
  docker run -it --name notebook -v /home/myhome:/home/jovyan/myhome --rm -d -p 8888:8888 digiklausur/notebook:latest
  ```

* Open browser and go to localhost:8888
* Enter the notebook token if asked
  
  If you run docker in the background, you can get the log and the notebook token by

  ```
  docker logs --follow notebook
  ```
