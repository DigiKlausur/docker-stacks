ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
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

# Install Julia packages for TU Dortmund and IJulia kernel
RUN /opt/setup-scripts/setup-julia-packages.bash \
    && julia -e \
        'import Pkg; Pkg.update(); Pkg.add([ \
        "Plots", \
        "CairoMakie", \
        "HDF5", \
        "MAT", \
        "DelimitedFiles", \
        "Colors", \
        "LaTeXStrings", \
        "GZip", \
        "Serialization", \
        "ComponentArrays", \
        "BenchmarkTools", \
        "SparseArrays", \
        "Random", \
        "LinearAlgebra", \
        "Statistics", \
        "StatsBase", \
        "OrdinaryDiffEq", \
        "Optim", \
        "FiniteDiff", \
        "ForwardDiff", \
        "GridLayoutBase", \
        "COSMO", \
        "Zygote", \
        "JuMP", \
        "DataInterpolations", \
        "LineSearches", \
        "Lux", \
        "Optimization", \
        "OptimizationFlux", \
        "Flux", \
        "OptimizationOptimJL", \
        "SciMLSensitivity" \
    ]); Pkg.precompile();' \
    && jupyter kernelspec list