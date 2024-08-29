ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x julia notebook"

USER $NB_USER

# Install Julia and IJulia package
RUN mamba install -y -c conda-forge julia \
    && /opt/conda/bin/julia -e 'using Pkg; Pkg.add("IJulia");' \
    
# Move IJulia kernel to the appropriate location
    && mkdir -p /opt/conda/share/jupyter/kernels/ \
    && mv /home/"$NB_USER"/.local/share/jupyter/kernels/* /opt/conda/share/jupyter/kernels/ \
    
# Verify the installation and list the available kernels
    && /opt/conda/bin/julia -e 'using IJulia;' \
    && jupyter kernelspec list
