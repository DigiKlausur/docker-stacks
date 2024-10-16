ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

ARG FROM_REPO=false
ARG E2XGRADER_VERSION=""
ARG E2XGRADER_BRANCH="main"
ARG E2XGRADER_MODE="student"

# Inherit from any image, then just install e2xgrader and activate a mode
LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root
# Copy nbgrader base config
COPY configs/nbgrader_config.py /etc/jupyter/nbgrader_config.py
RUN chown root:"$NB_GID" /etc/jupyter/nbgrader_config.py &&\
    chmod g+rwX /etc/jupyter/nbgrader_config.py
    
USER $NB_USER

# Install requirements shared between all modes
RUN echo "Installing common requirements"
COPY common_requirements.txt /tmp/common_requirements.txt
RUN pip install --no-cache-dir -r /tmp/common_requirements.txt

RUN python -m java_syntax_kernel.install --sys-prefix

# Install mode specific requirements
RUN echo "Installing requirements for ${E2XGRADER_MODE}"
COPY ${E2XGRADER_MODE}_requirements.txt /tmp/mode_requirements.txt
RUN pip install --no-cache-dir -r /tmp/mode_requirements.txt


    
USER root
# If teacher mode is activated install wkhtmltopdf, needed for feedback PDFs
RUN if [ "$E2XGRADER_MODE" = "teacher" ]; then \
        echo "Installing wkhtmltopdf for teacher mode"; \
        apt-get update \ 
        && apt-get install -y wkhtmltopdf \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*; \
    fi

RUN rm /tmp/common_requirements.txt /tmp/mode_requirements.txt

USER $NB_USER

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

# Activate a mode
RUN e2xgrader activate "$E2XGRADER_MODE" --sys-prefix

