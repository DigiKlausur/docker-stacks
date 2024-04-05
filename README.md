[![K8s Hub](https://github.com/DigiKlausur/docker-stacks/actions/workflows/hub.yml/badge.svg)](https://github.com/DigiKlausur/docker-stacks/actions/workflows/hub.yml)

[![Notebook Stable](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_main.yml/badge.svg)](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_main.yml)
[![Notebook Dev](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_dev.yml/badge.svg)](https://github.com/DigiKlausur/docker-stacks/actions/workflows/docker_dev.yml)

# E2x Docker Stacks

## Branches
The `dev` branch will always reflect `ghcr.io/digiklausur/docker-stacks/{image_name}-dev:tag` on the GitHub container registry, and the `master` branch reflects `ghcr.io/digiklausur/docker-stacks/{image_name}:tag`. The default image tag is `latest`, and images using the commit hash are also built but not necessarily pushed to avoid fine-grained image tags on the registry. Additionally, the image used in a particular semester and release version can be pulled using tag i.e. `ws20` for winter semester 2020.

## Single user image
* `minimal-notebook`
  - Based on [jupyter/minimal-notebook](https://github.com/jupyter/docker-stacks/blob/master/minimal-notebook/Dockerfile)
* `datascience-notebook`
  - Built on top of `minimal-notebook`
  - Includes machine learning libraries like TensorFlow, PyTorch, scikit-learn, etc.
* `notebook`
  - Built on top of `datascience-notebook`
  - Includes e2xgrader and its dependencies for teaching purposes
* `exam-notebook`
  - Built on top of `notebook`
  - Includes exam extensions such as restricted tree, no delete button, etc.

To learn more about our teaching, authoring, grading, and examination packages, please visit our [e2xgrader repository](https://github.com/DigiKlausur/e2xgrader). 

## Build the image locally
You can build our images locally by using the following script
```
bash ci/build-and-deploy.sh --deployment "" --registry ghcr.io --image all --publish none
```
If you want to build the individual image, you can replace argument `--image` with the name of the image e.g. `minimal-notebook`, `datascience-notebook`, `notebook`, and `exam-notebook`


## Run the image locally
```
docker run -it --name notebook --rm -p 8888:8888 ghcr.io/digiklausur/docker-stacks/notebook:latest 
``` 
* Attach host host directory to the container
  ```
  docker run -it --name notebook -v /home/myhome:/home/jovyan/myhome --rm -p 8888:8888 ghcr.io/digiklausur/docker-stacks/notebook:latest

  ```
* Run the container in the background
  ```
  docker run -it --name notebook -v /home/myhome:/home/jovyan/myhome --rm -d -p 8888:8888 ghcr.io/digiklausur/docker-stacks/notebook:latest
  ```

* Open browser and go to localhost:8888
* Enter the notebook token if asked
  
  If you run docker in the background, you can get the log and the notebook token by

  ```
  docker logs --follow notebook
  ```

For more detailed information on how to run the image in your local pc, as well as to mount you local disks to the container, please visit [this page](https://e2x.inf.h-brs.de/usage/student.html#working-on-the-assignments-locally).
