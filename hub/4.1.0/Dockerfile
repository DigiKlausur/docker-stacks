ARG IMAGE_SOURCE=jupyterhub/k8s-hub:4.1.0
ARG NODE_IMAGE=node:24-bookworm-slim

FROM $NODE_IMAGE AS node

FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur (E2x) project HBRS <e2x@h-brs.de>"
LABEL org.opencontainers.image.description="JupyterHub k8s 4.1.0 image for E2x project"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

ARG NB_USER=jovyan \
    NB_UID=1000 \
    HOME=/home/jovyan

USER root

# Modern Node.js (needed to build frontend assets of some packages)
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx && \
    ln -sf /usr/local/lib/node_modules/corepack/dist/corepack.js /usr/local/bin/corepack && \
    node --version && npm --version

RUN pip install --no-cache-dir pandas && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2x-nativeauth.git@v0.1.0-dev3 && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/miaauth.git@main && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xhub.git@main && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2x-exam-hub.git@v0.1.0-dev1 && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2x-course-hub.git@v0.2.0-dev && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2x-course-hub-kubespawner.git@fix/duplicate-mounts

USER ${NB_USER}
