ARG IMAGE_SOURCE=jupyterhub/k8s-hub:1.1.1
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur (E2x) project HBRS <mohammad.wasil@h-brs.de>"

USER root
RUN pip install pandas

USER $NB_USER
