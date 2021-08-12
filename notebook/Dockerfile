ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

#Fix opencv libGl
USER root
RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev

# Install PDF libraries
RUN apt-get install -y wkhtmltopdf

# Create default config for ipython kernel config
RUN mkdir /etc/ipython/ && \
    chown root:$NB_GID /etc/ipython/ &&\
    chmod g+rwX /etc/ipython/ &&\
    chmod +6000 /etc/ipython/

USER $NB_USER

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Update jupyterhub and use the version that is used in z2jh version
RUN pip install --no-cache-dir jupyterhub==1.4.*

# Install nbzip
RUN pip install --no-cache-dir nbzip==0.1.0 && \
    jupyter serverextension enable  --sys-prefix --py nbzip && \
    jupyter nbextension     install --sys-prefix --py nbzip && \
    jupyter nbextension     enable  --sys-prefix --py nbzip

# Install nbgrader and H-BRS DigiKlausur nbextension
RUN pip install --no-cache-dir git+https://github.com/jupyter/nbgrader.git@master

# Install ngshare_exchange
RUN pip install --no-cache-dir ngshare_exchange

# Install e2xgrader and enable e2xgrader extensions
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xgrader.git@dev

# Activate student mode by default
RUN python -m e2xgrader activate student --sys-prefix

# Install assignmenttest
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/assignmenttest@master

# Install exam kernel
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/exam_kernel@master
RUN python -m exam_kernel.install --sys-prefix
RUN touch /etc/ipython/ipython_config.py

# Install e2x-help
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2x-help.git@master

# Install graphviz via conda
RUN conda install graphviz

RUN jupyter nbextension list

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
