import requests
from requests.auth import HTTPBasicAuth
import ast

from botils.load_config_logger import CFG, _get_module_logger

def get_ticket():
    basic = HTTPBasicAuth(CFG.nadeo_username, CFG.nadeo_pw)

    url = "https://public-ubiservices.ubi.com/v3/profiles/sessions"
    headers = {"Content-Type": "application/json", "Ubi-AppId":"86263886-327a-4328-ac69-527f0d20a237", "User-Agent":"ThijsvanB"}

    x = requests.post(url, headers=headers, auth=basic)

    print("Request ticket: ", x)
    return x.text.split('"')[7]

def get_Live_API_token(ticket):
    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices"

    headers = {"Content-Type": "application/json", "Authorization": "ubi_v1 t=" + ticket, "User-Agent":"ThijsvanB"}
    body = {"audience": "NadeoLiveServices"}

    x = requests.post(url, headers = headers, json=body)

    print("Request live token: ", x)
    return [x.text.split('"')[3], x.text.split('"')[7]]

def get_top_two(mapNr):
    ticket = get_ticket()
    liveToken = get_Live_API_token(ticket)  

    file = open(CFG.map_ids)
    maps = file.readline().split("\n")
    print(maps)

    getRecordsUrl = "https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/Personal_Best/map/{mapUid}/top?length=2&onlyWorld=true&offset=0"

    urlReq = getRecordsUrl.replace("{mapUid}", maps[mapNr - 1])

    x = requests.get(urlReq, headers={"Authorization": "nadeo_v1 t=" + liveToken[0]})
    print("Request records:", x)
    findata = ast.literal_eval(x.text)
    return [findata["tops"][0]["top"][0]["score"], findata["tops"][0]["top"][1]["score"]]