import ast
import requests
import botils.config
import datetime
import jwt

from botils.load_config_logger import get_module_logger
from requests.auth import HTTPBasicAuth

logger = get_module_logger(__name__)

def get_KR_map_Ids():
    logger.info("Parsing kr map Ids")

    file = open(botils.config.CFG.SECRETS["kr_map_ids"])
    krMapUIDs = file.readline().split("\\n")

    return krMapUIDs

krMapUids = get_KR_map_Ids()

def validate_token(token):
    try:
        decoded_payload = jwt.decode(token, options={"verify_signature": False})
        
        exp_timestamp = decoded_payload.get('exp')
        
        if exp_timestamp:
            # Convert timestamp to a readable UTC datetime
            expire_date = datetime.datetime.fromtimestamp(exp_timestamp, tz=datetime.timezone.utc)
            buffer_time = datetime.timedelta(minutes=1)

            expire_date -= buffer_time

            current_date = datetime.datetime.now(tz=datetime.timezone.utc)
            
            return current_date <= expire_date

        else:
            print("The token does not contain an 'exp' field.")
            return False

    except jwt.DecodeError:
        print("Error: Invalid token format.")
        return False

def isReloaded(uid):
    return uid in krMapUids

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

access_live_token = None
refresh_live_token = None

def refresh_live_API_token():
    global access_live_token
    global refresh_live_token

    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/refresh"

    headers = {"Content-Type": "application/json", "Authorization": "nadeo_v1 t=" + refresh_live_token, "User-Agent":"ThijsvanB"}
    
    x = requests.post(url, headers = headers)

    access_live_token = x.text.split('"')[3]
    refresh_live_token = x.text.split('"')[7]

def get_Live_API_token():
    global access_live_token
    global refresh_live_token

    #check if token is still valid
    if validate_token(access_live_token):
        return access_live_token
    
    #check if refresh token is still valid
    if validate_token(refresh_live_token):
        return access_live_token

    #do the big refresh
    ticket = get_ticket()

    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices"

    headers = {"Content-Type": "application/json", "Authorization": "ubi_v1 t=" + ticket, "User-Agent":"ThijsvanB"}
    body = {"audience": "NadeoLiveServices"}

    x = requests.post(url, headers = headers, json=body)

    if(x.status_code != 200):
        return -1
    
    access_live_token = x.text.split('"')[3]
    refresh_live_token = x.text.split('"')[7]

    return access_live_token
