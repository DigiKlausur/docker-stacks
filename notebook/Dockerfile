ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/minimal-notebook:latest
FROM $IMAGE_SOURCE

LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

ARG E2XGRADER_BRANCH=master

#Fix opencv libGl
USER root
RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev zip wkhtmltopdf

# Fixes libQt5Core not found (https://github.com/microsoft/WSL/issues/3023)
RUN strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5

# Create default config for ipython kernel config
RUN mkdir /etc/ipython/ && \
    chown root:$NB_GID /etc/ipython/ &&\
    chmod g+rwX /etc/ipython/ &&\
    chmod +6000 /etc/ipython/

USER $NB_USER

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install pytorch
RUN pip install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Update jupyterhub and use the version that is used in z2jh version
RUN pip install --no-cache-dir jupyterhub==1.4.2

# Install nbzip
RUN pip install --no-cache-dir nbzip==0.1.0 && \
    jupyter serverextension enable  --sys-prefix --py nbzip && \
    jupyter nbextension     install --sys-prefix --py nbzip && \
    jupyter nbextension     enable  --sys-prefix --py nbzip

# Install ngshare_exchange
# Use the latest commit after this PR: https://github.com/LibreTexts/ngshare_exchange/pull/19 
# to ensure compatibility with nbgrader 7 and up
RUN pip install --no-cache-dir ngshare_exchange>=0.5.2

# Install e2xgrader and enable e2xgrader extensions
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xgrader.git@dev

# Activate student mode by default
RUN e2xgrader activate student --sys-prefix

# Install assignmenttest
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/assignmenttest@master

# Install e2xtest
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/e2xtest@main


# Install pdf feedback
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/pdf_feedback_exporter@main

# Install exam kernel
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/exam_kernel@master
RUN python -m exam_kernel.install --sys-prefix
RUN touch /etc/ipython/ipython_config.py

# Install java syntax kernel
RUN pip install --no-cache-dir git+https://github.com/DigiKlausur/java_syntax_kernel@main
RUN python -m java_syntax_kernel.install --sys-prefix

# Install graphviz via conda
RUN conda install graphviz

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

USER root
RUN rm /tmp/requirements.txt

USER $NB_USER
