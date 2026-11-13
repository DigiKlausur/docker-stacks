# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x notebook for statistics course"
LABEL org.opencontainers.image.description="e2x notebook for statistics course"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root
# Copy nbgrader wus config
COPY configs/nbgrader_config.py /opt/conda/etc/jupyter/nbgrader_config.py
RUN chown root:"$NB_GID" /opt/conda/etc/jupyter/nbgrader_config.py &&\
    chmod g+rwX /opt/conda/etc/jupyter/nbgrader_config.py

USER $NB_USER

# Enable highlight word
RUN uv pip install jupyter_highlight_selected_word \
    && jupyter nbclassic-extension install --py --sys-prefix jupyter_highlight_selected_word \
    && jupyter nbclassic-extension enable --sys-prefix highlight_selected_word/main \
    && jupyter nbclassic-extension list

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER $NB_USER
