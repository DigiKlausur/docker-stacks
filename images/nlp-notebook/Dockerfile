ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/ml-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x natural language processing notebook"

USER $NB_USER

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Jupyter extension list
RUN jupyter nbextension list

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
