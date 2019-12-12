FROM ubuntu:16.04

RUN apt-get update && apt-get install -y sudo python3-pip git python3-dev libpq-dev apache2 libapache2-mod-wsgi vim libssl-dev libffi-dev wamerican \ 
 && apt-get clean && apt-get autoremove \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --upgrade pip

COPY . /data-simulator
WORKDIR /data-simulator

RUN  pip install -r requirements.txt \
     && /usr/bin/python3 setup.py develop
