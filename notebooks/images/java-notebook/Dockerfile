# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x java notebook"


USER $NB_USER

RUN uv pip install git+https://github.com/digiklausur/java_syntax_kernel.git@main && \
    python -m java_syntax_kernel.install --sys-prefix && \
    jupyter kernelspec remove python3 -f && \
    echo c.KernelSpecManager.ensure_native_kernel = False >> /etc/jupyter/jupyter_notebook_config.py && \
    echo c.NotebookApp.terminals_enabled = False >> /etc/jupyter/jupyter_notebook_config.py && \    
    jupyter nbclassic-extension list && \
    jupyter kernelspec list

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER $NB_USER
    
