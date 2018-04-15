#!/usr/bin/env python3

import sys
import checker_api
import random
import json
import requests
import base64
import string
from ribbons_api import Ribbons, ApiError

MAX_POSTS = 3

def get_rand_string(l):
	return ''.join(random.choice(string.ascii_lowercase) for _ in range(l))

def get_channel_name():
	return get_rand_string(random.randint(10, 15))

def get_password():
	return get_rand_string(random.randint(10, 14))

def get_post():
	return get_rand_string(random.randint(30, 120)).encode()

def handle_check(hostname):
	ribbons = Ribbons(hostname)

	name = get_channel_name()
	password = get_password()

	cid = ribbons.add_channel(name, password)

	posts = [get_post() for _ in range(random.randint(0, MAX_POSTS))]

	for post in posts:
		ribbons.add_post(cid, password, post)

	new_password = get_password()
	ribbons.change_password(cid, password, new_password)
	password = new_password

	key = ribbons.get_key(cid, password)

	channel = ribbons.view(cid)
	received_posts = channel.posts.copy()
	channel.decrypt(key)
	if channel.posts != posts:
		raise BadResponseError("Posts don't match: expected {}, actual {}. Received key: {}, received posts: {}".format(posts, channel.posts, key, received_posts))

	checker_api.ok()

def handle_put(hostname, id, flag):
	ribbons = Ribbons(hostname)

	name = get_channel_name()
	password = get_password()

	cid = ribbons.add_channel(name, password)

	key = ribbons.get_key(cid, password)

	posts = [get_post() for _ in range(random.randint(0, MAX_POSTS - 1))] + [flag]
	random.shuffle(posts)

	for post in posts:
		ribbons.add_post(cid, password, post)

	credentials = {
		"channel_id": cid,
		"password": password,
		"key": key.decode("latin-1")
	}

	checker_api.ok(message=base64.b64encode(json.dumps(credentials).encode()).decode())

def handle_get(hostname, id, flag):
	ribbons = Ribbons(hostname)
	credentials = json.loads(base64.b64decode(id).decode())
	
	channel = ribbons.view(credentials["channel_id"])
	channel.decrypt(credentials["key"].encode("latin-1"))

	if flag.encode() not in channel.posts:
		checker_api.corrupt(error='Flag not found. Posts count: {}'.format(len(channel.posts)))
	else:
		checker_api.ok()


def main():
	checker = checker_api.Checker(handle_check, [(handle_put, handle_get)])
	try:
		checker.process(sys.argv)
	except ApiError as e:
		checker_api.mumble(error=str(e), exception=e.__context__)
	except requests.RequestException as e:
		checker_api.down(exception=e)

if __name__ == "__main__":
	main()
