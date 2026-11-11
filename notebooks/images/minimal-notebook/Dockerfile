# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE
# Built from... https://hub.docker.com/r/jupyter/minimal-notebook/
#               https://github.com/jupyter/docker-stacks/blob/main/images/minimal-notebook/Dockerfile
# Built from... Ubuntu 22.04

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x minimal notebook"
LABEL org.opencontainers.image.description="e2x minimal notebook"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root

ENV TZ=Europe/Berlin

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

# Set timezone and create default config for ipython kernel config
RUN ln -snf /usr/share/zoneinfo/"$TZ" /etc/localtime && echo "$TZ" > /etc/timezone \
    && mkdir /etc/ipython/ \
    && chown root:"$NB_GID" /etc/ipython/ \
    && chmod g+rwX /etc/ipython/ \
    && chmod +6000 /etc/ipython/ \
    && rm -rf "$HOME"/work \ 
    && apt-get update -y \
    && apt-get install --yes \
       ncdu \
       vim \
       zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# uv installs Python packages for this image and all its children. Pinned on
# purpose; bump by hand. UV_PYTHON points uv at the conda env (uv refuses
# non-virtual environments otherwise), UV_NO_CACHE keeps the layers small.
# UV_CONSTRAINT protects pins (e.g. jupyter-server<2) from later installs in
# child images; see uv-constraints.txt.
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /usr/local/bin/uv
COPY uv-constraints.txt /etc/uv/constraints.txt
ENV UV_PYTHON=/opt/conda/bin/python \
    UV_NO_CACHE=1 \
    UV_CONSTRAINT=/etc/uv/constraints.txt

# Install requirements
COPY requirements.txt /tmp/requirements.txt

# Install git and graphviz, upgrade pip (still used interactively) and install requirements
RUN mamba install -y gh --channel conda-forge \
    && mamba install -y graphviz --no-update-deps \
    && mamba clean -afy \
    && npm cache clean --force \
    && uv pip install --upgrade pip \
    && uv pip install -r /tmp/requirements.txt \
    && uv pip uninstall jupyter-server-terminals \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete \
    && jupyter serverextension list

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER $NB_USER
