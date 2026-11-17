# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x c notebook"

# gcc, make etc. The C kernel compiles every cell with gcc, so unlike in other
# images build-essential stays in the image.
USER root
RUN apt-get update -y \
    && apt-get install --yes --no-install-recommends build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# jupyter-c-kernel ("C"): real C, but each cell is compiled and run as its own
# program, so cells share no state.
RUN uv pip install jupyter-c-kernel \
    && install_c_kernel --sys-prefix

# xeus-cpp: a C++ interpreter (clang-repl), cells share state. Successor of
# xeus-cling, which no longer installs next to the base environment.
RUN mamba install -y --channel conda-forge --freeze-installed xeus-cpp \
    && mamba clean -afy \
    && jupyter kernelspec list

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER $NB_USER
