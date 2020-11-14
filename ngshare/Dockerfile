FROM jupyterhub/jupyterhub:latest
LABEL maintainer="DigiKlausur project HBRS <mohammad.wasil@h-brs.de>"

#RUN apt-get install git-all
RUN apt-get update && \
    apt-get install -y git &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*
# Change time
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install exam kernel
RUN pip install --no-cache-dir git+https://github.com/LibreTexts/ngshare.git@89685b12580990f983d4523e0ec45fd249afb702

USER 65535:65535
ENTRYPOINT ["python3", "-m", "ngshare"]
