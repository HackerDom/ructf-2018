FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install libwgdb-dev whitedb make -y

COPY . /home/lifesim
WORKDIR /home/lifesim

CMD bash

