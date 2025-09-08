ARG IMAGE_SOURCE=jupyterhub/k8s-hub:4.1.0
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur (E2x) project HBRS <e2x@h-brs.de>"
LABEL org.opencontainers.image.description="JupyterHub k8s 4.1.0 image for E2x project"
LABEL org.opencontainers.image.authors="e2x project H-BRS <e2x@inf.h-brs.de>"

ARG NB_USER=jovyan \
    NB_UID=1000 \
    HOME=/home/jovyan

USER root

RUN pip install --no-cache-dir pandas && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2x-nativeauth.git@v0.1.0-dev3 && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/miaauth.git@main && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xhub.git@main && \
    pip install --no-cache-dir git+https://github.com/DigiKlausur/e2x-exam-hub.git@v0.1.0-dev1 && \
    curl -L -o /tmp/e2x_course_service-0.1.1rc0-py3-none-any.whl https://github.com/DigiKlausur/e2x-course-service/releases/download/v0.1.1rc0/e2x_course_service-0.1.1rc0-py3-none-any.whl && \
    pip install --no-cache-dir /tmp/e2x_course_service-0.1.1rc0-py3-none-any.whl && \
    rm /tmp/e2x_course_service-0.1.1rc0-py3-none-any.whl

USER ${NB_USER}
