#!/usr/bin/env python3

import sys
from checker import Checker
import checker
from networking import State
import random
import json
import time
import asyncio
import string

PORT = 7483

def check_points_list(l, expected=[]):
	if not type(l) is list:
		checker.mumble(error='list of points not a list, {}'.format(type(l)))
	error = []
	for i in range(len(l)):
		if not type(l[i]) is dict:
			checker.mumble(error='point #{} is not a dict, {}'.format(i, type(l[i])))
		for field in expected:
			if field not in l[i]:
				error.append(field)
		if len(error) > 0:
			checker.mumble(error='not all expected fields have founded in point #{}. {}'.format(i, str(errors)))

def get_point(points, id):
	for p in points:
		if p['id'] == id:
			return p

def compare(p1, p2, fields):
	error = []
	for f in fields:
		if p1[f] != p2[f]:
			error.append(f)
	if len(error) > 0:
		checker.mumble(error='points are different in fields {}: {} vs {}'.format(error, p1, p2))

async def get_point_with_flag(hostname, username, password, id):
	state = State(hostname, PORT)
	await state.login(username, password)
	listener = state.get_points_listener()
	point = await listener.find(id)
	return point
		
FIELDS = ['id', 'x', 'y', 'message', 'public', 'user']

async def check_one(username, sender, viewer, is_public):
	point = await sender.put_point(is_public=True, user=username)
	p = await viewer.find(point['id'])
	compare(point, p, FIELDS)

def get_rand_point():
	return {
			'x' : checker.get_rand_string(13, checker.printable),
			'y' : checker.get_rand_string(13, checker.printable)
	}

def equal_points(p1, p2):
	return p1['x'] == p2['x'] and p1['y'] == p2['y']

def is_between_str(l, r, p):
	return l <= p <= r or l >= p >= r

def is_between(l, r, p):
	return l['x'] == p['x'] == r['x'] and is_between_str(l['y'], r['y'], p['y']) or l['y'] == p['y'] == r['y'] and is_between_str(l['x'], r['x'], p['x'])

async def check_path(username, sender, another, aname):
	responses = []
	for i in range(random.randint(1, 3)):
		responses.append(await sender.put_point(user=username))
	for i in range(random.randint(1, 3)):
		responses.append(await another.put_point(is_public=True, user=aname))

	start = get_rand_point()
	finish = get_rand_point()

	ids = [point['id'] for point in responses]

	path = await sender.get_path(start, finish, ids)
	check_points_list(path, ['x', 'y'])
	if len(path) == 0:
		checker.mumble(error='path must contains at least one point')
	if not equal_points(path[0], start):
		checker.mumble(error='start point is bad: {} vs {}'.format(start, path[0]))
	if not equal_points(path[-1], finish):
		checker.mumble(error='finish point is bad: {} vs {}'.format(finish, path[-1]))

	for p in responses:
		for i in range(1, len(path)):
			if is_between(path[i - 1], path[i], p):
				break
		else:
			checker.mumble(error='point {} not in path {}'.format(p, path))


async def handler_check(hostname):

	first = State(hostname, PORT, 'first')
	fusername, fpassword = await first.register()
	point_listener = first.get_points_listener()

	second = State(hostname, PORT, 'second')
	suser, spass = await second.register()
	public_listener = second.get_public_listener()

	tasks = []

	tasks.append(asyncio.ensure_future(check_one(fusername, first, public_listener, True)))
	tasks.append(asyncio.ensure_future(check_one(fusername, first, point_listener, False)))
	tasks.append(asyncio.ensure_future(check_path(fusername, first, second, suser)))
	await asyncio.gather(*tasks)

	checker.ok()

async def handler_get(hostname, id, flag):
	id = json.loads(id)
	if 'type' not in id or id['type'] == 1:
		await handler_get_1(hostname, id, flag)
	else:
		await handler_get_2(hostname, id, flag)

async def handler_get_1(hostname, id, flag):
	p = await get_point_with_flag(hostname, id['username'], id['password'], id['id'])
	if p['message'] != flag:
		checker.corrupt(message="Bad flag: expected {}, found {}".format(flag, p['message']))
	checker.ok()

async def handler_put(hostname, id, flag):
	t = random.randint(1, 2)
	if t == 1:
		id = await handler_put_1(hostname, id, flag)
	else:
		id = await handler_put_2(hostname, id, flag)
	id['type'] = t
	checker.ok(message=json.dumps(id))

async def handler_put_1(hostname, id, flag):
	state = State(hostname, PORT)
	username, password = await state.register()
	point = await state.put_point(message=flag, is_public=False)
	await state.put_point(is_public=True)
	return {'username': username, 'password': password, 'id': point['id']}

async def handler_get_2(hostname, id, flag):
	p = await get_point_with_flag(hostname, id['username'], id['password'], id['id'])
	if p['x'] + p['y'] != flag:
		checker.corrupt(message="Bad flag: expected {}, found {}".format(flag, p['message']))
	checker.ok()

async def handler_put_2(hostname, id, flag):
	state = State(hostname, PORT)
	username, password = await state.register()
	point = await state.put_point(x = flag[:len(flag) // 2], y = flag[len(flag) // 2:], is_public=False)
	await state.put_point(is_public=True)
	return {'username': username, 'password': password, 'id': point['id']}

def main():
	checker = Checker(handler_check, [(handler_put, handler_get)])
	checker.process(sys.argv)

if __name__ == "__main__":
	main()
