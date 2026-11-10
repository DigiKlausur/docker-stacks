ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x business data notebook"
LABEL org.opencontainers.image.description="e2x business data notebook"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"


USER $NB_USER

COPY requirements.txt /tmp/requirements.txt

# Create a new conda environment for bi and install the requirements there
RUN mamba create -n bi "python=3.12" pip -y \
    && /opt/conda/envs/bi/bin/python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && mamba clean -afy \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Go to /opt/conda/share/kernels/python3 and replace the path to the python executable with the one from the bi environment in kernel.json
RUN sed -i 's|/opt/conda/bin/python|/opt/conda/envs/bi/bin/python|g' /opt/conda/share/jupyter/kernels/python3/kernel.json