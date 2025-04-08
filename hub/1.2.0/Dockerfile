ARG IMAGE_SOURCE=jupyterhub/k8s-hub:1.2.0
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur (E2x) project HBRS <mohammad.wasil@h-brs.de>"
LABEL org.opencontainers.image.description="JupyterHub k8s 1.2.0 image for E2x project"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

ARG NB_USER=jovyan \
    NB_UID=1000 \
    HOME=/home/jovyan

USER root
RUN pip install --no-cache-dir pandas && \
    pip install --no-cache-dir jupyterhub-nativeauthenticator==1.1.0 && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/miaauth.git@main

USER ${NB_USER}
