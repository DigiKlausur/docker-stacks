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
    jupyter nbextension enable --system assignment_list/main --section=tree &&\
    jupyter serverextension enable --system nbgrader.server_extensions.assignment_list

RUN cd /tmp && \
    git clone https://github.com/DigiKlausur/Jupyter-Extensions.git && \
    cd /tmp/Jupyter-Extensions/nbextensions/exam_extensions && \
    jupyter nbextension install --system restricted_tree &&\
    jupyter nbextension enable --system restricted_tree/main --section=tree &&\
    jupyter nbextension install --system exam_view &&\
    jupyter nbextension enable --system exam_view/main &&\
    rm -rf /tmp/*

# fix conda permission
RUN chown root:$NB_GID $CONDA_DIR 

# remove unnecessary packages and cache
RUN conda remove --force-remove jupyterlab &&\
    conda clean --all -f -y && \
    npm cache clean --force && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf /home/$NB_USER/.cache/yarn 

RUN jupyter nbextension list

USER $NB_USER
