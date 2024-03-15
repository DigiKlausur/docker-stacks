ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/datascience-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"

ARG E2XGRADER=e2xgrader=="0.3.0-dev0"

USER root
# Copy nbgrader base config
COPY configs/nbgrader_config.py /etc/jupyter/nbgrader_config.py
RUN chown root:$NB_GID /etc/jupyter/nbgrader_config.py &&\
    chmod g+rwX /etc/jupyter/nbgrader_config.py

USER $NB_USER

# Install grading requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir $E2XGRADER

# Set up kernels
RUN touch /etc/ipython/ipython_config.py && \
    python -m exam_kernel.install --sys-prefix && \
    python -m java_syntax_kernel.install --sys-prefix

# Activate student mode by default
RUN e2xgrader activate student --sys-prefix

# Jupyter extension list
RUN jupyter nbextension list

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
