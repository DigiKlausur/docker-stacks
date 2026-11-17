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

USER root

# Man pages (e.g. `man 3 printf`): the base image is a minimized Ubuntu that drops
# them and replaces `man` with a stub. Undo both, so packages installed from here
# on bring their man pages (packages installed before keep none).
RUN sed -i '\|^path-exclude=/usr/share/man/|d' /etc/dpkg/dpkg.cfg.d/excludes \
    && rm /usr/bin/man \
    && dpkg-divert --quiet --remove --rename /usr/bin/man

# Tools for the systems programming course. build-essential (gcc, make and the
# sanitizer runtimes) stays in the image: the C kernel compiles every cell with gcc.
RUN apt-get update -y \
    && apt-get install --yes --no-install-recommends \
        build-essential gdb cmake clang lldb cppcheck \
        clang-format clang-tidy \
        strace ltrace elfutils valgrind \
        man-db manpages-dev glibc-doc \
        bsdmainutils bear libtree xxd netcat-openbsd parallel btop \
        meson ninja-build \
        pkg-config autoconf automake libtool \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Intel syntax by default (assembler chapter): `objdump -M intel` alias and the
# `cintel` helper for interactive shells. profile.d covers login shells,
# bash.bashrc the terminals of Jupyter and VS Code.
COPY scripts/intel-syntax.sh /etc/profile.d/99-intel-syntax.sh
RUN echo '. /etc/profile.d/99-intel-syntax.sh' >> /etc/bash.bashrc

# gdb: Intel syntax as well, and keep ASLR on. gdb turns ASLR off by default, which
# containers forbid, so every run would print "Error disabling address space
# randomization".
RUN printf 'set disassembly-flavor intel\nset disable-randomization off\n' \
        > /etc/gdb/gdbinit.d/e2x.gdb

# Java 25 JDK (Eclipse Temurin) for mixing languages: Java calls C/assembler via the
# Foreign Function & Memory API (java.lang.foreign, final since JDK 22). 25 = LTS.
# The 25-jdk tag follows patch releases (security fixes), like the JRE in bi-notebook.
ENV JAVA_HOME=/opt/java/openjdk
COPY --from=eclipse-temurin:25-jdk $JAVA_HOME $JAVA_HOME
ENV PATH="${JAVA_HOME}/bin:${PATH}"

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
