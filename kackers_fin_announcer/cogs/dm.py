import botils.shelfer as std
import discord
from botils.fetch import fetch_player_finishes
from botils.utils import _create_embed, _get_module_logger
from discord import app_commands
from discord.ext import commands

logger = _get_module_logger(__name__)


class KFADm(commands.Cog, name="DMCog"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="add")
    async def add_user(self, interaction: discord.Interaction, username: str) -> None:
        """Add a player to be tracked

        Args:
            username (str): Ubisoft username
        """
        await interaction.response.defer(thinking=True)
        if username in std.get_all_players():
            await interaction.followup.send(
                embed=_create_embed(title=f"Player already added")
            )
            return
        fins = fetch_player_finishes(username)
        if fins:
            std.add_or_update_player(username, fins)
            await interaction.followup.send(
                embed=_create_embed(
                    title=f"Player added",
                    data={"Player name": username, "Finish count": len(fins)},
                )
            )
        else:
            await interaction.followup.send(
                embed=_create_embed(
                    title=f"Player not added",
                    data={
                        "Comment": "Player doesn't exist or Kacky API not reachable."
                    },
                )
            )

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
        await interaction.response.defer(thinking=True)
        logger.info(f"Remove player {username}")
        std.delete_player(username)
        await interaction.followup.send(
            embed=_create_embed(title=f"{username} removed")
        )

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
        await interaction.response.defer(thinking=True)
        std.update_username(old_name, new_name)
        await interaction.followup.send(
            embed=_create_embed(title=f"Player name changed")
        )

    @app_commands.command(name="list")
    async def list_players(self, interaction: discord.Interaction) -> None:
        """List all registered players"""
        await interaction.response.defer(thinking=True)
        data = std.get_all_data()
        names, fins = "", ""
        for player in list(data.keys()):
            names += f"{player}\n"
            fins += f"**{len(data[player])}**\n"
        await interaction.followup.send(
            embed=_create_embed(
                title=f"Registered players ({len(list(data.keys()))})",
                data={"Name": names, "Finish count": fins},
            )
        )


async def setup(bot):
    await bot.add_cog(KFADm(bot))
