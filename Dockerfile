FROM ubuntu:16.04

RUN apt-get update && apt-get install -y sudo python-pip git python-dev libpq-dev apache2 libapache2-mod-wsgi vim libssl-dev libffi-dev wamerican \ 
 && apt-get clean && apt-get autoremove \
 && rm -rf /var/lib/apt/lists/*

COPY . /data-simulator
WORKDIR /data-simulator

RUN  pip install -r requirements.txt \
     && python setup.py develop
