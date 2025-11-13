ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

ARG FROM_REPO=false
ARG E2XGRADER_VERSION=""
ARG E2XGRADER_BRANCH="main"
ARG E2XGRADER_MODE="student"

# Inherit from any image, then just install e2xgrader and activate a mode
LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL org.opencontainers.image.title="e2xgrader-notebook"
LABEL org.opencontainers.image.description="A Docker image for the e2xgrader notebook, designed to facilitate grading and managing assignments in Jupyter Notebooks, with support for different user modes including student, student_exam, and teacher."
LABEL org.opencontainers.image.vendor="H-BRS"
LABEL org.opencontainers.image.url="https://github.com/DigiKlausur/docker-stacks/"
LABEL org.opencontainers.image.source="https://github.com/DigiKlausur/docker-stacks/images/e2xgrader-notebook"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.mode="$E2XGRADER_MODE"

ENV JUPYTER_CONFIG_DIR=/opt/conda/etc/jupyter

USER root

# ------------------------------------ #
#   Base configuration for all modes   #
# ------------------------------------ #

# Copy nbgrader base config
COPY configs/base/nbgrader_config.py /etc/jupyter/nbgrader_config.py
RUN chown root:"$NB_GID" /etc/jupyter/nbgrader_config.py &&\
    chmod g+rwX /etc/jupyter/nbgrader_config.py

# Copy and append jupyter notebook config override
COPY configs/base/jupyter_notebook_config_override.py /tmp/jupyter_notebook_config_override.py
RUN cat /tmp/jupyter_notebook_config_override.py >> /etc/jupyter/jupyter_notebook_config.py && \
    rm /tmp/jupyter_notebook_config_override.py && \
    chown root:"$NB_GID" /etc/jupyter/jupyter_notebook_config.py && \
    chmod g+rwX /etc/jupyter/jupyter_notebook_config.py
    
USER $NB_USER

# Install requirements shared between all modes
RUN echo "Installing common requirements"
COPY common_requirements.txt /tmp/common_requirements.txt
RUN pip install --no-cache-dir -r /tmp/common_requirements.txt && \
    python -m java_syntax_kernel.install --sys-prefix

# Install mode specific requirements
RUN echo "Installing requirements for ${E2XGRADER_MODE}"
COPY ${E2XGRADER_MODE}_requirements.txt /tmp/mode_requirements.txt
RUN pip install --no-cache-dir -r /tmp/mode_requirements.txt

# ------------------------------------ #
#      Student Exam Configuration      #
# ------------------------------------ #

# Copy custom-preload.js if mode equals student_exam
COPY custom/custom-preload.js /tmp/custom-preload.js
# Copy jupyter_backup_config.py if mode equals student_exam
COPY configs/exam/jupyter_backup_config.py /tmp/jupyter_backup_config.py
RUN if [ "$E2XGRADER_MODE" = "student_exam" ]; then \
        echo "Copying custom-preload.js for student_exam mode"; \
        mkdir -p "$JUPYTER_CONFIG_DIR"/custom/; \
        cp /tmp/custom-preload.js "$JUPYTER_CONFIG_DIR"/custom/; \
        cp /tmp/jupyter_backup_config.py /etc/jupyter/jupyter_backup_config.py && \
        chown root:"$NB_GID" /etc/jupyter/jupyter_backup_config.py && \
        chmod g+rwX /etc/jupyter/jupyter_backup_config.py; \
    fi
    
# ------------------------------------ #
#        Teacher Configuration         #
# ------------------------------------ #
USER root
# If teacher mode is activated install wkhtmltopdf, needed for feedback PDFs
RUN if [ "$E2XGRADER_MODE" = "teacher" ]; then \
        echo "Installing wkhtmltopdf for teacher mode"; \
        apt-get update \ 
        && apt-get install -y wkhtmltopdf \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*; \
    fi

# Clean up temporary files
RUN rm -rf /tmp/*.txt /tmp/*.js /tmp/*.py

USER $NB_USER

RUN if [ "$E2XGRADER_MODE" = "teacher" ]; then \
    echo "Enabling the nbdime git extension for teacher mode"; \
    nbdime config-git --enable --global; \
    fi

# ------------------------------------ #
#          E2xGrader Install           #
# ------------------------------------ #
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
    fi && \
    e2xgrader activate "$E2XGRADER_MODE" --sys-prefix

