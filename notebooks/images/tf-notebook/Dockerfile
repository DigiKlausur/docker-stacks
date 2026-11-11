# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x tensorflow machine learning notebook"
LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL org.opencontainers.image.title="tf-notebook"
LABEL org.opencontainers.image.description="A Docker image for the for Jupyter notebook based on datascience notebook with tensorflow installed."
LABEL org.opencontainers.image.vendor="H-BRS"
LABEL org.opencontainers.image.url="https://github.com/DigiKlausur/docker-stacks/"
LABEL org.opencontainers.image.source="https://github.com/DigiKlausur/docker-stacks/notebooks/images/tf-notebook"
LABEL org.opencontainers.image.licenses="MIT"

USER root

# Install requirements and list extensions
COPY requirements.txt /tmp/requirements.txt
RUN uv pip install -r /tmp/requirements.txt \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete \
    && jupyter nbextension list

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER $NB_USER
