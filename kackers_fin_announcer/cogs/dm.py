import botils.config
import botils.shelfer as std
import discord
from botils.fetch import fetch_player_finishes
from botils.load_config_logger import get_module_logger
from botils.utils import _create_embed, filter_duplicates, parse_teams
from discord import app_commands
from discord.ext import commands

logger = get_module_logger(__name__)


class KFADm(commands.Cog, name="DMCog"):
    cfg_group = app_commands.Group(name="config", description="Configure bot dynamically")
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
    
    @app_commands.command(name="add")
    async def add_user(self, interaction: discord.Interaction, username: str, pid: int) -> None:
        """Add a player to be tracked

        Args:
            username (str): Ubisoft username
            pid (int): ID from kacky.gg
        """
        await interaction.response.defer(thinking=True)
        if username in std.get_all_players():
            await interaction.followup.send(
                embed=_create_embed(title=f"Player already added")
            )
            return
        fins = fetch_player_finishes(username, pid)
        cleaned_fins = filter_duplicates(fins)
        if fins:
            std.add_or_update_player(username, pid, cleaned_fins)
            await interaction.followup.send(
                embed=_create_embed(
                    title=f"Player added",
                    data={"Player name": username, "Player id": pid, "Finish count": len(cleaned_fins)},
                )
            )
        else:
            await interaction.followup.send(
                embed=_create_embed(
                    title=f"Player not added",
                    data={
                        "Comment": "Player doesn't exist or Kacky API can't find them. Check your inputs"
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


    @app_commands.command(name="list")
    async def list_players(self, interaction: discord.Interaction) -> None:
        """List all registered players"""
        await interaction.response.defer(thinking=True)
        data = std.get_all_data()
        names, fins, ids = "", "", ""
        for player in list(data.keys()):
            names += f"{player}\n"
            fins += f"**{len(data[player]['finishes'])}**\n"
            ids += f"{data[player]['id']}\n"
        await interaction.followup.send(
            embed=_create_embed(
                title=f"Registered players ({len(list(data.keys()))})",
                data={"Name": names, "Finish count": fins, "ID": ids},
            )
        )

    @cfg_group.command(name="bot")
    @app_commands.choices(mode=[app_commands.Choice(name="Hunting", value="hunting"), app_commands.Choice(name="Event", value="event")])
    async def config_bot(self, interaction: discord.Interaction, mode: app_commands.Choice[str], finannouncement_channel: int=botils.config.CFG.BOT["bot"]["finannouncement_channel"], teambattle_channel: int=botils.config.CFG.BOT["bot"]["teambattle_channel"], thumbnails:str=botils.config.CFG.BOT["bot"]["thumbnails"]) -> None:
        """Set general bot configuration
        
        Args:
            mode (str): Mode to use for bot, this will be instantly applied
            finannouncement_channel (int): ChannelID where to send player finishes
            teambattle_channel (int): ChannelID where to send teambattle standings
        """
        await interaction.response.defer(thinking=True)
        logger.info("Configuring bot")
        try:
            if botils.config.CFG.BOT["bot"]["mode"] != mode:
                logger.info("Changing modes")
                if mode.value == "hunting":
                    logger.info("Unloaded cogs.event")
                    await self.bot.unload_extension("cogs.event")
                elif mode == "event":
                    logger.info("Unloaded cogs.hunting")
                    await self.bot.unload_extension("cogs.hunting")
                await self.bot.load_extension(f"cogs.{mode.value}")
            std.update_bot_config({"mode":mode.value, "finannouncement_channel":finannouncement_channel, "teambattle_channel":teambattle_channel, "thumbnails": thumbnails})
        except Exception as e:
            logger.error(e)
            await interaction.followup.send("Could not change modes. Check bot logs for further info")
        await interaction.followup.send(
            embed=_create_embed(title=f"Bot configuration", data=botils.config.CFG.BOT["bot"])
        )

    @cfg_group.command(name="hunting")
    async def config_bot(self, interaction: discord.Interaction, interval: int=botils.config.CFG.BOT["hunting"]["interval"], mappack_count: int=botils.config.CFG.BOT["hunting"]["mappack_count"], pb_limit: int=botils.config.CFG.BOT["hunting"]["pb_limit"], api: str=botils.config.CFG.BOT["hunting"]["api"]) -> None:
        """Set hunting configuration
        
        Args:
            api (str): Where to fetch finishes from
            interval (int): How often to refresh finish data of players
            mappack_count (int): Current mappack size
            pb_limit (int): Limit for announcing PB finishes
        """
        await interaction.response.defer(thinking=True)
        logger.info("Configuring hunting")
        if interval != botils.config.CFG.BOT["hunting"]["interval"] and botils.config.CFG.BOT["bot"]["mode"] == "hunting":
            logger.info("Realoding hunting cog")
            await self.bot.unload_extension("cogs.hunting")
            await self.bot.load_extension("cogs.hunting")
        std.update_hunting_config({"api":api, "interval":interval, "mappack_count":mappack_count, "pb_limit":pb_limit})
        await interaction.followup.send(
            embed=_create_embed(title=f"Hunting configuration", data=botils.config.CFG.BOT["hunting"])
        )

    @cfg_group.command(name="event")
    async def config_bot(self, interaction: discord.Interaction, battle_interval: int=botils.config.CFG.BOT["event"]["battle_interval"], interval: int=botils.config.CFG.BOT["event"]["interval"], mappack_count: int=botils.config.CFG.BOT["event"]["mappack_count"], pb_limit: int=botils.config.CFG.BOT["event"]["pb_limit"], api: str=botils.config.CFG.BOT["event"]["api"], teams:  discord.Attachment=None, edition: int=botils.config.CFG.BOT["event"]["edition"]) -> None:
        """Set hunting configuration
        
        Args:
            api (str): Where to fetch finishes from
            interval (int): How often to refresh finish data of players
            mappack_count (int): Current mappack size
            pb_limit (int): Limit for announcing PB finishes
        """
        await interaction.response.defer(thinking=True)
        logger.info("Configuring event")
        if teams:
            teams_in = await teams.read()
            parsed_teams = parse_teams(teams_in)
        else:
            parsed_teams = botils.config.CFG.BOT["event"]["teams"]
        if (battle_interval != botils.config.CFG.BOT["event"]["battle_interval"] or interval != botils.config.CFG.BOT["event"]["interval"]) and botils.config.CFG.BOT["bot"]["mode"] == "event":
            logger.info("Realoding event cog")
            await self.bot.unload_extension("cogs.event")
            await self.bot.load_extension("cogs.event")
        std.update_event_config({"api":api, "battle_interval": battle_interval, "interval":interval, "mappack_count":mappack_count, "pb_limit":pb_limit, "teams":parsed_teams, "edition": edition})
        await interaction.followup.send(
            embed=_create_embed(title=f"Event configuration", data=botils.config.CFG.BOT["event"])
        )

    @cfg_group.command(name="get")
    async def config_bot(self, interaction: discord.Interaction) -> None:
        """Get all configuration data"""
        await interaction.response.defer(thinking=True)
        await interaction.followup.send(
            embed=_create_embed(title=f"Entire configuration", data=std.get_config())
        )


async def setup(bot):
    await bot.add_cog(KFADm(bot))
