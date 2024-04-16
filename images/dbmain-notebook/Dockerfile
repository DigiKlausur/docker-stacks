ARG IMAGE_SOURCE=ghcr.io/digiklausur/docker-stacks/desktop-notebook:dev
FROM $IMAGE_SOURCE

USER root

RUN wget -P /tmp https://projects.info.unamur.be/dbmain/files/dbm-1102-linux-amd64-setup.tar.gz && \
    mkdir -p /usr/local/db-main && \
    tar -xf /tmp/dbm-1102-linux-amd64-setup.tar.gz -C /usr/local/db-main --strip-components=1

RUN chown -R $NB_UID:$NB_GID /usr/local/db-main

USER $NB_USER

COPY --chown=$NB_UID:$NB_GID dbmain/start_dbmain.sh /usr/local/db-main/bin
COPY --chown=$NB_UID:$NB_GID dbmain/dbmain.desktop /usr/share/applications/
COPY --chown=$NB_UID:$NB_GID dbmain/dbmain.desktop /home/$NB_USER/xfce-userdirs/Desktop/
COPY --chown=$NB_UID:$NB_GID dbmain/dbmain.desktop /etc/xdg/autostart/
COPY --chown=$NB_UID:$NB_GID dbmain/db_main.ini /home/$NB_USER/.db-main/

RUN chmod a+x /usr/local/db-main/bin
RUN chmod +x /usr/share/applications/dbmain.desktop
RUN chmod +x /usr/local/db-main/bin/start_dbmain.sh
RUN chmod +x /home/$NB_USER/xfce-userdirs/Desktop/dbmain.desktop
RUN chmod +x /etc/xdg/autostart/dbmain.desktop

RUN echo "export DB_MAIN_BIN=/usr/local/db-main/bin" >> ~/.bashrc
RUN echo "export PATH=/usr/local/db-main/bin:$PATH" >> ~/.bashrc
RUN echo "export LD_LIBRARY_PATH=/usr/local/db-main/java/jre/lib/amd64/server:/usr/local/db-main/bin/:$LD_LIBRARY_PATH" >> ~/.bashrc

USER $NB_USER

COPY --chown=$NB_UID:$NB_GID nbextensions /tmp/nbextensions
RUN jupyter nbextension install /tmp/nbextensions/notebook-link --sys-prefix
RUN jupyter nbextension enable notebook-link/main --section=tree --sys-prefix
