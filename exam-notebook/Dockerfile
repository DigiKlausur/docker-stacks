ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

USER $NB_USER

# Activate student exam mode by default
RUN e2xgrader activate student_exam --sys-prefix

# Deactivate RISE
RUN jupyter-nbextension uninstall rise --py --sys-prefix

RUN jupyter nbextension list
