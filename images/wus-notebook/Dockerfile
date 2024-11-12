ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x notebook for statistics course"
LABEL org.opencontainers.image.description="e2x notebook for statistics course"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root
# Copy nbgrader wus config
COPY configs/nbgrader_config.py /opt/conda/etc/jupyter/nbgrader_config.py
RUN chown root:"$NB_GID" /opt/conda/etc/jupyter/nbgrader_config.py &&\
    chmod g+rwX /opt/conda/etc/jupyter/nbgrader_config.py

USER $NB_USER

# Disable execute time extension and enable highlight word
RUN jupyter nbextension disable --sys-prefix execute_time/ExecuteTime \
    && pip install --no-cache-dir jupyter_highlight_selected_word \
    && jupyter nbextension install --py --sys-prefix jupyter_highlight_selected_word \
    && jupyter nbextension enable --sys-prefix highlight_selected_word/main \
    && jupyter nbextension list
