ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/datascience-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x tensorflow machine learning notebook"
LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL org.opencontainers.image.title="tf-notebook"
LABEL org.opencontainers.image.description="A Docker image for the for Jupyter notebook based on datascience notebook with tensorflow installed."
LABEL org.opencontainers.image.vendor="H-BRS"
LABEL org.opencontainers.image.url="https://github.com/DigiKlausur/docker-stacks/"
LABEL org.opencontainers.image.source="https://github.com/DigiKlausur/docker-stacks/images/tf-notebook"
LABEL org.opencontainers.image.licenses="MIT"

USER root

# Install requirements and list extensions
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete \
    && jupyter nbextension list

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
