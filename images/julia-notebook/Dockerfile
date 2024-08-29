ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x julia notebook"

USER root

# Install Julia
ARG JULIA_VERSION=1.10.5

RUN apt-get update -y \
    && apt-get install --yes \
        wget \
        tar \
    && wget -q https://julialang-s3.julialang.org/bin/linux/x64/"$(echo $JULIA_VERSION | cut -d. -f1-2)"/julia-"$JULIA_VERSION"-linux-x86_64.tar.gz \
    && tar -xzf julia-"$JULIA_VERSION"-linux-x86_64.tar.gz \
    && mv julia-"$JULIA_VERSION" /opt/ \
    && ln -s /opt/julia-"$JULIA_VERSION"/bin/julia /usr/local/bin/julia \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm julia-"$JULIA_VERSION"-linux-x86_64.tar.gz

# Create a shared environment directory for Julia packages
RUN mkdir -p /opt/julia-env \
    && chown root:staff /opt/julia-env \
    && chmod 775 /opt/julia-env

# Set JULIA_DEPOT_PATH to the shared environment directory
ENV JULIA_DEPOT_PATH="/opt/julia-env"

# Install the IJulia kernel globally
RUN julia -e 'using Pkg; Pkg.add("IJulia"); using IJulia' && chmod -R $NB_USER:$NB_USER /opt/julia-env

USER $NB_USER

# Verify IJulia installation for all users
RUN julia -e 'using IJulia; println("IJulia installation verified")'
