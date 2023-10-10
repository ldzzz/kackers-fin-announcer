import db.fin_ops as finops
from botils.fetch import fetch_player_finishes
from botils.utils import CFG, _get_module_logger, build_announce_embed
from discord.ext import commands, tasks

logger = _get_module_logger(__name__)


class KFAFin(commands.Cog, name="FinishAnnouncerCog"):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_finishes.start()

    def cog_unload(self):
        self.fetch_finishes.cancel()

    @tasks.loop(seconds=CFG.interval)
    async def fetch_finishes(self):
        players = finops.get_all_players()
        logger.info(players)
        for player in players:
            fetched_fins = fetch_player_finishes(player["username"])
            if fetched_fins:
                finops.update_or_create_finishes(player["id"], fetched_fins)
                player["fincount"] = finops.get_player_finish_count(player["id"])
                latest_fins = finops.get_latest_finishes(player["id"])
                for fin in latest_fins:
                    await self.bot.get_channel(self.bot.channel.id).send(
                        embed=build_announce_embed(player, fin)
                    )
        logger.info("Done fetching all players")

    @fetch_finishes.before_loop
    async def fetcher_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(KFAFin(bot))
