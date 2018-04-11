#!/usr/bin/env python3
from PIL import Image
from PIL import ImageDraw
import struct
import socket

MON_WIDTH = (1366 + 2) // 4
MON_HEIGHT = 768 // 4

MON_ADDRS = [
    ["0.0.0.0", "0.0.0.0", "0.0.0.0", "0.0.0.0"],
    ["0.0.0.0", "0.0.0.0", "0.0.0.0", "0.0.0.0"],
    ["0.0.0.0", "0.0.0.0", "127.0.0.1", "0.0.0.0"],
    ["0.0.0.0", "0.0.0.0", "0.0.0.0", "0.0.0.0"],
]

MON_NUM_X = len(MON_ADDRS[0])
MON_NUM_Y = len(MON_ADDRS)

PORT = 31337

def smart_img_resize(img, tgt_width, tgt_height):
    img = img.copy()
    img.thumbnail((tgt_width, tgt_height), Image.ANTIALIAS)

    full_image = Image.new('RGB', (tgt_width, tgt_height), img.getpixel((0, 0)))

    offset = ((full_image.width - img.width) // 2, (full_image.height - img.height) // 2)
    full_image.paste(img, offset)
    return full_image


def send_image(img, host):
    data = bytearray()

    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x,y)) 
            data += struct.pack("BBB", *pixel)
    s = socket.socket()
    s.connect((host, PORT))
    s.sendall(data)


img = Image.open("облака-1.jpg")
img = smart_img_resize(img, MON_WIDTH * MON_NUM_X, MON_HEIGHT * MON_NUM_Y)

draw = ImageDraw.Draw(img)
draw.text((70, 100),"12345678901234567890123456789012=",(255,0,0))

print(img.width, img.height)

for mon_y in range(MON_NUM_Y):
    for mon_x in range(MON_NUM_X):
        host = MON_ADDRS[mon_y][mon_x]
        if host == "0.0.0.0":
            continue

        print(img.width, img.height, mon_x*MON_WIDTH, mon_y*MON_HEIGHT)
        rect = (mon_x*MON_WIDTH, mon_y*MON_HEIGHT, (mon_x+1)*MON_WIDTH, (mon_y+1)*MON_HEIGHT)
        img_part = img.crop(rect)
        print(img_part.width, img_part.height)

        send_image(img_part, host)


