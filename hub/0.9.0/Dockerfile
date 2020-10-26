FROM jupyterhub/k8s-hub:0.9.0

LABEL maintainer="DigiKlausur (E2x) project HBRS <mohammad.wasil@h-brs.de>"

USER root
RUN pip3 install pandas
RUN cd /tmp &&\
    git clone https://github.com/jupyterhub/nativeauthenticator.git &&\
    cd nativeauthenticator && git checkout 32ea9e7 && \
    pip3 install -e .

USER $NB_USER
