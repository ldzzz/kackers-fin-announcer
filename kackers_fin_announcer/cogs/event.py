import json

import botils.shelfer as std
import discord
from botils.fetch import fetch_player_finishes
from botils.load_config_logger import CFG, logger
from botils.nadeoAPI import get_top_two
from botils.utils import _create_embed, build_announce_embed, get_latest_finishes
from discord import app_commands
from discord.ext import commands, tasks


class KFAEvent(commands.Cog, name="EventBattleCog"):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_finishes.start()
        self.team_battle_standing.start()

    def cog_unload(self):
        self.fetch_finishes.cancel()

    @app_commands.command(name="helmboard")
    async def helm_leaderboard(self, interaction: discord.Interaction) -> None:
        """Show helm event leaderboard"""
        await interaction.response.defer(thinking=True)
        data = std.get_all_data()
        data_n = [(player, len([mapnr for mapnr in fins.keys() if int(mapnr) > (CFG.event.edition-1)*75])) for player,fins in data.items()]
        data_sorted = sorted(data_n, key=lambda x: x[1], reverse=True)
        unzipped = list(zip(*data_sorted))
        names, fin_cnt = '\n'.join(unzipped[0]), '**' + '\n'.join(str(x) for x in unzipped[1]) + '**'
        await interaction.followup.send(
            embed=_create_embed(
                title="Helm Leaderboard",
                data={
                    "Rank": "**" + '.\n'.join(str(x) for x in range(1, 1 + len(data.keys()))) + "**",
                    "Name": names,
                    "Finish count": fin_cnt,
                },
            )
        )

    @tasks.loop(minutes=CFG["event"]["interval"])
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
            nfpb = cleaned_fins[:2]
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
                
            std.add_or_update_player(player, data["id"], cleaned_fins)
        logger.info("Done fetching all players")


    @tasks.loop(hours=6)
    async def team_battle_standing(self):
        players = std.get_all_data()
        team1_score = 0
        team2_score = 0
        for player, fins in players.items():
            player_score = len([mapnr for mapnr in fins.keys() if int(mapnr) > (CFG.event.edition-1)*75])
            print(player)
            print(player_score)
            if player in CFG.event.team1:
                team1_score += player_score
            elif player in CFG.event.team2:
                team2_score += player_score
            else:
                continue

        await self.bot.get_channel(CFG["bot"]["teambattle_channel"]).send(
            embed=_create_embed(
                title="Team Standings", data={"Team1": team1_score, "Team2": team2_score}
            )
        )
        logger.info("Done calculating team standings")

    @fetch_finishes.before_loop
    @team_battle_standing.before_loop
    async def fetcher_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(KFAEvent(bot))
