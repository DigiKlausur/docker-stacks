ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"

USER $NB_USER

# Activate student exam mode by default
RUN e2xgrader activate student_exam --sys-prefix

# Remove RISE
RUN pip uninstall RISE

# Jupyter extension list
RUN jupyter nbextension list
