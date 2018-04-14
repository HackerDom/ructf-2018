from holograms_api import Api, ApiException
from actions import MUMBLE, DOWN, OK, CORRUPT
from urllib.error import HTTPError, URLError
import traceback


def get(team_addr, flag_id, flag, vuln):
    try:
        api = Api(team_addr)
        result = api.get_hologram(flag_id)
        if result["body"].split()[-1] == flag:
            return {"code": OK}
        else:
            return {"code": CORRUPT}
    except (ApiException, KeyError, IndexError) as e:
        return {"code": MUMBLE, "private": traceback.format_exc()}
    except (HTTPError, URLError) as e:
        return {"code": DOWN, "private": traceback.format_exc()}
