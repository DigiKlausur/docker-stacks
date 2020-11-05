FROM jupyterhub/k8s-hub:0.10.2

LABEL maintainer="DigiKlausur (E2x) project HBRS <mohammad.wasil@h-brs.de>"

USER root
RUN pip3 install pandas
RUN pip install --ignore-installed --no-cache-dir git+https://github.com/DigiKlausur/nativeauthenticator.git@feature/patch-1

USER $NB_USER
