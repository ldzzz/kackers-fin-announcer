import ast

import requests
import botils.config
from botils.load_config_logger import get_module_logger
from requests.auth import HTTPBasicAuth

logger = get_module_logger(__name__)

def get_KR_map_Ids():
    logger.info("Parsing kr map Ids")

    file = open(botils.config.CFG.SECRETS['kr_map_ids'])
    krMapUIDs = file.readline().split("\\n")

    return krMapUIDs


krMapUids = get_KR_map_Ids()

def isReloaded(uid):
    return uid in krMapUids

def get_top_two(mapNr):
    pass

def get_rank(map_uid, score):
    live_token = get_Live_API_token()

    url = "https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/map"

    params = {
        f"scores[{map_uid}]": score
    }

    payload = {
        "maps": [
        {
            "mapUid": f"{map_uid}",
            "groupUid": "Personal_Best"
        }] 
    }

    headers = {
        "Authorization": "nadeo_v1 t=" + live_token,
        "Content-Type": "application/json"
    }

    x = requests.post(url, headers=headers, params=params, json=payload)
    findata = ast.literal_eval(x.text)
    if (x.status_code != 200 or findata == {}):
        print("Error getting rank")
        return -1


    rank = findata[0]["zones"][0]["ranking"]["position"] - 1
    print(f"found rank {rank}")

    return rank

ticket = None

def get_ticket():
    basic = HTTPBasicAuth(botils.config.CFG.SECRETS["nadeo_username"], botils.config.CFG.SECRETS["nadeo_password"])

    url = "https://public-ubiservices.ubi.com/v3/profiles/sessions"
    headers = {"Content-Type": "application/json", "Ubi-AppId":botils.config.CFG.SECRETS["ubi_app_id"], "User-Agent":"ThijsvanB"}

    x = requests.post(url, headers=headers, auth=basic)

    print("Request ticket: ", x)

    if(x.status_code != 200):
        return -1

    return x.text.split('"')[7]

live_token = None

def get_Live_API_token():
    ticket = get_ticket()

    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices"

    headers = {"Content-Type": "application/json", "Authorization": "ubi_v1 t=" + ticket, "User-Agent":"ThijsvanB"}
    body = {"audience": "NadeoLiveServices"}

    x = requests.post(url, headers = headers, json=body)

    print("Request live token: ", x)

    if(x.status_code != 200):
        return -1
    
    live_token = x.text.split('"')[3]

    print(live_token)

    return live_token