#!/usr/bin/env python3

import checker
import aiohttp
import random
import asyncio
import string

import UserAgents

def get_cookie_string(cookies):
	return '; '.join([str(cookie.key) + '=' + str(cookie.value) for cookie in cookies])

async def check_status(response, log_info):
	if response.status >= 500:
		checker.down(error='{}\n\tstatus code is {}. Content: {}\n'.format(log_info, response.status, await response.text()))
	if response.status != 200:
		checker.mumble(error='{}\n\tstatus code is {}. Content: {}\n'.format(log_info, response.status, await response.text()))

class WSHelper:
	def __init__(self, connection):
		self.connection = connection
		self.queue = asyncio.Queue()
		self.wanted = set()
		self.closed = False
	def start(self):
		asyncio.async(self.start_internal())
	async def start_internal(self):
		try:
			async with self.connection as ws:
				async for msg in ws:
					if msg.type == aiohttp.WSMsgType.TEXT:
						try:
							data = msg.json(loads = lambda s : checker.parse_json(s, ['id', 'x', 'y', 'message', 'public', 'user'], ['id']))
						except Exception as ex:
							checker.mumble(error='can\'t parse service responce', exception=ex)
						await self.queue.put(data)
					elif msg.type == aiohttp.WSMsgType.CLOSED:
						self.closed = True
						break
					else:
						checker.mumble(error='get message with unexpected type {}\nmessage: {}'.format(msg.type, msg.data))
		except Exception as ex:
			checker.down(error='something down', exception=ex)
	def want(self, point):
		self.wanted.add(json.dumps(data, sort_keys=True))
	async def finish(self):
		while len(self.wanted) > 0:
			top = await self.queue.get()
			top = json.dumps(top, sort_keys=True)
			if top in self.wanted:
				self.wanted.remove(top)
		self.connection.close()
	async def find(self, id):
		while True:
			if self.queue.empty() and self.closed:
				checker.mumble(error='point not found')
			top = await self.queue.get()
			if top['id'] == id:
				self.connection.close()
				return top

def get_log_info(name, url):
	return '[{:05}] {}: {}'.format(random.randint(0, 99999), name, url)

class State:
	def __init__(self, hostname, port=None, name=''):
		self.hostname = hostname
		self.name = name
		self.port = '' if port is None else ':' + str(port)
		cookie_jar = aiohttp.CookieJar(unsafe=True)
		self.session = aiohttp.ClientSession(
			cookie_jar=cookie_jar,
			headers={
				'Referer': self.get_url(''), 
				'User-Agent': UserAgents.get(),
			})
	def __del__(self):
		self.session.close()
	def get_url(self, path='', proto='http'):
		return '{}://{}{}/{}'.format(proto, self.hostname, self.port, path.lstrip('/'))

	async def get(self, url):
		url = self.get_url(url)
		log_info = get_log_info(self.name, url)
		try:
			checker.log(log_info + ' cookies:' + get_cookie_string(self.session.cookie_jar))
			async with self.session.get(url) as response:
				await check_status(response, log_info)
				text = await response.text()
				checker.log(log_info + ' responsed')
				return text
		except Exception as ex:
			checker.down(error=log_info, exception=ex)

	async def post(self, url, data={}, need_check_status=True):
		url = self.get_url(url)
		log_info = get_log_info(self.name, url)
		try:
			checker.log(log_info + ' cookies:' + get_cookie_string(self.session.cookie_jar))
			async with self.session.post(url, json=data) as response:
				if need_check_status:
					await check_status(response, log_info)
					text = await response.text()
					checker.log(log_info + ' responsed')
					return text
				else:
					return response.status, await response.text()
		except Exception as ex:
			checker.down(error='{}\n{}'.format(log_info, data), exception=ex)

	async def register(self, username=None, password=None):
		can_retry = username is None
		request = {'user': checker.get_value_or_rand_name(username), 'password': checker.get_value_or_rand_string(password, 16)}
		status, text = await self.post('/api/login', request, need_check_status = False)
		if status == 200:
			return request['user'], request['password']
		if 500 > status >= 400 and can_retry:
			while 500 > status >= 400:
				request['user'] = checker.get_rand_string(16)
				request['password'] = checker.get_rand_string(32)
				status, text = await self.post('/api/login', request, need_check_status = False)
			return request['user'], request['password']
		checker.mumble(error='error while login: status {}, response {}'.format(status, text))

	async def login(self, username, password):
		request = {'user': username, 'password': password}
		await self.post('/api/login', request)

	async def get_public_points(self):
		return checker.parse_json(await self.get('/api/publics'))

	async def get_points(self):
		return checker.parse_json(await self.get('/api/points'))

	def get_listener(self, url):
		url = self.get_url(url, proto='ws')
		log_info = get_log_info(self.name, url)
		try:
			checker.log(log_info + ' cookies:' + get_cookie_string(self.session.cookie_jar))
			connection = self.session.ws_connect(url, origin=self.get_url(''))
			checker.log(log_info + ' connected')
		except Exception as ex:
			checker.down(error=log_info, exception=ex)
		helper = WSHelper(connection)
		helper.start()
		return helper

	def get_public_listener(self):
		return self.get_listener('/ws/publics')

	def get_points_listener(self):
		return self.get_listener('/ws/points')

	async def put_point(self, x = None, y = None, message = None, is_public = None, user = None):
		point = {
			'x' : checker.get_value_or_rand_string(x, 13, checker.printable), 
			'y' : checker.get_value_or_rand_string(y, 13, checker.printable), 
			'message' : checker.get_value_or_rand_text(message), 
			'public' : is_public if is_public is not None else random.choice([True, False])}
		point['id'] = await self.post('/api/add', point)
		point['user'] = user
		return point

	async def get_path(self, start, finish, inners):
		response = await self.post('/api/path', {
			'start': start,
			'finish': finish,
			'sub': inners
		})
		return checker.parse_json(response)
