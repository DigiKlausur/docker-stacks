ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:dev
FROM $IMAGE_SOURCE

ARG CODE_VERSION=4.23.1

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x code notebook"
LABEL org.opencontainers.image.description="e2x code notebook"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root
ENV CODE_VERSION=$CODE_VERSION

RUN apt-get update -y \
    && apt-get install --yes \
       curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fOL https://github.com/coder/code-server/releases/download/v$CODE_VERSION/code-server_${CODE_VERSION}_amd64.deb \
    && dpkg -i code-server_${CODE_VERSION}_amd64.deb \
    && rm -f code-server_${CODE_VERSION}_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && find /usr/lib/code-server -type f -name '*.js.map' -delete \
    && npm cache clean --force



RUN mamba install -y jupyter-server-proxy -c conda-forge && \
    mamba install -y jupyter-vscode-proxy -c conda-forge && \
    mamba clean -afy && \
    npm cache clean --force && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

USER $NB_USER



