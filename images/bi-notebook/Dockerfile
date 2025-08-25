ARG IMAGE_SOURCE=jupyter/minimal-notebook:notebook-6.5.3
FROM $IMAGE_SOURCE

# USe 6.5.3 minimal-notebook as base image for Python 3.10 needed by vaex

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x business intelligence notebook"
LABEL org.opencontainers.image.description="e2x business intelligence notebook"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root

ENV TZ=Europe/Berlin

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

# Set timezone and create default config for ipython kernel config
RUN ln -snf /usr/share/zoneinfo/"$TZ" /etc/localtime && echo "$TZ" > /etc/timezone \
    && mkdir /etc/ipython/ \
    && chown root:"$NB_GID" /etc/ipython/ \
    && chmod g+rwX /etc/ipython/ \
    && chmod +6000 /etc/ipython/ \
    && rm -rf "$HOME"/work \ 
    && apt-get update -y \
    && apt-get install --yes \
       ncdu \
       vim \
       zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# Install requirements and enable extenstions and Jupyter contrib extensions
COPY requirements.txt /tmp/requirements.txt

# Install git and graphviz and upgrade pip
RUN mamba install -y gh --channel conda-forge \
    && mamba install -y graphviz --no-update-deps \
    && mamba install -y vaex \
    && mamba clean -afy \
    && npm cache clean --force \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip uninstall "jupyter-server-terminals" -y \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete 
