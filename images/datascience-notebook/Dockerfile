ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x datascience notebook"

USER root

# Install requirements
# We need build-essential to compile some of the packages and then we remove it to keep the image small
# We install as root and then switch back to the $NB_USER to install the packages
COPY requirements.txt /tmp/requirements.txt
RUN apt-get update -y \
    && apt-get install --yes \
        build-essential \
    && su $NB_USER -c ". /opt/conda/bin/activate && pip install --no-cache-dir -r /tmp/requirements.txt" \
    && rm /tmp/requirements.txt \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete \
    && apt-get purge -y --auto-remove build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# Jupyter extension list
RUN jupyter nbextension list
