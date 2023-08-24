FROM jupyter/minimal-notebook:4d70cf8da953
# Built from... https://hub.docker.com/r/jupyter/minimal-notebook/
#               https://github.com/jupyter/docker-stacks/blob/main/images/minimal-notebook/Dockerfile
# Built from... Ubuntu 22.04

LABEL maintainer="DigiKlausur project HBRS <e2x@inf.h-brs.de>"

USER root

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
    && apt-get install --yes \
      pandoc \
      texlive-xetex \
      texlive-fonts-recommended \
      texlive-latex-recommended \
      texlive-latex-extra \
      vim \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN rm -rf $HOME/work

#Fix opencv libGl
RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev zip wkhtmltopdf

# Create default config for ipython kernel config
RUN mkdir /etc/ipython/ && \
    chown root:$NB_GID /etc/ipython/ &&\
    chmod g+rwX /etc/ipython/ &&\
    chmod +6000 /etc/ipython/

USER $NB_USER

RUN pip install --upgrade pip

# Update jupyterhub and use the version that is used in z2jh version
RUN pip install --no-cache-dir jupyterhub==1.4.2

# Install RISE for presentation
RUN pip install --no-cache-dir RISE==5.7.1 && \
    jupyter-nbextension install rise --py --sys-prefix

# Jupyter contrib extensions
RUN cd /tmp && \
    git clone --depth 1 -b master https://github.com/ipython-contrib/jupyter_contrib_nbextensions.git && \
    cd /tmp/jupyter_contrib_nbextensions/src/jupyter_contrib_nbextensions/nbextensions && \
    jupyter nbextension install --sys-prefix codefolding && \
    jupyter nbextension enable --sys-prefix codefolding/main && \
    jupyter nbextension install --sys-prefix collapsible_headings && \
    jupyter nbextension enable --sys-prefix collapsible_headings/main && \
    jupyter nbextension install --sys-prefix execute_time && \
    jupyter nbextension enable --sys-prefix execute_time/ExecuteTime && \
    rm -rf /tmp/jupyter_contrib_nbextensions

RUN jupyter nbextension list