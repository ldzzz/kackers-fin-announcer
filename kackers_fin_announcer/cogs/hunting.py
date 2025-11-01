import botils.config
import botils.shelfer as std
from botils.fetch import fetch_player_finishes
from botils.load_config_logger import get_module_logger
from botils.nadeoAPI import get_top_two
from botils.utils import build_announce_embed, filter_duplicates, get_latest_finishes
from discord.ext import commands, tasks

logger = get_module_logger(__name__)


class KFAFin(commands.Cog, name="FinishAnnouncerCog"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Updating intervals for Hunting Cog")
        self.fetch_finishes.change_interval(minutes=botils.config.CFG.BOT["hunting"]["interval"])
        if not self.fetch_finishes.is_running():
            logger.info("starting fetch finishes")
            self.fetch_finishes.start()

        if self.fetch_finishes.is_running():
            logger.info("Canceling fetch finishes")
            self.fetch_finishes.cancel()

    @tasks.loop(minutes=botils.config.CFG.BOT["hunting"]["interval"])
    async def fetch_finishes(self):
        players = std.get_all_data()
        for player, data in players.items():
            fetched_fins = fetch_player_finishes(player, data["id"])
            cleaned_fins = filter_duplicates(fetched_fins)
            # skip if Kacky-API failed at any point
            if not fetched_fins:
                logger.error(
                    f"This doesnt look right:\n{player}: old_cnt={len(data['finishes'])}, new_cnt={len(cleaned_fins)} -> Skipping"
                )
                continue
            nfpb = get_latest_finishes(data["finishes"], cleaned_fins)
            nfpb = nfpb[:1]
            # self-correct if writing to file failed at any point
            if len(cleaned_fins) // 2 > len(data["finishes"]):
                logger.error(
                    f"This doesnt look right:\n{player}: old_cnt={len(data['finishes'])}, new_cnt={len(fetched_fins)} -> Self-correcting"
                )
                nfpb = []
            for fin in nfpb:
                embed_msg = build_announce_embed(
                        {"username": player, "fincount": len(cleaned_fins)}, fin
                    )

                # TODO: also will neeed fixing
                logger.info("Sending Message")
                await self.bot.get_channel(self.bot.fin_channel.id).send(
                    embed=embed_msg
                )
                #check for offline wr
                #logger.info("Sending message 1")
                #offlineTopTwo = get_top_two(fin['mapnr'])
                #if offlineTopTwo[0] == fin['score']:
                #    logger.info("Sending Message")
                #    await self.bot.get_channel(self.bot.fin_channel.id).send(
                #        "<@&1349723580203536527>",
                #        embed=embed_msg
                #    )
                #else:
                #    logger.info("Sending Message")
                #    await self.bot.get_channel(self.bot.fin_channel.id).send(
                #        embed=embed_msg
                #    )

                #ping wr role
                #if fin['kacky_rank'] == 1:
                #    await self.bot.get_channel(self.bot.fin_channel.id).send("<@&1349723580203536527>")

            std.add_or_update_player(player, data["id"], cleaned_fins)
        logger.info("Done fetching all players")

    @fetch_finishes.before_loop
    async def fetcher_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(KFAFin(bot))
