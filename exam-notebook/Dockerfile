FROM ghcr.io/digiklausur/docker-stacks/notebook-dev:latest

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

USER $NB_USER

# Activate student exam mode by default
RUN e2xgrader activate student_exam --sys-prefix

# activate e2x-help
RUN echo 'c = get_config()'  >> /etc/jupyter/e2xhelp_config.py
RUN echo 'c.Help.shared_path = "/srv/shares"' >> /etc/jupyter/e2xhelp_config.py

RUN jupyter serverextension enable e2xhelp --py --sys-prefix && \
    jupyter nbextension install e2xhelp --py --sys-prefix && \
    jupyter nbextension enable e2xhelp --py --sys-prefix

RUN jupyter nbextension list
