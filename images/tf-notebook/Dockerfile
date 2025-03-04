ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/datascience-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x tensorflow machine learning notebook"

USER root

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Jupyter extension list
RUN jupyter nbextension list

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
