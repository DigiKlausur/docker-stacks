ARG IMAGE_SOURCE=jupyterhub/k8s-hub:2.0.0
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur (E2x) project HBRS <mohammad.wasil@h-brs.de>"

ARG NB_USER=jovyan \
    NB_UID=1000 \
    HOME=/home/jovyan

USER root
RUN pip install --no-cache-dir pandas && \
    pip install --no-cache-dir jupyterhub-nativeauthenticator==1.1.0 && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/miaauth.git@main && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xhub.git@main

USER ${NB_USER}
