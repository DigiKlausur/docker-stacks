FROM digiklausur/minimal-notebook:latest

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

USER $NB_USER

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install --no-cache-dir jupyterhub==1.1.*

RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
    jupyter serverextension enable --py jupyterlab --sys-prefix

# Install nbzip
RUN pip install --no-cache-dir nbzip==0.1.0 && \
    jupyter serverextension enable  --sys-prefix --py nbzip && \
    jupyter nbextension     install --sys-prefix --py nbzip && \
    jupyter nbextension     enable  --sys-prefix --py nbzip

# Install RISE for presentation
RUN pip install --no-cache-dir RISE==5.6.1 && \
    jupyter-nbextension install rise --py --sys-prefix

# Install codefolding and google translate
RUN pip install --no-cache-dir jupyter-contrib-nbextensions==0.5.1 && \
    jupyter contrib nbextension install --sys-prefix && \
    jupyter nbextension enable --sys-prefix codefolding/main && \
    jupyter nbextension enable --sys-prefix nbTranslate/main && \
    jupyter nbextension enable --sys-prefix collapsible_headings/main

# Install nbgrader and H-BRS DigiKlausur nbextension
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/nbgrader.git@clean_up

# Install e2xgrader and enable e2xgrader extensions
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xgrader@master

# Activate student mode by default
RUN python -m e2xgrader activate student --sys-prefix

RUN jupyter nbextension list