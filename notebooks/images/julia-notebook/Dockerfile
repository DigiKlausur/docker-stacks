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

