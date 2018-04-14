#!/usr/bin/perl

use strict;
use warnings;

$\ = $/;

my $service = 'lifesim';

my %sim;
$sim{$_} = 1 while (<*.sim>);

my %c;
$c{$_} = 1 while (<*.c>);

open DEP, '<depencies' or die"'depencies: $!";
my %dep;
for my $line (<DEP>) {
	chomp $line;
	my @parts = split /\s*:\s*/, $line;
	my @deps = split /\s+/, $parts[1];
	$dep{$parts[0]} = \@deps;
}

open MAKE, '>Makefile' or die "Makefile: $!";

print MAKE <<END
CC=gcc
#CFLAGS=-O2 -fms-extensions -Wall -Wextra -Werror -Wno-unused-label -Wno-sequence-point -Wno-parentheses -fsanitize=undefined -fsanitize=address -g3 -I/usr/local/include
CFLAGS=-O2 -fms-extensions -I/usr/local/include

SIM=cim
SIMFLAGS=

LDFLAGS=-L/usr/local/lib -lcim -lm -lc -lwgdb

.PHONY: all clean clean-all

.NOTPARALLEL:

all: $service

END
;

for my $s (keys %sim) {
	my $name = (split /\./, $s)[0];
	my $deps = '';
	if (exists $dep{$name}) {
		for my $d (@{$dep{$name}}) {
			$deps .= " $d.atr" if exists $sim{"$d.sim"};
		}
	}
	print MAKE <<END
$name.c $name.atr: $name.sim $deps
	sleep 1
	\$(SIM) \$(SIMFLAGS) -S $name
END
;
	$c{"$name.c"} = 1;
}

my @obj;

for my $cc (keys %c) {
	my $name = (split /\./, $cc)[0];
	my $deps = '';
	if (exists $dep{$name}) {
		for my $d (@{$dep{$name}}) {
			$deps .= " $d.o" if exists $c{"$d.c"};
		}
	}
	print MAKE <<END
$name.o: $name.c
	\$(CC) \$(CFLAGS) -c -o \$@ \$^
END
;
	push @obj, "$name.o";
}

my @del;
for my $s (keys %sim) {
	my $name = (split /\./, $s)[0];
	push @del, "$name.c";
}

print MAKE <<END
$service: @obj
	\$(CC) \$(CFLAGS) -o \$@ \$^ \$(LDFLAGS) 

test: test.o sparsearray.o utils.o
	\$(CC) \$(CFLAGS) -o \$@ \$^ \$(LDFLAGS) 

clean:
	rm -f *.o *.shl *.atr @del

clean-all: clean
	rm -f $service
END
;
