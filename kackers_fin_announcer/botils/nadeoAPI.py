import ast

import requests
import botils
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
"""
TODO: also needs updating
def get_ticket():
    basic = HTTPBasicAuth(CFG.nadeo_username, CFG.nadeo_pw)

    url = "https://public-ubiservices.ubi.com/v3/profiles/sessions"
    headers = {"Content-Type": "application/json", "Ubi-AppId":"86263886-327a-4328-ac69-527f0d20a237", "User-Agent":"ThijsvanB"}

    x = requests.post(url, headers=headers, auth=basic)

    print("Request ticket: ", x)

    if(x.status_code != 200):
        return -1

    return x.text.split('"')[7]

def get_Live_API_token(ticket):
    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices"

    headers = {"Content-Type": "application/json", "Authorization": "ubi_v1 t=" + ticket, "User-Agent":"ThijsvanB"}
    body = {"audience": "NadeoLiveServices"}

    x = requests.post(url, headers = headers, json=body)

    print("Request live token: ", x)

    if(x.status_code != 200):
        return -1

    return [x.text.split('"')[3], x.text.split('"')[7]]

def get_top_two(mapNr):
    ticket = get_ticket()
    if ticket == -1:
        print("Ticket failed, returning -1")
        return [-1, -1]

    liveToken = get_Live_API_token(ticket)  

    if liveToken == -1:
        print("LiveToken failed, returning -1")
        return [-1, -1]

    file = open(CFG.map_ids)
    maps = file.readline().split("\\n")

    getRecordsUrl = "https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/Personal_Best/map/{mapUid}/top?length=2&onlyWorld=true&offset=0"

    print(mapNr, type(mapNr))
    urlReq = getRecordsUrl.replace("{mapUid}", maps[int(mapNr) - 1])
    print(urlReq)

    x = requests.get(urlReq, headers={"Authorization": "nadeo_v1 t=" + liveToken[0]})
    print("Request records:", x)
    findata = ast.literal_eval(x.text)
    return [findata["tops"][0]["top"][0]["score"], findata["tops"][0]["top"][1]["score"]]
"""