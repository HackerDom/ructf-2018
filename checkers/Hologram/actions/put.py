from actions.utils import get_random_cords, get_random_body, get_random_header
from holograms_api import Api, ApiException
from actions import MUMBLE, DOWN, OK
from urllib.error import HTTPError, URLError
import traceback


def put(team_addr, _, flag, vuln):
    x, y, z = get_random_cords()
    head = get_random_header()
    body = get_random_body() + "\n" + flag
    try:
        api = Api(team_addr)
        result = api.create_hologram(x, y, z, head, body)
    except ApiException as e:
        return {"code": MUMBLE, "private": traceback.format_exc()}
    except (HTTPError, URLError) as e:
        return {"code": DOWN, "private": traceback.format_exc()}
    return {"code": OK, "flag_id": result["id"]}
