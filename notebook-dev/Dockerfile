FROM digiklausur/minimal-notebook:latest

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

#Fix opencv libGl
USER root
RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev

USER $NB_USER
COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install --no-cache-dir jupyterhub==1.1.*

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
#RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xgrader@dev

# Activate student mode by default
#RUN python -m e2xgrader activate student --sys-prefix

# Install exam kernel
#RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/exam_kernel@master
#RUN python -m exam_kernel.install --sys-prefix

################################ Use this e2xgrader version formgrader does not work yet
#disable default formgrader and assignment_list server extensions
RUN jupyter serverextension disable nbgrader.server_extensions.formgrader --sys-prefix &&\
    jupyter serverextension disable nbgrader.server_extensions.assignment_list --sys-prefix

#install e2xgrader and enable e2xgrader extensions
# Install ngshare_exchange
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xgrader@d4cc04a
RUN jupyter serverextension enable e2xgrader --py --sys-prefix &&\
    jupyter nbextension install e2xgrader --py --sys-prefix --overwrite &&\
    jupyter nbextension enable e2xgrader --py --sys-prefix

#install students extension
# Install e2xgrader and enable e2xgrader extensions
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xstudent.git@main
RUN jupyter nbextension install e2xstudent --py --sys-prefix &&\
    jupyter nbextension enable e2xstudent --py --sys-prefix &&\
    jupyter nbextension disable exam_view/main --sys-prefix &&\
    jupyter nbextension disable restricted_tree/main --sys-prefix --section=tree
###############################

RUN jupyter nbextension list
