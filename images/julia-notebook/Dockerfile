ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x julia notebook"

USER root

# Set Julia environment variables
ENV JULIA_DEPOT_PATH=/opt/julia-1.10.5/share/julia
ENV JULIA_PKGDIR=/opt/julia-1.10.5/share/julia
ENV JULIA_VERSION=1.10.5

# Install Julia
RUN apt-get update && apt-get install -y wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q https://julialang-s3.julialang.org/bin/linux/x64/1.10/julia-1.10.5-linux-x86_64.tar.gz \
    && tar zxf julia-1.10.5-linux-x86_64.tar.gz \
    && mv julia-1.10.5 /opt/ \
    && ln -s /opt/julia-1.10.5/bin/julia /usr/local/bin/julia \
    && rm julia-1.10.5-linux-x86_64.tar.gz \
    && chown -R "$NB_USER":users /opt/julia-1.10.5

USER $NB_USER

# Install Julia kernel and set permissions
RUN julia -e 'using Pkg; Pkg.add("IJulia");' \
    && chmod -R 777 /opt/julia-1.10.5/share/julia \
    && mkdir -p /opt/conda/share/jupyter/kernels/julia-1.10 \
    && mv /home/"$NB_USER"/.local/share/jupyter/kernels/julia-1.10 /opt/conda/share/jupyter/kernels/ \
    && jupyter kernelspec list
