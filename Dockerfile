FROM quay.io/cdis/python:python3.9-buster-2.0.0

RUN apt-get update \
     && apt-get install -y --no-install-recommends\
     ca-certificates \
     gcc \
     curl bash git vim \
     musl-dev \
     libffi-dev

COPY . /data-simulator
WORKDIR /data-simulator

RUN pip install --upgrade pip && pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -vv
