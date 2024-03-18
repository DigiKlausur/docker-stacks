ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root
# Copy nbgrader base config
COPY configs/nbgrader_config.py /etc/jupyter/nbgrader_config.py
RUN chown root:$NB_GID /etc/jupyter/nbgrader_config.py &&\
    chmod g+rwX /etc/jupyter/nbgrader_config.py

USER $NB_USER

# Install grading requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir e2xgrader=="0.3.0-dev2"

# Set up kernels
RUN touch /etc/ipython/ipython_config.py && \
    python -m exam_kernel.install --sys-prefix && \
    python -m java_syntax_kernel.install --sys-prefix

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER

# Activate student exam mode by default
RUN e2xgrader activate student_exam --sys-prefix

# Remove RISE
RUN pip uninstall -y RISE

# Jupyter extension list
RUN jupyter nbextension list
