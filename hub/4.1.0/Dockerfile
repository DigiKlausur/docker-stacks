ARG IMAGE_SOURCE=jupyterhub/k8s-hub:4.1.0
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur (E2x) project HBRS <e2x@h-brs.de>"

ARG NB_USER=jovyan \
    NB_UID=1000 \
    HOME=/home/jovyan

USER root
RUN pip install --no-cache-dir pandas && \
    pip install --no-cache-dir jupyterhub-nativeauthenticator==1.3.0 && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/miaauth.git@main && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xhub.git@main && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2x-exam-hub.git@v0.1.0-dev1

USER ${NB_USER}