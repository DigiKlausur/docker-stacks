FROM ubuntu:18.04

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

ENV APP_DIR /srv/app
ENV PATH ${APP_DIR}/venv/bin:$PATH

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && \
    apt-get install --yes \
            python3.7 \
            python3.7-venv \
            python3.7-dev \
            build-essential \
            tar \
            git \
            wget \
            npm \
            nodejs \
            locales \
            vim \
            # for nbconvert
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

# Container storage
ENV IPYTHONDIR ${APP_DIR}/venv/etc/ipython

RUN adduser --disabled-password --gecos "Default Jupyter user" jovyan

RUN install -d -o jovyan -g jovyan ${APP_DIR}

WORKDIR /home/jovyan

RUN apt-get install --yes python3-venv

USER jovyan
RUN python3.7 -m venv ${APP_DIR}/venv

RUN export PIP_DEFAULT_TIMEOUT=100

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install --no-cache-dir jupyterhub==1.0.*

# nbresuse to show users memory usage
RUN pip install nbresuse==0.3.3

# interact notebook extension
RUN pip install nbgitpuller==0.8.0

# Install nbzip
RUN pip install nbzip==0.1.0 && \
    jupyter serverextension enable  --sys-prefix --py nbzip && \
    jupyter nbextension     install --sys-prefix --py nbzip && \
    jupyter nbextension     enable  --sys-prefix --py nbzip

ADD ipython_config.py ${IPYTHONDIR}/ipython_config.py

#Install nbgrader and H-BRS DigiKlausur nbextension
RUN pip install -I git+http://git@github.com/DigiKlausur/nbgrader.git@v0.7.0-dev-k8s
RUN jupyter serverextension enable --sys-prefix --py nbgrader &&\
    jupyter nbextension install --sys-prefix --py nbgrader --overwrite &&\
    jupyter nbextension enable --sys-prefix assignment_list/main --section=tree &&\
    jupyter serverextension enable --sys-prefix nbgrader.server_extensions.assignment_list

RUN cd /tmp && \
    git clone https://github.com/DigiKlausur/Jupyter-Extensions.git && \
    cd /tmp/Jupyter-Extensions/nbextensions/exam_extensions && \
    jupyter nbextension install restricted_tree --sys-prefix &&\
    jupyter nbextension enable restricted_tree/main --section=tree &&\
    jupyter nbextension install exam_view --sys-prefix &&\
    jupyter nbextension enable exam_view/main    

RUN jupyter nbextension list

EXPOSE 8888
