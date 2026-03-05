import random
import botils.shelfer as std
from botils.player_stats import get_kr_missing

async def sendMessage(channel):
    print("April fools LO")

    data = std.get_all_data()
    if len(data.keys()) == 0:
        return
    
    player = random.choice(list(data.keys()))
    missing = get_kr_missing(data[player])

    print(f"Fooling {player}")

    while(len(missing) == 0):
        player = random.choice(list(data.keys()))
        print(f"Fooling {player}")
        missing = get_kr_missing(data[player])

    difficultiesFile = open("C:/Users/20223626/OneDrive - TU Eindhoven/Documents/Programming(SELF)/kackers-fin-announcer/data/difficultyList.txt")
    difficulties = difficultiesFile.readlines()
    easiestMissing = ""
    for i in range(0, 450):
        mapNr = int(difficulties[i].split('Â\xa0')[0])
        if mapNr in missing:
            easiestMissing = difficulties[i]
            break

    await channel.send(f"{player} is still missing {easiestMissing} LOL")

