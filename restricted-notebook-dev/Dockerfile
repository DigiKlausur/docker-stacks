FROM digiklausur/minimal-notebook:latest

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

USER root

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install --no-cache-dir jupyterhub==1.1.*

#Install nbgrader and H-BRS DigiKlausur nbextension
RUN pip install  --no-cache-dir git+http://git@github.com/DigiKlausur/nbgrader.git@v0.7.0-dev-k8s
RUN jupyter serverextension enable --system --py nbgrader &&\
    jupyter nbextension install --system --py nbgrader --overwrite &&\
    jupyter nbextension enable --system extra_cells/main &&\
    jupyter nbextension enable --system assignment_list/main --section=tree &&\
    jupyter serverextension enable --system nbgrader.server_extensions.assignment_list

RUN cd /tmp && \
    git clone https://github.com/DigiKlausur/Jupyter-Extensions.git && \
    cd /tmp/Jupyter-Extensions && \
    git checkout -b ss20 d63ed0e && \
    cd /tmp/Jupyter-Extensions/nbextensions/exam_extensions && \
    jupyter nbextension install --system restricted_tree &&\
    jupyter nbextension enable --system restricted_tree/main --section=tree &&\
    jupyter nbextension install --system exam_view &&\
    jupyter nbextension enable --system exam_view/main &&\
    rm -rf /tmp/*

RUN cd /tmp && \
    git clone https://github.com/DigiKlausur/e2x-help.git && \
    cd /tmp/e2x-help && \
    pip install . && \
    jupyter serverextension enable --system --py e2xhelp && \
    jupyter nbextension install --system --py e2xhelp && \
    jupyter nbextension enable --system --py e2xhelp

# fix conda permission
RUN chown -R root:root $CONDA_DIR 

# remove unnecessary packages and cache
RUN conda remove --force-remove jupyterlab &&\
    conda clean --all -f -y && \
    npm cache clean --force && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf /home/$NB_USER/.cache/yarn 

#Change owner of jupyter to user, e.g. change nbgrader and other configs
RUN chown $NB_USER:$NB_GID -R /etc/jupyter

RUN jupyter nbextension list

USER $NB_USER
