
FROM python:3.12.0a5-alpine

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
     git \
     g++ \
     && pip install --upgrade pip
# add g++ because greenlet needs it (imported by sqlalchemy 1.4)

COPY . /data-simulator
WORKDIR /data-simulator

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -vv
