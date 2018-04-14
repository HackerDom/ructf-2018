from urllib.request import urlopen, Request
from urllib.parse import quote, urlencode
from json import loads, dumps
import socket


class Api:
    def __init__(self, team_addr):
        self.team_addr = team_addr

    def __make_request_obj(self, method, data="", query_string=""):
        api = "http://hologram.{}/api/holograms"
        return Request(
            url=api.format(self.team_addr),
            method=method
        )

    def __run_request(self, request):
        try:
            urlopen(request, timeout=3)
        except socket.timeout:
            try:
                urlopen(request, timeout=3)
            except socket.timeout:
                raise Exception("") #fixit

    def create_hologram(self, x, y, z, name, body):
        holo_data = {
            "x": x,
            "y": y,
            "z": z,
            "name": name,
            "body": body
        }




class Methods:
    POST = "POST"
    GET = "GET"
