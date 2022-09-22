ARG IMAGE_SOURCE=jupyterhub/k8s-hub:1.1.1
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur (E2x) project HBRS <mohammad.wasil@h-brs.de>"

USER root
RUN pip install pandas

# install jupyterhub-nativeauthenticator
pip install jupyterhub-nativeauthenticator==1.1.0

USER $NB_USER
