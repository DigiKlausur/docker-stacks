ARG IMAGE_SOURCE=jupyterhub/k8s-hub:1.2.0
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur (E2x) project HBRS <mohammad.wasil@h-brs.de>"

USER root
RUN pip install --no-cache-dir pandas && \
    pip install --no-cache-dir jupyterhub-nativeauthenticator==1.1.0 && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/miaauth.git@main

USER $NB_USER
