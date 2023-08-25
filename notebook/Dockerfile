ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/datascience-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"

USER $NB_USER

# Install grading requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xgrader.git@dev

# Set up kernels
RUN touch /etc/ipython/ipython_config.py && \
    python -m exam_kernel.install --sys-prefix && \
    python -m java_syntax_kernel.install --sys-prefix

# Activate student mode by default
RUN e2xgrader activate student --sys-prefix

# Copy nbgrader base config
COPY configs/nbgrader_config.py /etc/jupyter/nbgrader_config.py

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
