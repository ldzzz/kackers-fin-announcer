from botils.utils import CFG, build_announce_embed, get_updated_fins
from discord.ext import commands, tasks
import discord
import db.fin_ops as finops
from botils.fetch import fetch_player_fins
from botils.utils import _get_module_logger

logger = _get_module_logger(__name__)


class KFAFin(commands.Cog, name="FinishAnnouncerCog"):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_fins.start()

    def cog_unload(self):
        self.fetch_fins.cancel()

    @tasks.loop(minutes=1)
    async def fetch_fins(self):
        players = finops.get_all_players()
        print(players)
        for username, id in players.items():
            fetched_fins = fetch_player_fins(username)
            db_fins = finops.get_player_fins(username)
            new_fins, pb_fins = get_updated_fins(fetched_fins, db_fins)
            print("new fins", new_fins)
            print("pb fins", pb_fins)
            # update database
            ret1 = finops.create_fins(id, new_fins)
            ret2 = finops.update_fins(id, pb_fins)
            # hopefully this will never be executed
            if not (ret1 and ret2):
                logger.error(
                    f"Couldnt update some finishes for {username}. NEW FINS: {ret1}, PBS: {ret2}"
                )
                s = (
                    f"DINKDONK bot finna fucking up. Djinn trash developer. Go fix.\n"
                    f"Some new fins or PBs weren't updated for **{username}**\n"
                    f"NEW: {new_fins}\n"
                    f"PB: {pb_fins}"
                )
                await self.bot.get_channel(self.bot.channel_id).send(s)
            # report finishes anyway
            player_data = (username, len(fetched_fins))
            for fin in new_fins:
                await self.bot.get_channel(self.bot.channel_id).send(
                    embed=build_announce_embed(player_data, fin)
                )
            for fin in pb_fins:
                await self.bot.get_channel(self.bot.channel_id).send(
                    embed=build_announce_embed(player_data, fin[::-1])
                )

    @fetch_fins.before_loop
    async def fetcher_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(KFAFin(bot))
