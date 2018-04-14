from urllib.request import urlopen, Request
from urllib.parse import urlencode
from json import loads, dumps
from user_agents import get as get_user_agent
import socket


class Api:
    def __init__(self, team_addr, timeout_per_request=3):
        self.team_addr = team_addr
        self.timeout = timeout_per_request

    def __make_request_obj(self, method, data="", query_string=None):
        api = "http://{}/api/holograms"
        if query_string is not None:
            api += "?{}".format(urlencode(query_string))
        request = Request(
            url=api.format(self.team_addr),
            method=method,
            data=data.encode()
        )
        request.add_header('User-Agent', get_user_agent())
        return request

    def __run_request(self, request):
        try:
            return urlopen(request, timeout=self.timeout)\
                .read()\
                .decode()
        except socket.timeout:
            try:
                return urlopen(request, timeout=self.timeout)\
                    .read()\
                    .decode()
            except socket.timeout:
                raise ApiException("Service timed out!")

    def create_hologram(self, x, y, z, name, body):
        hologram_data = {
            "x": x,
            "y": y,
            "z": z,
            "name": name,
            "body": body
        }
        request_obj = self.__make_request_obj(Methods.POST, dumps(hologram_data))
        response = self.__run_request(request_obj)
        return loads(response)

    def get_hologram(self, id):
        request_obj = self.__make_request_obj(Methods.GET, query_string={"id": id})
        response = self.__run_request(request_obj)
        return loads(response)


class Methods:
    POST = "POST"
    GET = "GET"


class ApiException(Exception):
    pass
