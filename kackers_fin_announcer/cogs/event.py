import botils.config
import botils.shelfer as std
import discord
from botils.fetch import fetch_player_finishes
from botils.load_config_logger import get_module_logger
from botils.nadeoAPI import get_top_two
from botils.utils import (
    _create_embed,
    build_announce_embed,
    filter_duplicates,
    get_latest_finishes,
)
from discord import app_commands
from discord.ext import commands, tasks

logger = get_module_logger(__name__)

class KFAEvent(commands.Cog, name="EventBattleCog"):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Updating intervals for Event Cog")
        self.fetch_finishes.change_interval(minutes=botils.config.CFG.BOT["event"]["interval"])
        self.team_battle_standing.change_interval(minutes=botils.config.CFG.BOT["event"]["battle_interval"])
        if not self.fetch_finishes.is_running():
            logger.info("starting fetch finishes")
            self.fetch_finishes.start()
        if not self.team_battle_standing.is_running():
            logger.info("starting teambattle")
            self.team_battle_standing.start()

    def cog_unload(self):
        if self.fetch_finishes.is_running():
            logger.info("Canceling fetch finishes")
            self.fetch_finishes.cancel()
        if self.team_battle_standing.is_running():
            logger.info("Canceling teambattle")
            self.team_battle_standing.cancel()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    @tasks.loop(minutes=botils.config.CFG.BOT["event"]["interval"])
    async def fetch_finishes(self):
        logger.info("Started fetching all players")
        players = std.get_all_data()
        for player, data in players.items():

            fetched_fins = fetch_player_finishes(player, data["id"])
            cleaned_fins_kr = filter_duplicates(fetched_fins[0])
            cleaned_fins_kx = filter_duplicates(fetched_fins[1])
            # skip if Kacky-API failed at any point
            if not fetched_fins:
                logger.error(
                    f"This doesnt look right:\n{player}: old_cnt={len(data['finishes'])}, new_cnt={len(cleaned_fins_kr)} -> Skipping"
                )
                continue

            nfpbkr = get_latest_finishes(data["kr_finishes"], cleaned_fins_kr)
            nfpbkr = nfpbkr[:1]
            # self-correct if writing to file failed at any point
            if len(cleaned_fins_kr) // 2 > len(data["kr_finishes"]):
                logger.error(
                    f"This doesnt look right:\n{player}: old_cnt={len(data['finishes'])}, new_cnt={len(cleaned_fins_kr)} -> Self-correcting"
                )
                nfpbkr = []

            for fin in nfpbkr:
                embed_msg = build_announce_embed(
                        {"username": player, "fincount": len(cleaned_fins_kr)}, fin, True
                    )

                # TODO: also will neeed fixing
                logger.info("Sending Message")
                await self.bot.get_channel(self.bot.kr_fin_channel.id).send(
                    embed=embed_msg
                )

            nfpbkx = get_latest_finishes(data["kx_finishes"], cleaned_fins_kx)
            nfpbkx = nfpbkx[:1]
            # self-correct if writing to file failed at any point
            if len(cleaned_fins_kx) // 2 > len(data["kx_finishes"]):
                logger.error(
                    f"This doesnt look right:\n{player}: old_cnt={len(data['finishes'])}, new_cnt={len(cleaned_fins_kx)} -> Self-correcting"
                )
                nfpbkx = []

            for fin in nfpbkx:
                embed_msg = build_announce_embed(
                        {"username": player, "fincount": len(cleaned_fins_kx)}, fin, False
                    )

                # TODO: also will neeed fixing
                logger.info("Sending Message")
                await self.bot.get_channel(self.bot.kx_fin_channel.id).send(
                    embed=embed_msg
                )
            std.add_or_update_player(player, data["id"], cleaned_fins_kr, cleaned_fins_kx)

        logger.info("Done fetching all players")


    @tasks.loop(hours=6)
    async def team_battle_standing(self):
        players = std.get_all_data()
        cfg = std.get_config()
        battlestats = {}
        for team in cfg["event"]["teams"]:
            battlestats[team["name"]] = 0
        print(battlestats)
        for player, data in players.items():
            pscore = sum(1 for entry in data["kr_finishes"] if entry["number"] > (cfg["event"]["edition"]-1)*75)
            for i, team in enumerate(botils.config.CFG.BOT["event"]["teams"]):
                if player in team["members"]:
                    battlestats[team["name"]] += pscore
                    break  # found the team, stop searching
        
        await self.bot.get_channel(botils.config.CFG.BOT["bot"]["teambattle_channel"]).send(
            embed=_create_embed(
                title="Team Standings", data=battlestats
            )
        )
        logger.info("Done calculating team standings")

    @fetch_finishes.before_loop
    @team_battle_standing.before_loop
    async def fetcher_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(KFAEvent(bot))
