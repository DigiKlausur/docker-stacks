FROM jupyter/minimal-notebook:016833b15ceb
# Built from... https://hub.docker.com/r/jupyter/minimal-notebook/
#               https://github.com/jupyter/docker-stacks/blob/master/minimal-notebook/Dockerfile
# Built from... Ubuntu 20.04 (focal)

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

USER root

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
    && apt-get install --yes \
      pandoc \
      texlive-xetex \
      texlive-fonts-recommended \
      texlive-latex-recommended \
      texlive-latex-extra \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN rm -rf $HOME/work

USER $NB_USER
