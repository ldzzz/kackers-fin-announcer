import random
import botils.shelfer as std
from botils.player_stats import get_kr_missing
from botils.utils import parse_ts

async def sendMessage(channel):
    print("April fools LO")

    data = std.get_all_data()
    if len(data.keys()) == 0:
        return
    
    player = random.choice(list(data.keys()))
    missing = get_kr_missing(data[player])

    print(f"Fooling {player}")

    index = 0
    while(len(missing) == 0):
        player = random.choice(list(data.keys()))
        print(f"Fooling {player}")
        missing = get_kr_missing(data[player])
        index += 1

        if (index > 100):
            return
        
    data[player]['kr_finishes'].sort(key = lambda x: x["createdAt"])

    difficultiesFile = open("C:/Users/20223626/OneDrive - TU Eindhoven/Documents/Programming(SELF)/kackers-fin-announcer/data/difficultyList.txt")
    difficulties = difficultiesFile.readlines()
    easiestMissing = ""
    for i in range(0, 450):
        mapNr = int(difficulties[i].split('Â\xa0')[0])
        if mapNr in missing:
            easiestMissing = difficulties[i]
            break

    responsesList = [
        f"Did u know, {player} is still missing {easiestMissing}",
        f"KEKL {player} is still missing {easiestMissing}",
        f"{player} is only on {len(data[player]['kr_finishes'])} finishes, laugh at them",
        f"{player} has not finished anything since {parse_ts(data[player]['kr_finishes'][len(data[player]['kr_finishes']) - 1]['createdAt'])}"
    ]

    await channel.send(random.choice(responsesList))

