FROM jupyter/minimal-notebook:4d70cf8da953
# Built from... https://hub.docker.com/r/jupyter/minimal-notebook/
#               https://github.com/jupyter/docker-stacks/blob/main/images/minimal-notebook/Dockerfile
# Built from... Ubuntu 22.04

LABEL maintainer="e2x project H-BRS <e2x@inf.h-brs.de>"

USER root

ENV TZ=Europe/Berlin

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Create default config for ipython kernel config
RUN mkdir /etc/ipython/ && \
    chown root:$NB_GID /etc/ipython/ &&\
    chmod g+rwX /etc/ipython/ &&\
    chmod +6000 /etc/ipython/

# Remove default work dir
RUN rm -rf $HOME/work

RUN apt-get update -y \
    && apt-get install --yes \
       pandoc \
       texlive-xetex \
       texlive-fonts-recommended \
       texlive-latex-recommended \
       texlive-latex-extra \
       vim \
       libgl1-mesa-dev zip wkhtmltopdf \
       build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER $NB_USER

# Install conda related pkgs
RUN conda install gh --channel conda-forge && \
    conda install graphviz

RUN pip install --upgrade pip && \
    pip install --no-cache-dir RISE==5.7.1

# Enable extenstions and Jupyter contrib extensions
RUN cd /tmp && \
    git clone --depth 1 -b master https://github.com/ipython-contrib/jupyter_contrib_nbextensions.git && \
    cd /tmp/jupyter_contrib_nbextensions/src/jupyter_contrib_nbextensions/nbextensions && \
    jupyter nbextension install --sys-prefix codefolding && \
    jupyter nbextension enable --sys-prefix codefolding/main && \
    jupyter nbextension install --sys-prefix collapsible_headings && \
    jupyter nbextension enable --sys-prefix collapsible_headings/main && \
    jupyter nbextension install --sys-prefix execute_time && \
    jupyter nbextension enable --sys-prefix execute_time/ExecuteTime && \
    jupyter-nbextension install rise --py --sys-prefix && \
    jupyter nbextension list && \
    rm -rf /tmp/jupyter_contrib_nbextensions

USER root

# clean up
RUN rm /tmp/requirements.txt && \
    /opt/conda/bin/conda clean -afy && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyc' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

USER $NB_USER
