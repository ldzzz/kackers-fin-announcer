import db.dm_ops as dmops
import discord
from botils.fetch import fetch_player_finishes
from botils.utils import _get_module_logger
from discord import app_commands
from discord.ext import commands

logger = _get_module_logger(__name__)


class KFADm(commands.Cog, name="DMCog"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="add")
    async def add_user(
        self,
        interaction: discord.Interaction,
        username: str
    )-> None:
        """Add a player to be tracked

        Args:
            username (str): Ubisoft username
        """
        if username in list(map(lambda player: player["username"], dmops.get_all_players())):
            await interaction.response.send_message(f"Player **{username}** aleady added.")
            return
        fins = fetch_player_finishes(username)
        if fins and dmops.add_player(username, fins):
            await interaction.response.send_message(f"Added player: **{username}** with **{len(fins)} fins**.")
        else:
            await interaction.response.send_message(f"Couldn't add player: **{username}** (Player doesn't exist or Kacky API not reachable).")        

    @app_commands.command(name="remove")
    async def remove_user(
        self,
        interaction: discord.Interaction,
        username: str,
    ) -> None:
        """Removes player that was tracked

        Args:
            username (str): Ubisoft username
        """
        ret = dmops.remove_player(username)
        logger.debug(f"Remove player ret = {ret}")
        s = (
            f"Removed user: **{username}**"
            if ret
            else f"Couldn't remove user: **{username}**."
        )
        await interaction.response.send_message(s)

    @app_commands.command(name="update")
    async def update_user(
        self,
        interaction: discord.Interaction,
        old_name: str,
        new_name: str,
    ) -> None:
        """Update player username

        Args:
            old_name (str): Old username
            new_name (str): New username
        """
        await self.invoke(self.bot.get_command('remove'), query=old_name)
        await self.invoke(self.bot.get_command('add'), query=new_name)
        await interaction.response.send_message(f"Changed username from **{old_name}** to **{new_name}**")

    @app_commands.command(name="list")
    async def list_players(self, interaction: discord.Interaction) -> None:
        """List all registered players
        """
        players = dmops.get_all_players()
        s = f"Total amount of registered players: **{len(players)}**\n\n"
        for player in players:
            s += f"{player['username']}: **{player['fincount']}**\n"
        await interaction.response.send_message(s)


async def setup(bot):
    await bot.add_cog(KFADm(bot))
