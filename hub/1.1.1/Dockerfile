FROM jupyterhub/k8s-hub:1.1.1

LABEL maintainer="DigiKlausur (E2x) project HBRS <mohammad.wasil@h-brs.de>"

USER root
RUN pip install pandas

# use e2x version
RUN pip install --no-cache-dir --upgrade --no-deps --force-reinstall git+https://github.com/DigiKlausur/nativeauthenticator.git@feature/patch-1

USER $NB_USER
