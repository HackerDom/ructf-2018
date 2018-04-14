from holograms_api import Api, ApiException
from actions import MUMBLE, DOWN, OK, CORRUPT
from urllib.error import HTTPError, URLError
import traceback
from ws_helper import run_ws, create_ws_addr
import json


def get(team_addr, flag_id, flag, _):
    try:
        api = Api(team_addr)
        ## debug only
        #api_team_addr = team_addr.split(":")[0] + ":8080"
        #api = Api(api_team_addr)
        ## debug only
        result = api.get_hologram(flag_id)
        x, y, z = result["x"], result["y"], result["z"]
        guid = result["id"]
        expected_flag = result["body"].split()[-1]
        messages = run_ws(create_ws_addr(team_addr, x, y, z, 3), delegate)
        if expected_flag == flag and \
                any(
                    (message["id"] == guid and message["body"].split()[-1] == expected_flag)
                    for message in (json.loads(msg) for msg in messages)
                ):
            return {"code": OK}
        else:
            return {"code": CORRUPT}
    except (ApiException, KeyError, IndexError, TypeError) as e:
        return {"code": MUMBLE, "private": traceback.format_exc()}
    except (HTTPError, URLError) as e:
        return {"code": DOWN, "private": traceback.format_exc()}


def delegate():
    pass
