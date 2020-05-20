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

RUN python3.7 -m venv ${APP_DIR}/venv

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install --no-cache-dir jupyterhub==1.1.*

#Install nbgrader and H-BRS DigiKlausur nbextension
RUN pip install --no-cache-dir git+http://git@github.com/DigiKlausur/nbgrader.git@v0.7.0-dev-k8s
RUN jupyter serverextension enable --system --py nbgrader &&\
    jupyter nbextension install --system --py nbgrader --overwrite &&\
    jupyter nbextension enable --system assignment_list/main --section=tree &&\
    jupyter serverextension enable --system nbgrader.server_extensions.assignment_list

RUN cd /tmp && \
    git clone https://github.com/DigiKlausur/Jupyter-Extensions.git && \
    cd /tmp/Jupyter-Extensions/nbextensions/exam_extensions && \
    jupyter nbextension install --system restricted_tree &&\
    jupyter nbextension enable --system restricted_tree/main --section=tree &&\
    jupyter nbextension install --system exam_view &&\
    jupyter nbextension enable --system exam_view/main &&\
    rm -rf /tmp/*

ADD ipython_config.py ${IPYTHONDIR}/ipython_config.py

# remove unnecessary packages and cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

USER jovyan
RUN jupyter nbextension list

USER $NB_USER