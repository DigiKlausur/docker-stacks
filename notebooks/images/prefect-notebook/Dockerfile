# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x prefect notebook"
LABEL org.opencontainers.image.description="e2x prefect notebook"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

# Opt out of Prefect's anonymous usage data: on the server, and in clients (flows)
ENV PREFECT_SERVER_ANALYTICS_ENABLED=false \
    DO_NOT_TRACK=1

# start-prefect and start-datacontract-editor: run the Prefect server and the
# Data Contract Editor behind jupyter-server-proxy (from the parent image)
COPY --chmod=755 scripts/start-prefect scripts/start-datacontract-editor /usr/local/bin/

USER $NB_USER

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN uv pip install -r /tmp/requirements.txt \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER $NB_USER
