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
import time

PORT = 8084

async def register_and_put(state):
	username, _ = await state.register()
	data = checker.get_rand_string(32)
	await state.put_data(data)
	return username, data

async def check_in_self_list(state, data):
	datas = await state.get_my()
	return data in datas

def splitBits(data):
	if len(data) % 2 == 1:
		data += '\0'
	l = ''
	r = ''
	for k in range(0, len(data), 2):
		for j in [0, 1]:
			ch = ord(data[k + j])
			for i in range(0, 8, 2):
				l += '0' if ch % 2 == 0 else '1'
				ch //= 2
				r += '0' if ch % 2 == 0 else '1'
				ch //= 2
	return l, r
			
def unpack(d):
	res = ''
	for c in d.encode(encoding='cp1251'):
		m = 256
		for i in range(7, -1, -1):
			m //= 2
			res += '0' if (c & m) == 0 else '1'
	return res

def splitsCount(d, l, r):
	if len(d) == 0:
		return 0;
	inf = int(1e9)

	dp = [[inf, inf] for i in range(len(d))]
	if d[0] == l[0]:
		dp[0][0] = 0
	if d[0] == r[0]:
		dp[0][1] = 0

	for i in range(1, len(d)):
		if d[i] == l[i]:
			dp[i][0] = min(dp[i - 1][0], dp[i - 1][1] + 1)
		if d[i] == r[i]:
			dp[i][1] = min(dp[i - 1][0] + 1, dp[i - 1][1])

	return min(dp[-1])

async def check_in_anothers_list(state, user, data):
	datasTask =  state.get_data(user)
	l, r = splitBits(data)
	datas = await datasTask

	for d in datas:
		dd = unpack(d)
		if len(l) == len(dd) and splitsCount(dd, l, r) <= 2:
			return True
	return False

async def check_in_user_list(state, username):
	users = await state.get_users()
	return username in users

async def handler_check(hostname):

	first = State(hostname, PORT, 'first')
	fregister_and_put = register_and_put(first)

	second = State(hostname, PORT, 'second')
	sregister = second.register()

	fregister_and_put_result, _ = await asyncio.gather(asyncio.ensure_future(fregister_and_put), asyncio.ensure_future(sregister))

	fusername, fdata = fregister_and_put_result

	while True:
		time.sleep(1)
		fcheckTask = check_in_self_list(first, fdata)
		scheckTask = check_in_anothers_list(second, fusername, fdata)
		suser_check_task = check_in_user_list(second, fusername)
		
		(fcheck, scheck, suser_check) = await asyncio.gather(asyncio.ensure_future(fcheckTask), asyncio.ensure_future(scheckTask), asyncio.ensure_future(suser_check_task))
		
		if not scheck:
			checker.log("no suitable data in another user's list")
			continue
		
		if not fcheck:
			checker.log("posted data not present in list of owner")
			continue
		
		if not suser_check:
			checker.log("no user in list")
			continue

		break

	checker.ok()

async def handler_get(hostname, id, flag):
	id = json.loads(id)
	getter = State(hostname, PORT, 'get', id['user'], id['pass'])
	if not await check_in_self_list(getter, flag):
		checker.corrupt()
	checker.ok()

async def handler_put(hostname, id, flag):
	putter = State(hostname, PORT, 'put')
	username, password = await putter.register()
	await putter.put_data(flag)
	checker.ok(message=json.dumps({'user': username, 'pass': password}))

def main():
	checker = Checker(handler_check, [(handler_put, handler_get)])
	checker.process(sys.argv)

if __name__ == "__main__":
	main()
