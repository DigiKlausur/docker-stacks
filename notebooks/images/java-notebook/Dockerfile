# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x java notebook"


USER $NB_USER

RUN pip install --no-cache-dir git+https://github.com/digiklausur/java_syntax_kernel.git@main && \
    python -m java_syntax_kernel.install --sys-prefix && \
    jupyter kernelspec remove python3 -f && \
    echo c.KernelSpecManager.ensure_native_kernel = False >> /etc/jupyter/jupyter_notebook_config.py && \
    echo c.NotebookApp.terminals_enabled = False >> /etc/jupyter/jupyter_notebook_config.py && \    
    jupyter nbextension list && \
    jupyter kernelspec list
    
