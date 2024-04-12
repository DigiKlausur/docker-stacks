ARG IMAGE_SOURCE=jupyter/minimal-notebook:notebook-6.5.4
FROM $IMAGE_SOURCE
# Built from... https://hub.docker.com/r/jupyter/minimal-notebook/
#               https://github.com/jupyter/docker-stacks/blob/main/images/minimal-notebook/Dockerfile
# Built from... Ubuntu 22.04

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x minimal notebook"
LABEL org.opencontainers.image.description="e2x minimal notebook"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root

ENV TZ=Europe/Berlin

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Create default config for ipython kernel config
RUN mkdir /etc/ipython/ && \
    chown root:$NB_GID /etc/ipython/ &&\
    chmod g+rwX /etc/ipython/ &&\
    chmod +6000 /etc/ipython/

# Remove default work dir
RUN rm -rf $HOME/work

RUN apt-get update -y \
    && apt-get install --yes \
       pandoc \
       vim \
       libgl1-mesa-dev zip wkhtmltopdf \
       build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# Install conda related pkgs
RUN mamba install -y gh --channel conda-forge && \
    mamba install -y graphviz

RUN pip install --upgrade pip

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Enable extenstions and Jupyter contrib extensions
RUN cd /tmp && \
    git clone --depth 1 -b master https://github.com/ipython-contrib/jupyter_contrib_nbextensions.git && \
    cd /tmp/jupyter_contrib_nbextensions/src/jupyter_contrib_nbextensions/nbextensions && \
    jupyter nbextension install --sys-prefix execute_time && \
    jupyter nbextension enable --sys-prefix execute_time/ExecuteTime && \
    jupyter nbextension list && \
    rm -rf /tmp/jupyter_contrib_nbextensions

USER root

# clean up
RUN /opt/conda/bin/conda clean -afy && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyc' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

USER $NB_USER

# Jupyter extension list
RUN jupyter nbextension list