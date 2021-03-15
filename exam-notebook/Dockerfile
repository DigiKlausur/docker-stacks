FROM digiklausur/minimal-notebook:latest

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

#Fix opencv libGl
USER root
RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev

# Create default config for ipython kernel config
RUN mkdir /etc/ipython/ && \
    chown root:$NB_GID /etc/ipython/ &&\
    chmod g+rwX /etc/ipython/ &&\
    chmod +6000 /etc/ipython/

USER $NB_USER

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install --no-cache-dir jupyterhub==1.3.*

# Install nbzip
RUN pip install --no-cache-dir nbzip==0.1.0 && \
    jupyter serverextension enable  --sys-prefix --py nbzip && \
    jupyter nbextension     install --sys-prefix --py nbzip && \
    jupyter nbextension     enable  --sys-prefix --py nbzip

# Install nbgrader and H-BRS DigiKlausur nbextension
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/nbgrader.git@clean_up

# Install ngshare_exchange
RUN pip install --no-cache-dir ngshare_exchange

# Install e2xgrader and enable e2xgrader extensions
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xgrader@dev

# Activate student mode by default
RUN e2xgrader activate student_exam --sys-prefix

# Install nbassignment
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/nbassignment@dev

# Install assignmenttest
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/assignmenttest@master

# Install exam kernel
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/exam_kernel@master
RUN python -m exam_kernel.install --sys-prefix
RUN touch /etc/ipython/ipython_config.py

# Install e2x-help
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2x-help.git@master
RUN jupyter serverextension enable e2xhelp --py --sys-prefix && \
    jupyter nbextension install e2xhelp --py --sys-prefix && \
    jupyter nbextension enable e2xhelp --py --sys-prefix

# Install graphviz via conda
RUN conda install graphviz

RUN jupyter nbextension list

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
