ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/datascience-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x machine learning notebook"

USER $NB_USER

# Install conda related pkgs
RUN mamba install -y xeus-sql --channel conda-forge && \
    mamba install -y soci-mysql --channel conda-forge && \
    mamba install -y soci-postgresql --channel conda-forge && \
    mamba install -y soci-sqlite --channel conda-forge && \
    mamba clean -afy && \
    npm cache clean --force && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Jupyter extension list
RUN jupyter nbextension list

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
