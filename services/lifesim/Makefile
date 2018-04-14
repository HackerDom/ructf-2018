CC=gcc
#CFLAGS=-O2 -fms-extensions -Wall -Wextra -Werror -Wno-unused-label -Wno-sequence-point -Wno-parentheses -fsanitize=undefined -fsanitize=address -g3 -I/usr/local/include
CFLAGS=-O2 -fms-extensions -I/usr/local/include

SIM=cim
SIMFLAGS=

LDFLAGS=-L/usr/local/lib -lcim -lm -lc -lwgdb

.PHONY: all clean clean-all

.NOTPARALLEL:

all: lifesim


main.c main.atr: main.sim  server.atr args.atr utils.atr
	sleep 1
	$(SIM) $(SIMFLAGS) -S main

textbuilder.c textbuilder.atr: textbuilder.sim 
	sleep 1
	$(SIM) $(SIMFLAGS) -S textbuilder

args.c args.atr: args.sim 
	sleep 1
	$(SIM) $(SIMFLAGS) -S args

utils.c utils.atr: utils.sim  textbuilder.atr
	sleep 1
	$(SIM) $(SIMFLAGS) -S utils

server.c server.atr: server.sim  utils.atr textbuilder.atr
	sleep 1
	$(SIM) $(SIMFLAGS) -S server

textbuilder.o: textbuilder.c
	$(CC) $(CFLAGS) -c -o $@ $^

whitedbutils.o: whitedbutils.c
	$(CC) $(CFLAGS) -c -o $@ $^

args.o: args.c
	$(CC) $(CFLAGS) -c -o $@ $^

network.o: network.c
	$(CC) $(CFLAGS) -c -o $@ $^

utils.o: utils.c
	$(CC) $(CFLAGS) -c -o $@ $^

picoparserutils.o: picoparserutils.c
	$(CC) $(CFLAGS) -c -o $@ $^

picohttpparser.o: picohttpparser.c
	$(CC) $(CFLAGS) -c -o $@ $^

argutils.o: argutils.c
	$(CC) $(CFLAGS) -c -o $@ $^

poll.o: poll.c
	$(CC) $(CFLAGS) -c -o $@ $^

main.o: main.c
	$(CC) $(CFLAGS) -c -o $@ $^

server.o: server.c
	$(CC) $(CFLAGS) -c -o $@ $^

lifesim: textbuilder.o whitedbutils.o args.o network.o utils.o picoparserutils.o picohttpparser.o argutils.o poll.o main.o server.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS) 

test: test.o sparsearray.o utils.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS) 

clean:
	rm -f *.o *.shl *.atr main.c textbuilder.c args.c utils.c server.c

clean-all: clean
	rm -f lifesim

