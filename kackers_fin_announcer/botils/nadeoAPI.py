import ast
import requests
import botils.config
import datetime
import jwt
import time

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

def getKrMapUIDFromNumber(nr: int):
    if nr < 0 or nr > botils.config.CFG.BOT["hunting"]["kr_mappack_count"]:
        logger.error(f"{nr} is not in current mappack")
        return ""

    if krMapUids:
        return krMapUids[nr]
    else:
        logger.error("Could not find kr map UIDS")
        return ""

def get_wr(mapNr):
    liveToken = get_Live_API_token()  

    getRecordsUrl = botils.config.CFG.BOT["nadeo_api"]["wr_call"]

    mapUid = getKrMapUIDFromNumber(mapNr)
    if mapUid == "":
        return #error has already been displayed in get uid function
    
    urlReq = getRecordsUrl.replace("{mapUid}", mapUid)
    time.sleep(1) #Preventing rate limiting

    x = requests.get(urlReq, headers={"Authorization": "nadeo_v1 t=" + liveToken})
    time.sleep(1) #Preventing rate limiting

    findata = ast.literal_eval(x.text)["tops"][0]["top"]

    userIds = [findata[0]["accountId"], findata[1]["accountId"]]
    scores = [findata[0]["score"], findata[1]["score"]]

    display_names = get_display_name(userIds)
    usernames = [display_names[userIds[0]], display_names[userIds[1]]]

    return [usernames, scores]

def get_rank(map_uid, score):
    live_token = get_Live_API_token()

    url = botils.config.CFG.BOT["nadeo_api"]["rank_call"]

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
    time.sleep(1) #Preventing rate limiting

    findata = ast.literal_eval(x.text)
    if (x.status_code != 200 or findata == {}):
        print("Error getting rank")
        return -1


    rank = findata[0]["zones"][0]["ranking"]["position"] - 1
    print(f"found rank {rank}")

    return rank

def get_display_name(accountIds):
    url = botils.config.CFG.BOT["nadeo_api"]["display_name_call"]

    oauth_token_ = get_oauth_token()

    urlParams = ""
    for i in range(0, len(accountIds)):
        accountId = accountIds[i]

        if i != 0:
            urlParams += "&"
        urlParams += "accountId[]=" + accountId

    url = url.replace("ACCOUNTS", urlParams)

    logger.info(url)

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {oauth_token_}"}
    
    x = requests.get(url, headers = headers)
    time.sleep(1) #preventing rate limiting

    return ast.literal_eval(x.text)


ticket = None

def get_ticket():
    basic = HTTPBasicAuth(botils.config.CFG.SECRETS["nadeo_username"], botils.config.CFG.SECRETS["nadeo_password"])

    url = url = botils.config.CFG.BOT["nadeo_api"]["ticket_call"]
    headers = {"Content-Type": "application/json", "Ubi-AppId":botils.config.CFG.SECRETS["ubi_app_id"], "User-Agent":botils.config.CFG.SECRETS["user-agent"]}

    x = requests.post(url, headers=headers, auth=basic)
    time.sleep(1) #Preventing rate limiting

    if(x.status_code != 200):
        return -1

    return x.text.split('"')[7]

access_live_token = None
refresh_live_token = None
oauth_token = None

def refresh_live_API_token():
    global access_live_token
    global refresh_live_token

    url = botils.config.CFG.BOT["nadeo_api"]["refresh_live_token_call"]

    headers = {"Content-Type": "application/json", "Authorization": "nadeo_v1 t=" + refresh_live_token, "User-Agent":botils.config.CFG.SECRETS["user-agent"]}
    
    x = requests.post(url, headers = headers)
    time.sleep(1) #Preventing rate limiting

    access_live_token = x.text.split('"')[3]
    refresh_live_token = x.text.split('"')[7]

def get_oauth_token():
    global oauth_token

    if (oauth_token != None and oauth_token["expires"] >= datetime.datetime.now()):
        return oauth_token["access_token"]

    url = botils.config.CFG.BOT["nadeo_api"]["oauth_token_call"]

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    body = {
        "grant_type": "client_credentials",
        "client_id": botils.config.CFG.SECRETS["oauth_identifier"],
        "client_secret": botils.config.CFG.SECRETS["oauth_secret"],
    }
    
    x = requests.post(url, headers = headers, data=body)
    time.sleep(1) #Preventing rate limiting

    token = ast.literal_eval(x.text)
    expires_in = token["expires_in"] - 10 #subtract 10 for buffer
    token["expires"] = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

    oauth_token = token

    return oauth_token["access_token"]

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

    url = botils.config.CFG.BOT["nadeo_api"]["access_live_token_call"]

    headers = {"Content-Type": "application/json", "Authorization": "ubi_v1 t=" + ticket, "User-Agent":botils.config.CFG.SECRETS["user-agent"]}
    body = {"audience": "NadeoLiveServices"}

    x = requests.post(url, headers = headers, json=body)
    time.sleep(1) #Preventing rate limiting

    if(x.status_code != 200):
        return -1
    
    access_live_token = x.text.split('"')[3]
    refresh_live_token = x.text.split('"')[7]

    return access_live_token
