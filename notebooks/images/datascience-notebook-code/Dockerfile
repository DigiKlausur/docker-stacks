# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE

# code-server: bump both together. The digest is shown next to the .deb on the
# GitHub release page (or: gh release view v<version> --repo coder/code-server --json assets).
ARG CODE_VERSION=4.145.2
ARG CODE_SHA256=7eddbdeaab34380bde3ac3bbadce58fe2f5722c4877f331ea593ae797c2517e1

# Download the code-server .deb in its own stage, so it never ends up in an image
# layer (240 MB) and the image needs no curl. BuildKit caches the download.
FROM scratch AS code-server
ARG CODE_VERSION
ADD https://github.com/coder/code-server/releases/download/v${CODE_VERSION}/code-server_${CODE_VERSION}_amd64.deb \
    /code-server.deb

# The image itself (keep this stage last: non-e2x images build without --target)
FROM $IMAGE_SOURCE
ARG CODE_VERSION CODE_SHA256

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x code notebook"
LABEL org.opencontainers.image.description="e2x code notebook"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root
ENV CODE_VERSION=$CODE_VERSION

RUN --mount=type=bind,from=code-server,source=/code-server.deb,target=/tmp/code-server.deb \
    echo "${CODE_SHA256}  /tmp/code-server.deb" | sha256sum -c - \
    && dpkg -i /tmp/code-server.deb \
    && find /usr/lib/code-server -type f -name '*.js.map' -delete

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
