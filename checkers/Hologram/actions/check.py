from actions.utils import get_random_body, get_random_header, get_random_cords
from holograms_api import Api, ApiException
from ws_helper import run_ws, create_ws_addr
from random import randint
from json import loads
from actions import MUMBLE, DOWN, OK
from urllib.error import HTTPError, URLError
import traceback


def check(team_addr):
    try:
        x, y, z = get_random_cords()
        ## debug only
        #api_team_addr = team_addr.split(":")[0] + ":8080"
        #api = Api(api_team_addr)
        ## debug only
        api = Api(team_addr)
        created_holos_ids = {api.create_hologram(x, y, z, get_random_header(), get_random_body())["id"]}
        messages = run_ws(
            create_ws_addr(team_addr, *randomize_coords(x, y, z, 2), randint(17, 20)),
            lambda: create_hologram_at(x, y, z, api, created_holos_ids)
        )
        results = set()
        for message in messages:
            try:
                msg_obj = loads(message)
                results.add(msg_obj["id"])
            except Exception:
                pass

        if created_holos_ids.issubset(results):
            return {"code": OK}
        return {"code": MUMBLE, "private": "{} is not subset of {}".format(created_holos_ids, results)}

    except (ApiException, TypeError) as e:
        return {"code": MUMBLE, "private": traceback.format_exc()}
    except (HTTPError, URLError) as e:
        return {"code": DOWN, "private": traceback.format_exc()}


def randomize_coords(x, y, z, en):
    en = abs(en)
    return x + randint(-en, en), y + randint(-en, en), z + randint(-en, en)


def create_hologram_at(x, y, z, api, link_to_holo):
    result = api.create_hologram(*randomize_coords(x, y, z, 2), get_random_header(), get_random_body())["id"]
    link_to_holo.add(result)