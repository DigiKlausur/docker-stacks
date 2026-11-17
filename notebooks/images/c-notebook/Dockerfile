# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE

# code-server (VS Code in the browser), copied from the official image: it is
# self-contained in /usr/lib/code-server. Bump: new tag and its digest, e.g. from
# docker buildx imagetools inspect codercom/code-server:<version>
FROM codercom/code-server:4.145.2@sha256:09565f9e07f5624554e295e8bab0e2fec4a7c533eb3cff459ed6596a4d3d7c1c AS code-server

# The image itself (keep this stage last: non-e2x images build without --target)
FROM $IMAGE_SOURCE

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"
LABEL description="e2x c notebook"

COPY --from=code-server /usr/lib/code-server /usr/lib/code-server
COPY --from=code-server /usr/bin/code-server /usr/bin/code-server

# gcc, make etc. The C kernel compiles every cell with gcc, so unlike in other
# images build-essential stays in the image.
USER root
RUN apt-get update -y \
    && apt-get install --yes --no-install-recommends build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# jupyter-c-kernel ("C"): real C, but each cell is compiled and run as its own
# program, so cells share no state. jupyter-vscode-proxy: the VS Code launcher
# for jupyter-server-proxy (installed in minimal-notebook).
RUN uv pip install jupyter-c-kernel jupyter-vscode-proxy \
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
