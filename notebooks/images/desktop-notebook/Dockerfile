# check=skip=InvalidDefaultArgInFrom
# IMAGE_SOURCE has no default on purpose: scripts/image_builder sets it from
# notebooks.toml. Build with: python scripts/image_builder build <image>
ARG IMAGE_SOURCE
FROM $IMAGE_SOURCE

USER root

RUN apt-get -y -qq update \
    && apt-get -y -qq install \
        dbus-x11 \
        xfce4 \
        xfce4-panel \
        xfce4-session \
        xfce4-settings \
        xorg \
        xubuntu-icon-theme \
        fonts-dejavu \
        libgtk2.0-0 \
        # Disable the automatic screenlock since the account password is unknown
    && apt-get -y -qq remove xfce4-screensaver \
        # chown $HOME to workaround that the xorg installation creates a
        # /home/$NB_USER/.cache directory owned by root
    && chown -R "$NB_UID":"$NB_GID" "$HOME" \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install a VNC server, either TigerVNC (default) or TurboVNC
ARG vncserver=tigervnc
RUN if [ "${vncserver}" = "tigervnc" ]; then \
        echo "Installing TigerVNC"; \
        apt-get -y -qq update; \
        apt-get -y -qq install \
            tigervnc-standalone-server \
            tigervnc-xorg-extension \
        ; \
        apt-get clean; \
        rm -rf /var/lib/apt/lists/*; \
    fi
ENV PATH=/opt/TurboVNC/bin:$PATH
RUN if [ "${vncserver}" = "turbovnc" ]; then \
        echo "Installing TurboVNC"; \
        # Install instructions from https://turbovnc.org/Downloads/YUM
        wget -q -O- https://packagecloud.io/dcommander/turbovnc/gpgkey | \
        gpg --dearmor >/etc/apt/trusted.gpg.d/TurboVNC.gpg; \
        wget -O /etc/apt/sources.list.d/TurboVNC.list https://raw.githubusercontent.com/TurboVNC/repo/main/TurboVNC.list; \
        apt-get -y -qq update; \
        apt-get -y -qq install \
            turbovnc \
        ; \
        apt-get clean; \
        rm -rf /var/lib/apt/lists/*; \
    fi



USER $NB_USER

COPY --chown=$NB_UID:$NB_GID config/user-dirs.defaults /etc/xdg/

RUN uv pip install "jupyter-server-proxy>=1.4" websockify jupyter_remote_desktop_proxy && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

USER root

COPY config/user-dirs.defaults /etc/xdg/
RUN mkdir -p /usr/local/xfce-userdirs/
RUN chown -R "$NB_UID":"$NB_GID" /usr/local/xfce-userdirs/

USER $NB_USER
RUN xdg-user-dirs-update

# Record this build in /etc/image-info.json (see notebooks/image_info).
# Keep this at the end: GIT_COMMIT and BUILD_DATE change on every build, and
# every RUN after their ARG line is rebuilt each time.
ARG IMAGE_SOURCE IMAGE_NAME GIT_COMMIT BUILD_DATE
USER root
COPY --from=image_info --chmod=755 image_info.py /usr/local/bin/image_info
RUN image_info record --name "$IMAGE_NAME" --parent "$IMAGE_SOURCE" \
        --git-commit "$GIT_COMMIT" --build-date "$BUILD_DATE"
USER $NB_USER
