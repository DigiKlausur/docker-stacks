ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur project HBRS <e2x@inf.h-brs.de>"

USER root
RUN apt-get install -y build-essential

USER $NB_USER

# Install requirements

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
USER root
RUN rm /tmp/requirements.txt

USER $NB_USER

# Install pytorch
RUN pip install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install graphviz via conda
RUN conda install graphviz