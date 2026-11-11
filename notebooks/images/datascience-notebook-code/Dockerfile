# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

ARG CODE_VERSION=4.23.1

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x code notebook"
LABEL org.opencontainers.image.description="e2x code notebook"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root
ENV CODE_VERSION=$CODE_VERSION

RUN apt-get update -y \
    && apt-get install --yes \
       curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fOL https://github.com/coder/code-server/releases/download/v$CODE_VERSION/code-server_${CODE_VERSION}_amd64.deb \
    && dpkg -i code-server_${CODE_VERSION}_amd64.deb \
    && rm -f code-server_${CODE_VERSION}_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && find /usr/lib/code-server -type f -name '*.js.map' -delete \
    && npm cache clean --force

USER $NB_USER

# As $NB_USER (not root), so later installs (e.g. the e2x layer) can still change these packages
RUN uv pip install jupyter-server-proxy jupyter-vscode-proxy && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER $NB_USER
