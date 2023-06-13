FROM python:3.8-slim

RUN apt-get update && apt-get upgrade -y

RUN mkdir -p /usr/src/ && mkdir -p /usr/work/

RUN pip install --upgrade pip \
    && pip install poetry

WORKDIR /usr/src/

ENTRYPOINT [ "/bin/bash", "-c"]
