from pathlib import Path
import json
import discord
import namedtupled


def _load_config():
    global CFG
    with open(Path.cwd() / "config.json", "r") as fp:
        data = json.load(fp)
        CFG = namedtupled.map(data, "CFG")
        print(CFG)


# TODO: build db of thumbnails - urls?? or dl to local files ?? - worse prob for me
def build_announce_embed(fin_data, rank) -> discord.Embed:
    fin_embed = discord.Embed(
        title=":heart_eyes: NEW FINISH :heart_eyes:",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        color=discord.Color.random(),
    )
    fin_embed.set_thumbnail(
        url="https://kackyreloaded.com/cache/tracks/thumbnails/e1FSUJRB63Q8u7u4DMz1FJJuGyj.jpg"
    )
    fin_embed.set
    fin_embed.add_field(name="Player", value="djinner", inline=False)
    fin_embed.add_field(name="Map", value="#2888", inline=True)
    fin_embed.add_field(name="Rank", value="1", inline=True)
    fin_embed.add_field(name="Total fins", value="225/225", inline=False)
    fin_embed.set_footer(text=f"Bot by djinn")
    return fin_embed
