#!/usr/bin/env python3

from random import choice


def read(filename):
	res = []
	with open('words/' + filename, 'r') as fin:
		for line in fin:
			res.append(line.strip())
	return res


nouns = read('nouns')
verbs = read('verbs')
adjectives = read('adjectives')

def get_text():
	return '{} {} {}'.format(choice(adjectives).capitalize(), choice(nouns).capitalize(), choice(verbs))

def get_name():
	return choice(adjectives).capitalize() + choice(nouns).capitalize()