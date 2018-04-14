#!/usr/bin/env python3

import checker
import aiohttp
import random
import asyncio
import string

import urllib.parse

import UserAgents

async def check_status(response, log_info):
	if response.status >= 500:
		checker.down(error='{}\n\tstatus code is {}. Content: {}\n'.format(log_info, response.status, await response.text()))
	if response.status != 200:
		checker.mumble(error='{}\n\tstatus code is {}. Content: {}\n'.format(log_info, response.status, await response.text()))

def get_log_info(name, url):
	return '[{:05}] {}: {}'.format(random.randint(0, 99999), name, url)

def decode(s):
	try:
		return urllib.parse.unquote(s, encoding="cp1251")
	except Exception as ex:
		checker.mumble(error="bad data '{}'".format(s), exception=ex)

class State:
	def __init__(self, hostname, port=None, name='', user=None, password=None):
		self.hostname = hostname
		self.name = name
		self.port = '' if port is None else ':' + str(port)
		self.useragent = UserAgents.get()
		self.session = None
		if user is not None and password is not None:
			self.create_session(user, password)
	def __del__(self):
		self.close()
	def close(self):
		if self.session is not None:
			self.session.close();
	def create_session(self, user, password):
		self.close();
		self.session = aiohttp.ClientSession(
			headers={
				'Referer': self.get_url(''), 
				'User-Agent': self.useragent,
			},
			auth=aiohttp.BasicAuth(user, password)
		)
	def get_url(self, path='', proto='http'):
		return '{}://{}{}/{}'.format(proto, self.hostname, self.port, path.lstrip('/'))

	async def get(self, url, need_check_status=True):
		url = self.get_url(url)
		log_info = get_log_info(self.name, url)
		try:
			checker.log(log_info)
			async with self.session.get(url) as response:
				if need_check_status:
					await check_status(response, log_info)
					text = await response.text()
					checker.log(log_info + ' responsed')
					return text
				else:
					return response.status, await response.text()
		except Exception as ex:
			checker.down(error=log_info, exception=ex)

	async def get_with_retries(self, url):
		status, text = await self.get(url, need_check_status=False)
		while status >= 500:
			status, text = await self.get(url, need_check_status=False)
		if status == 200:
			return text
		checker.corrupt(message="unexpected status {}".format(status));

	async def post(self, url, data=None, need_check_status=True):
		url = self.get_url(url)
		log_info = get_log_info(self.name, url)
		try:
			checker.log(log_info)
			async with self.session.post(url, data=data) as response:
				if need_check_status:
					await check_status(response, log_info)
					text = await response.text()
					checker.log(log_info + ' responsed')
					return text
				else:
					return response.status, await response.text()
		except Exception as ex:
			checker.down(error='{}\n{}'.format(log_info, data), exception=ex)

	async def post_with_retries(self, url, data):
		status, text = await self.post(url, data, need_check_status=False)
		while status >= 500:
			status, text = await self.post(url, data, need_check_status=False)
		if status == 200:
			return text
		checker.corrupt(message="unexpected status {}".format(status));

	async def register(self, username=None, password=None):
		can_retry = username is None
		username = checker.get_value_or_rand_name(username)
		password = checker.get_value_or_rand_string(password, 16)
		self.create_session(username, password)
		status, text = await self.post('/register', need_check_status=False)
		if status == 200:
			return username, password
		if status >= 400 or can_retry:
			while status != 200:
				if can_retry:
					username = checker.get_rand_string(16)
					password = checker.get_rand_string(32)
				self.create_session(username, password)
				status, text = await self.post('/register', need_check_status = False)
			return username, password
		checker.mumble(error='error while register: status {}, response {}'.format(status, text))

	async def put_data(self, data):
		return await self.post_with_retries('/create', data.encode())

	async def get_my(self):
		return (await self.get_with_retries('/my')).split('\r\n')

	async def get_data(self, user):
		return [decode(line) for line in (await self.post_with_retries('/data', user.encode())).split('\r\n')]

	async def get_users(self):
		return (await self.get_with_retries('/users')).split('\r\n')
