import botils.config
import botils.shelfer as std
import discord
from botils.fetch import fetch_player_finishes
from botils.load_config_logger import get_module_logger
from botils.nadeoAPI import get_rank
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

        #if self.fetch_finishes.is_running():
        #    logger.info("Canceling fetch finishes")
        #    self.fetch_finishes.cancel()

    @tasks.loop(minutes=botils.config.CFG.BOT["hunting"]["interval"])
    async def fetch_finishes(self):
        logger.info("Started fetching all players")
        await self.bot.change_presence(activity=discord.Game(name='Fetching finishes'))
        players = std.get_all_data()
        for player, data in players.items():
            fetched_fins = fetch_player_finishes(player, data["id"])
            cleaned_fins_kr = filter_duplicates(fetched_fins[0])
            cleaned_fins_kx = filter_duplicates(fetched_fins[1])
            # skip if Kacky-API failed at any point
            if not fetched_fins:
                logger.error(
                    f"This doesnt look right:\n{player}: old_cnt={len(data['kr_finishes'])}, new_cnt={len(cleaned_fins_kr)} -> Skipping"
                )
                continue
            
            nfpbkr = get_latest_finishes(data["kr_finishes"], cleaned_fins_kr)
            nfpbkr = nfpbkr[:1]
            # self-correct if writing to file failed at any point
            if len(cleaned_fins_kr) // 2 > len(data["kr_finishes"]):
                logger.error(
                    f"This doesnt look right:\n{player}: old_cnt={len(data['kr_finishes'])}, new_cnt={len(cleaned_fins_kr)} -> Self-correcting"
                )
                nfpbkr = []

            for fin in nfpbkr:
                fin["offline_rank"] = get_rank(fin["mapUid"], fin["score"])

                embed_msg = build_announce_embed(
                        {"username": player, "fincount": len(cleaned_fins_kr)}, fin, True
                    )

                # TODO: also will neeed fixing
                logger.info("Sending Message")
                if fin["offline_rank"] == 1:
                    await self.bot.get_channel(self.bot.kr_fin_channel.id).send(
                        f"<@&{botils.config.CFG.SECRETS["wr_role_id"]}>",
                        embed=embed_msg
                    )
                else:
                    await self.bot.get_channel(self.bot.kr_fin_channel.id).send(
                        embed=embed_msg
                    )

            nfpbkx = get_latest_finishes(data["kx_finishes"], cleaned_fins_kx)
            nfpbkx = nfpbkx[:1]
            # self-correct if writing to file failed at any point
            if len(cleaned_fins_kx) // 2 > len(data["kx_finishes"]):
                logger.error(
                    f"This doesnt look right:\n{player}: old_cnt={len(data['kx_finishes'])}, new_cnt={len(cleaned_fins_kx)} -> Self-correcting"
                )
                nfpbkx = []

            for fin in nfpbkx:
                fin["offline_rank"] = get_rank(fin["mapUid"], fin["score"])

                embed_msg = build_announce_embed(
                        {"username": player, "fincount": len(cleaned_fins_kx)}, fin, False
                    )

                # TODO: also will neeed fixing
                logger.info("Sending Message")

                if fin["offline_rank"] == 1:
                    await self.bot.get_channel(self.bot.kx_fin_channel.id).send(
                        f"<@&{botils.config.CFG.SECRETS["wr_role_id"]}>",
                        embed=embed_msg
                    )
                else:
                    await self.bot.get_channel(self.bot.kx_fin_channel.id).send(
                        embed=embed_msg
                    )
            std.add_or_update_player(player, data["id"], cleaned_fins_kr, cleaned_fins_kx)

        logger.info("Done fetching all players")
        await self.bot.change_presence(activity=discord.Game(name='🎮Finishing kacky maps'))

    @fetch_finishes.before_loop
    async def fetcher_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(KFAFin(bot))
