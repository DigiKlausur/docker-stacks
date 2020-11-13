FROM jupyterhub/k8s-hub:0.9.1

LABEL maintainer="DigiKlausur (E2x) project HBRS <mohammad.wasil@h-brs.de>"

USER root
RUN pip install pandas
RUN pip install --no-cache-dir --upgrade --no-deps --force-reinstall git+https://github.com/DigiKlausur/nativeauthenticator.git@feature/patch-1

USER $NB_USER
