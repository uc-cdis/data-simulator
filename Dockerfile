
FROM python:3.6-alpine

RUN apk update \
     && apk add --no-cache \
     ca-certificates \
     gcc \
     bash \
     curl \
     musl-dev \
     libffi-dev \
     openssl-dev \
     postgresql-dev \
     && pip install --upgrade pip

COPY . /data-simulator
WORKDIR /data-simulator

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -vv
