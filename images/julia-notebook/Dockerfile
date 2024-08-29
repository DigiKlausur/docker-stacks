ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x julia notebook"

USER root

# Install julia
ARG JULIA_VERSION=1.10.5

RUN apt-get update -y \
    && apt-get install --yes \
        wget \
        tar \
    && wget https://julialang-s3.julialang.org/bin/linux/x64/"$(echo $JULIA_VERSION | cut -d. -f1-2)"/julia-"$JULIA_VERSION"-linux-x86_64.tar.gz \
    && tar -xvzf julia-"$JULIA_VERSION"-linux-x86_64.tar.gz \
    && mv julia-"$JULIA_VERSION" /opt/ \
    && ln -s /opt/julia-"$JULIA_VERSION"/bin/julia /usr/local/bin/julia \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm julia-"$JULIA_VERSION"-linux-x86_64.tar.gz

USER $NB_USER

# Install the IJulia kernel and run a check to make sure that the IJulia kernel is installed
RUN julia -e 'using Pkg; Pkg.add("IJulia")' && julia -e 'using IJulia'