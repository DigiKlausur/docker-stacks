FROM jupyter/minimal-notebook:3b1f4f5e6cc1

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

USER root

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && \
    apt-get install --yes \
            pandoc \
            texlive-xetex \
            texlive-fonts-recommended \
            texlive-generic-recommended \
            texlive-generic-extra

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

#Install nbgrader and H-BRS DigiKlausur nbextension
RUN pip install -I git+http://git@github.com/DigiKlausur/nbgrader.git@v0.7.0-dev-k8s
RUN jupyter serverextension enable --sys-prefix --py nbgrader &&\
    jupyter nbextension install --sys-prefix --py nbgrader --overwrite &&\
    jupyter nbextension enable --sys-prefix assignment_list/main --section=tree &&\
    jupyter serverextension enable --sys-prefix nbgrader.server_extensions.assignment_list

RUN cd /tmp && \
    git clone https://github.com/DigiKlausur/Jupyter-Extensions.git && \
    cd /tmp/Jupyter-Extensions/nbextensions && \
    jupyter nbextension install assignment_view --sys-prefix && \
    jupyter nbextension enable assignment_view/main --sys-prefix

RUN jupyter nbextension list

USER $NB_USER
