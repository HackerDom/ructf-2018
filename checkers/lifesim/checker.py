#!/usr/bin/env python3

import sys
import traceback
import random
import string
import json
import asyncio
import time

import TextGenerator

printable = string.digits + string.ascii_letters + string.punctuation

def ructf_error(status=110, message=None, error=None, exception=None):
	if message:
		sys.stdout.write(message)
		sys.stdout.write("\n")

	sys.stderr.write("{}\n".format(status))
	if error:
		sys.stderr.write(error)
		sys.stderr.write("\n")

	if exception:
#		print(dir(exception))
		sys.stderr.write("Exception: {}\n".format(exception))
		traceback.print_tb(exception.__traceback__, file=sys.stderr)

	sys.exit(status)

def ok(status=101, message="Service OK", *args, **kwargs):
	return ructf_error(status, message, *args, **kwargs)

def corrupt(status=102, *args, **kwargs):
	return ructf_error(status, *args, **kwargs)

def mumble(status=103, *args, **kwargs):
	return ructf_error(status, *args, **kwargs)

def down(status=104, *args, **kwargs):
	return ructf_error(status, *args, **kwargs)

def make_err_message(message, request, reply):
	return "{}\n->\n{}\n<-\n{}\n=".format(message, request, reply)

def get_value_or_rand_string(value, l, additional=''):
	if value is None:
		return get_rand_string(l, additional)
	else:
		return value

def get_value_or_rand_name(value):
	if value is None:
		return TextGenerator.get_name()
	else:
		return value

def get_value_or_rand_text(value):
	if value is None:
		return TextGenerator.get_text()
	else:
		return value

def get_rand_string(l, additional=''):
	return ''.join(random.choice(string.ascii_lowercase + additional) for _ in range(l + random.randint(-l//2, l//2))).strip()

def parse_json(string, *expected):
	try:
		data = json.loads(string)
	except Exception as ex:
		mumble(error='can\'t parse string "{}" as json'.format(string), exception=ex)
	if len(expected) == 0:
		return data
	for fields in expected:
		errors = []
		for field in fields:
			if field not in data:
				errors.append(field)
		if len(errors) == 0:
			return data
	else:
		if len(errors) > 0:
			mumble(error='not all expected fields have founded in json. last expexted: {}'.format(str(errors)))

class Checker:
	def __init__(self, check, flag_handlers):
		self.check_handler = check
		self.flag_handlers = []
		for t in flag_handlers:
			if len(t) == 2:
				self.flag_handlers.append((t[0], t[1], 1))
			elif len(t) == 3:
				self.flag_handlers.append((t[0], t[1], t[2]))
			else:
				raise ValueError('wrong number of handlers')
		self.handlers = {
			'info' : self.info,
			'check' : self.check,
			'put' : self.put,
			'get' : self.get
		}
	def process(self, args):
		handler = args[1]
		if handler not in self.handlers:
			raise ValueError('unknown query type')
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.handlers[handler](args[2:]))
		loop.close()
	def info(self, args):
		ok(message='vulns: {}'.format(':'.join(map(lambda t : str(t[2]), self.flag_handlers))))
	async def check(self, args):
		host = args[0]
		await self.check_handler(host)
	def put(self, args):
		host, id, flag, vuln = args
		return self.get_vuln(vuln)[0](host, id, flag)
	def get(self, args):
		host, id, flag, vuln = args
		return self.get_vuln(vuln)[1](host, id, flag)
	def get_vuln(self, vuln):
		vuln = int(vuln) - 1
		if vuln >= len(self.flag_handlers):
			raise ValueError('wrong number of vuln')
		return self.flag_handlers[vuln]


start = time.time()
def log(*message):
	print('{: 2.05f}'.format(time.time() - start), *message, file=sys.stderr)
	sys.stderr.flush()