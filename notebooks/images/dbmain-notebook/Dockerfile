# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

USER root

RUN wget -P /tmp -q https://projects.info.unamur.be/dbmain/files/dbm-1102-linux-amd64-setup.tar.gz --no-check-certificate && \
    mkdir -p /usr/local/db-main && \
    tar -xf /tmp/dbm-1102-linux-amd64-setup.tar.gz -C /usr/local/db-main --strip-components=1 && \
    rm /tmp/dbm-1102-linux-amd64-setup.tar.gz && \
    chown -R "$NB_UID":"$NB_GID" /usr/local/db-main

USER $NB_USER

COPY --chown=$NB_UID:$NB_GID dbmain/start_dbmain.sh /usr/local/db-main/bin
COPY --chown=$NB_UID:$NB_GID dbmain/dbmain.desktop /usr/share/applications/
COPY --chown=$NB_UID:$NB_GID dbmain/dbmain.desktop /usr/local/xfce-userdirs/Desktop/
COPY --chown=$NB_UID:$NB_GID dbmain/dbmain.desktop /etc/xdg/autostart/
COPY --chown=$NB_UID:$NB_GID dbmain/db_main.ini /home/$NB_USER/.db-main/

RUN chmod a+x /usr/local/db-main/bin && \
    chmod +x /usr/share/applications/dbmain.desktop && \
    chmod +x /usr/local/db-main/bin/start_dbmain.sh && \
    chmod +x /usr/local/xfce-userdirs/Desktop/dbmain.desktop && \
    chmod +x /etc/xdg/autostart/dbmain.desktop

ENV DB_MAIN_BIN=/usr/local/db-main/bin
ENV PATH=/usr/local/db-main/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/db-main/java/jre/lib/amd64/server:/usr/local/db-main/bin/

RUN echo "export DB_MAIN_BIN=/usr/local/db-main/bin" >> ~/.bashrc && \
    echo "export PATH=/usr/local/db-main/bin:$PATH" >> ~/.bashrc && \
    echo "export LD_LIBRARY_PATH=/usr/local/db-main/java/jre/lib/amd64/server:/usr/local/db-main/bin/:$LD_LIBRARY_PATH" >> ~/.bashrc

USER $NB_USER

COPY --chown=$NB_UID:$NB_GID nbextensions /tmp/nbextensions
RUN jupyter nbextension install /tmp/nbextensions/notebook-link --sys-prefix && \
    jupyter nbextension enable notebook-link/main --section=tree --sys-prefix

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER $NB_USER
