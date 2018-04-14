FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install libwgdb-dev whitedb make libc6-dev gcc -y

COPY . /home/lifesim
WORKDIR /home/lifesim

RUN dpkg -i cim_5.1-1_amd64.deb

RUN ./configure.pl
RUN make

CMD LD_LIBRARY_PATH=/usr/local/lib  ./lifesim 8084 314 271
