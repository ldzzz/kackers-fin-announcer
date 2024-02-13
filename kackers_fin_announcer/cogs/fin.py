import botils.shelfer as std
from botils.fetch import fetch_player_finishes
from botils.utils import (
    CFG,
    _get_module_logger,
    build_announce_embed,
    get_latest_finishes,
)
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
        players = std.get_all_data()
        for player, fins in players.items():
            fetched_fins = fetch_player_finishes(player)
            # skip if Kacky-API failed at any point
            if not fetched_fins:
                logger.error(f"This doesnt look right:\n{player}: old_cnt={len(fins.keys())}, new_cnt={len(fetched_fins.keys())} -> Skipping")
                continue
            nfpb = get_latest_finishes(fins, fetched_fins)
            # self-correct if writing to file failed at any point
            if len(fetched_fins.keys()) // 2 > len(fins.keys()):
                logger.error(f"This doesnt look right:\n{player}: old_cnt={len(fins.keys())}, new_cnt={len(fetched_fins.keys())} -> Self-correcting")
                nfpb = []
            for fin in nfpb:
                await self.bot.get_channel(self.bot.channel.id).send(
                            embed=build_announce_embed(
                                {"username": player, "fincount": len(fetched_fins)}, fin
                            )
                        )
            std.add_or_update_player(player, fetched_fins)
        logger.info("Done fetching all players")

    @fetch_finishes.before_loop
    async def fetcher_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(KFAFin(bot))
