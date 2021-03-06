import requests
import struct
import random
import sys
import re
from time import sleep
from io import BytesIO
import user_agents

KEY_SIZE = 128

class ApiError(Exception):
	def __init__(self, message, method):
		super().__init__("{} failed. {}".format(method, message))

class UnexpectedStatusError(ApiError):
	pass

class BadResponseError(ApiError):
	pass		
		
class Channel:
	def __init__(self, name, posts):
		self.name = name
		self.posts = posts

	def decrypt(self, key):
		self.posts = [self._decrypt_post(post, key) for post in self.posts]

	def _decrypt_post(self, post, key):
		return bytes(post[i] ^ key[i % len(key)] for i in range(len(post)))
	
	@staticmethod
	def parse(serialized):
		bytesio = BytesIO(serialized)
		name = _read_string(bytesio)
		posts = []
		while bytesio.tell() != len(serialized):
			posts.append(_read_string(bytesio))
		return Channel(name, posts)

	
def _read_string(bytesio):
	size = _read_size_t(bytesio)
	data = _read_exactly(bytesio, size)
	return data

def _read_size_t(bytesio):
	return struct.unpack("<q", _read_exactly(bytesio, 8))[0]

def _read_exactly(bytesio, count):
	data = bytesio.read(count)
	if len(data) != count:
		raise EOFError()
	return data


class Ribbons:
	def __init__(self, hostname):
		self.hostname = hostname
		self._session = None

	@property
	def session(self):
		if not self._session:
			self._session = requests.session()
			self._session.headers = {"User-Agent": user_agents.get()}
		return self._session

	def _call(self, http_method, api_method, channel_id=None, data=None):
		params = { "channel_id": channel_id } if channel_id else {}
		sleep(random.randint(0, 1) + random.random())
		result = self.session.request(http_method, "http://{}:4243/api/{}".format(self.hostname, api_method), params=params, data=data)
		if random.randint(1, 3) == 1:
			self._session.close()
			self._session = None
		return result

	def _assert_status(self, response, status, api_method):
		if response.status_code != status:
			raise ApiError("Unexpected status: {}".format(response.status_code), api_method)

	def add_channel(self, name, password):
		method = "add_channel"
		response = self._call("POST", method, data={ "name": name, "password": password })
		self._assert_status(response, 201, method)
		match = re.fullmatch("id:(\d+)", response.text)
		if not match:
			raise BadResponseError("Id not found. Received: '{}'".format(response.text), method)
		return match.group(1)

	def add_post(self, channel_id, password, text):
		response = self._call("POST", "add_post", channel_id, { "password": password, "text": text })
		self._assert_status(response, 201, "add_post")
		return True

	def get_key(self, channel_id, password):
		response = self._call("POST", "key", channel_id, data={ "password": password })
		method = "get_key"
		self._assert_status(response, 200, method)
		received_key_size = len(response.content)
		if received_key_size != KEY_SIZE:
			raise BadResponseError("Key size ({}) do not match expected size ({}). Received key: '{}'".format(received_key_size, KEY_SIZE, response.content), method)
		return response.content

	def change_password(self, channel_id, password, new_password):
		response = self._call("POST", "change_password", channel_id, data={ "password": password, "new_password": new_password })
		self._assert_status(response, 200, "change_password")
		return True

	def view(self, channel_id):
		response = self._call("GET", "view", channel_id)
		self._assert_status(response, 200, "view")
		try:
			channel = Channel.parse(response.content)
		except EOFError as e:
			raise BadResponseError("Channel parsing failed. Received: '{}'".format(response.content), "view") from e
		return channel
