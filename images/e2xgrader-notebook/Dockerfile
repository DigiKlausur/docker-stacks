ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest

# ------------------------------------ #
#   Base configuration for all modes   #
# ------------------------------------ #
FROM $IMAGE_SOURCE AS base
ARG IMAGE_SOURCE
ARG FROM_REPO=false
ARG E2XGRADER_VERSION=""
ARG E2XGRADER_BRANCH="main"

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL org.opencontainers.image.title="e2xgrader-notebook"
LABEL org.opencontainers.image.description="The base image for the e2xgrader notebook, with common configurations and e2xgrader installation, designed to be extended for different user modes including student, student_exam, and teacher."
LABEL org.opencontainers.image.vendor="H-BRS"
LABEL org.opencontainers.image.url="https://github.com/DigiKlausur/docker-stacks/"
LABEL org.opencontainers.image.source="https://github.com/DigiKlausur/docker-stacks/images/e2xgrader-notebook"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.base.image="$IMAGE_SOURCE"

ENV JUPYTER_CONFIG_DIR=/opt/conda/etc/jupyter

USER root

# Copy nbgrader base config
COPY base/nbgrader_config.py /etc/jupyter/nbgrader_config.py
RUN chown root:"$NB_GID" /etc/jupyter/nbgrader_config.py &&\
    chmod g+rwX /etc/jupyter/nbgrader_config.py

# Copy and append jupyter notebook config override
COPY base/jupyter_notebook_config_override.py /tmp/jupyter_notebook_config_override.py
RUN cat /tmp/jupyter_notebook_config_override.py >> /etc/jupyter/jupyter_notebook_config.py && \
    rm /tmp/jupyter_notebook_config_override.py && \
    chown root:"$NB_GID" /etc/jupyter/jupyter_notebook_config.py && \
    chmod g+rwX /etc/jupyter/jupyter_notebook_config.py
    
USER $NB_USER

# Install requirements shared between all modes
RUN echo "Installing base requirements"
COPY requirements/base.txt /tmp/base_requirements.txt
RUN pip install --no-cache-dir -r /tmp/base_requirements.txt && \
    python -m java_syntax_kernel.install --sys-prefix

# Install e2xgrader
RUN if [ "$FROM_REPO" = "false" ] && [ -z "$E2XGRADER_VERSION" ]; then \
        echo "Installing e2xgrader from default source..."; \
        pip install --no-cache-dir e2xgrader; \
    elif [ "$FROM_REPO" = "false" ] && [ -n "$E2XGRADER_VERSION" ]; then \
        echo "Installing e2xgrader version: $E2XGRADER_VERSION from PyPI..."; \
        pip install --no-cache-dir e2xgrader=="$E2XGRADER_VERSION"; \
    elif [ "$FROM_REPO" = "true" ]; then \
        echo "Installing e2xgrader from GitHub repository: https://github.com/DigiKlausur/e2xgrader.git@$E2XGRADER_BRANCH"; \
        pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xgrader.git@"${E2XGRADER_BRANCH}"; \
    fi

USER root
RUN rm -rf /tmp/base_requirements.txt

USER $NB_USER

# ------------------------------------ #
#        Student configuration         #
# ------------------------------------ #
FROM base AS student

LABEL org.opencontainers.image.title ="e2xgrader-notebook:student"
LABEL org.opencontainers.image.description="The student mode of the e2xgrader notebook image, configured with specific settings and requirements for students. e2xgrader is activated in student mode."
LABEL org.opencontainers.image.mode="student"
ENV E2XGRADER_MODE=student

# Install requirements specific to student mode
RUN echo "Installing requirements for student mode"
COPY requirements/student.txt /tmp/student_requirements.txt
RUN pip install --no-cache-dir -r /tmp/student_requirements.txt

RUN e2xgrader activate student --sys-prefix

USER root
RUN rm -rf /tmp/student_requirements.txt

USER $NB_USER

# ------------------------------------ #
#      Student Exam configuration      #
# ------------------------------------ #
FROM base AS student_exam

LABEL org.opencontainers.image.title="e2xgrader-notebook:student_exam"
LABEL org.opencontainers.image.description="The student exam mode of the e2xgrader notebook image, configured with specific settings and requirements for students in exam mode. e2xgrader is activated in student_exam mode. This mode includes additional configurations for automatic backup of notebooks and custom JavaScript injection to enhance the exam experience."
LABEL org.opencontainers.image.mode="student_exam"
ENV E2XGRADER_MODE=student_exam

# Install requirements specific to student_exam mode
RUN echo "Installing requirements for student_exam mode"
COPY requirements/student_exam.txt /tmp/student_exam_requirements.txt
RUN pip install --no-cache-dir -r /tmp/student_exam_requirements.txt


# Copy jupyter_backup_config.py to configure automatic backup of notebooks for student_exam mode
COPY student_exam/jupyter_backup_config.py /etc/jupyter/jupyter_backup_config.py
USER root
RUN echo "Copying jupyter_backup_config.py for student_exam mode as root" && \
    chown root:"$NB_GID" /etc/jupyter/jupyter_backup_config.py && \
    chmod g+rwX /etc/jupyter/jupyter_backup_config.py
 
USER $NB_USER
# Copy custom-preload.js to inject custom JavaScript into the notebook interface for student_exam mode
COPY student_exam/custom-preload.js /tmp/custom-preload.js

RUN echo "Copying custom-preload.js for student_exam mode" && \
    mkdir -p "$JUPYTER_CONFIG_DIR"/custom/ && \
    cp /tmp/custom-preload.js "$JUPYTER_CONFIG_DIR"/custom/
    
RUN e2xgrader activate student_exam --sys-prefix

USER root
RUN rm -rf /tmp/student_exam_requirements.txt && \
    rm /tmp/custom-preload.js

USER $NB_USER

# ------------------------------------ #
#        Teacher configuration         #
# ------------------------------------ #
FROM base AS teacher

LABEL org.opencontainers.image.title ="e2xgrader-notebook:teacher"
LABEL org.opencontainers.image.description="The teacher mode of the e2xgrader notebook image, configured with specific settings and requirements for teachers. Tools to grade, author, and manage assignments are available in this mode. e2xgrader is activated in teacher mode. This mode includes additional tools for grading and assignment management, as well as the installation of wkhtmltopdf for generating feedback PDFs."
LABEL org.opencontainers.image.mode="teacher"

ENV E2XGRADER_MODE=teacher

USER root

# Install wkhtmltopdf, needed for feedback PDFs
RUN echo "Installing wkhtmltopdf for teacher mode" && \
    apt-get update && \ 
    apt-get install -y wkhtmltopdf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*    

USER $NB_USER

# Install requirements specific to teacher mode and enable nbdime git extension
RUN echo "Installing requirements for teacher mode"
COPY requirements/teacher.txt /tmp/teacher_requirements.txt
RUN pip install --no-cache-dir -r /tmp/teacher_requirements.txt && \
    nbdime config-git --enable --global

RUN e2xgrader activate teacher --sys-prefix

USER root
RUN rm -rf /tmp/teacher_requirements.txt

USER $NB_USER