ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/datascience-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x machine learning notebook"

USER root

# Install libgl1-mesa-dev for opencv
RUN apt-get update -y \
    && apt-get install --yes \
       libgl1-mesa-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# Install pytorch cpu 
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Jupyter extension list
RUN jupyter nbextension list

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
