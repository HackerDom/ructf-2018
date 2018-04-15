FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install libwgdb-dev whitedb make libc6-dev gcc -y

COPY . /home/lifesim
WORKDIR /home/lifesim

RUN dpkg -i cim_5.1-1_amd64.deb

RUN ./configure.pl
RUN make

CMD ./prepare.sh 1234 && ./prepare.sh 4321 && (./run.sh 8085 & ./run.sh 8086 & ./run.sh 8087 & ./dump.sh 1234 & ./dump.sh 4321)
