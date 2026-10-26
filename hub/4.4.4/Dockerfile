ARG IMAGE_SOURCE=jupyterhub/k8s-hub:4.4.4

FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur (E2x) project HBRS <e2x@h-brs.de>"
LABEL org.opencontainers.image.description="JupyterHub k8s 4.4.4 image for E2x project"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

ARG NB_USER=jovyan \
    NB_UID=1000 \
    HOME=/home/jovyan

USER root

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

USER ${NB_USER}
