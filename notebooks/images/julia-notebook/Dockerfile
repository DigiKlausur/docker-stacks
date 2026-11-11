# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x julia notebook"

USER root

# CPU architecture
RUN echo "Compile target is $(uname -m)"

# Set Julia environment variables
ENV JULIA_DEPOT_PATH=/opt/julia \
    JULIA_PKGDIR=/opt/julia \
    JULIA_VERSION=1.10.5

# Install Julia using the script provided by Jupyter
RUN /opt/setup-scripts/setup-julia.bash

USER ${NB_UID}

COPY scripts/setup-julia-packages.bash /tmp/setup-julia-packages.bash
COPY julia-packages.txt /tmp/julia-packages.txt

USER root
# Change ownership of the copied files to NB_UID
USER root
RUN chown ${NB_UID}:${NB_UID} /tmp/setup-julia-packages.bash /tmp/julia-packages.txt

USER ${NB_UID}

# Run the setup script to install Julia packages and the IJulia kernel
RUN /tmp/setup-julia-packages.bash /tmp/julia-packages.txt \
    && rm /tmp/julia-packages.txt \
    && rm /tmp/setup-julia-packages.bash \
    && jupyter kernelspec list

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER ${NB_UID}

