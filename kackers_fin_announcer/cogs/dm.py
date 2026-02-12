import botils.config
import botils.shelfer as std
import discord
from botils.fetch import fetch_player_finishes
from botils.load_config_logger import get_module_logger
from botils.utils import _create_embed, filter_duplicates, parse_teams
from discord import app_commands
from discord.ext import commands
from botils.player_stats import SwitchableView, GeneralStatsContainer, MissingContainer

logger = get_module_logger(__name__)


class KFADm(commands.Cog, name="DMCog"):
    cfg_group = app_commands.Group(name="config", description="Configure bot dynamically")
    helmboard_group = app_commands.Group(name="helmboard", description="Helmboards")
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
        cleaned_fins_kr = filter_duplicates(fins[0])
        cleaned_fins_kx = filter_duplicates(fins[1])
        if fins:
            std.add_or_update_player(username, pid, cleaned_fins_kr, cleaned_fins_kx)
            await interaction.followup.send(
                embed=_create_embed(
                    title=f"Player added",
                    data={"Player name": username, "Player id": pid,
                           "KR Finish count": len(cleaned_fins_kr),  "KX Finish count": len(cleaned_fins_kx)},
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

    @app_commands.command(name="add_list")
    async def add_user_list(self, interaction: discord.Interaction, file: discord.Attachment) -> None:
        """Add a player to be tracked

        Args:
            username (str): Ubisoft username
            pid (int): ID from kacky.gg
        """
        if not file.filename.endswith(".txt"):
            await interaction.response.send_message("Only .txt files allowed.")
            return

        logger.info("Starting adding players")

        await interaction.response.defer(thinking=True)

        file_bytes = await file.read()
        content = file_bytes.decode("utf-8")

        logger.info("Starting adding players")
        parts = content.split('\n')
        playercount = int((len(parts) / 2))
        logger.info(f"{len(parts)}, {playercount}")

        data = []
        for i in range(0, playercount):
            name = parts[i][:-1]
            id_ = parts[i + playercount][:-1]
            data.append((name, id_))

        logger.info(data)
        successes = 0
        existing_names = std.get_all_players()

        for player in data:
            logger.info(player)
            username = player[0]
            pid = player[1]

            if username in existing_names:
                logger.info(username + " exists, removing first")
                std.delete_player(username)

            fins = fetch_player_finishes(username, pid)
            if not fins:
                logger.info("Failed to add " + username)
                continue

            cleaned_fins_kr = filter_duplicates(fins[0])
            cleaned_fins_kx = filter_duplicates(fins[1])
            std.add_or_update_player(username, pid, cleaned_fins_kr, cleaned_fins_kx)
            logger.info("Added " + username)
            successes += 1

        await interaction.followup.send(
            embed=_create_embed(
                title=f"Added player list",
                data={
                    "Comment": f"Added {successes} players"
                },
            )
        )

    @app_commands.command(name="talk")
    async def talk(self, interaction: discord.Interaction, msg: str, channel: discord.TextChannel) -> None:
        """Send message to channel with ID
        
        Args:
            msg (str): Message to send
            channel (int): channel choices
        """
        await interaction.response.defer(thinking=True)
        await channel.send(msg)  # no need to get_channel manually

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
            fins += f"**{len(data[player]['kr_finishes'])}**\n"
            ids += f"{data[player]['id']}\n"
        await interaction.followup.send(
            embed=_create_embed(
                title=f"Registered players ({len(list(data.keys()))})",
                data={"Name": names, "Finish count": fins, "ID": ids},
            )
        )

    @app_commands.command(name="player_stats")
    async def stats(self, interaction: discord.Interaction, username: str) -> None:
        """Get general player stats"""
        await interaction.response.defer(thinking=True)
        if username not in std.get_all_players():
            await interaction.followup.send_message(
                embed=_create_embed(title=f"Player does not exist")
            )
            return
        
        data = std.get_all_data()

        try:
            generalStats = GeneralStatsContainer(username, data[username])
        except Exception as e:
            logger.log(e)
        
        try:
            missingStats = MissingContainer(username, data[username])
        except Exception as e:
            logger.log(e)
        try:
            view = SwitchableView(generalStats, missingStats)
        except Exception as e:
            logger.log(e)

        try:
            await interaction.followup.send(
                view=view
            )
        except Exception as e:
            logger.error("Failed to send view")
            logger.error(e)

    @helmboard_group.command(name="kr")
    async def helm_leaderboard(self, interaction: discord.Interaction) -> None:
        """Show helm leaderboard"""
        await interaction.response.defer(thinking=True)
        player_data = std.get_all_data()
        if botils.config.CFG.BOT["bot"]["mode"] == "event":
            data_n = [(player, (sum(1 for entry in data["kr_finishes"] if entry["number"] > (botils.config.CFG.BOT["event"]["edition"]-1)*75))) for player, data in player_data.items()]
        else:
            data_n = [(player, len(data["kr_finishes"])) for player, data in player_data.items()]
        data_sorted = sorted(data_n, key=lambda x: x[1], reverse=True)
        unzipped = list(zip(*data_sorted))
        names, fin_cnt = '\n'.join(unzipped[0]), '**' + '\n'.join(str(x) for x in unzipped[1]) + '**',
        await interaction.followup.send(
            embed=_create_embed(
                title="Helm Leaderboard",
                data={
                    "Rank": "**" + '.\n'.join(str(x) for x in range(1, 1 + len(player_data.keys()))) + "**",
                    "Name": names,
                    "Finish count KR": fin_cnt
                },
            )
        )

    @helmboard_group.command(name="kx")
    async def helm_leaderboard(self, interaction: discord.Interaction) -> None:
        """Show helm leaderboard"""
        await interaction.response.defer(thinking=True)
        player_data = std.get_all_data()
        if botils.config.CFG.BOT["bot"]["mode"] == "event":
            data_n = [(player, (sum(1 for entry in data["kr_finishes"] if entry["number"] > (botils.config.CFG.BOT["event"]["edition"]-1)*75))) for player, data in player_data.items()]
        else:
            data_n = [(player, len(data["kx_finishes"])) for player, data in player_data.items()]
        data_sorted = sorted(data_n, key=lambda x: x[1], reverse=True)
        unzipped = list(zip(*data_sorted))
        names, fin_cnt = '\n'.join(unzipped[0]), '**' + '\n'.join(str(x) for x in unzipped[1]) + '**',
        await interaction.followup.send(
            embed=_create_embed(
                title="Helm Leaderboard",
                data={
                    "Rank": "**" + '.\n'.join(str(x) for x in range(1, 1 + len(player_data.keys()))) + "**",
                    "Name": names,
                    "Finish count KR": fin_cnt
                },
            )
        )

    @cfg_group.command(name="bot")
    @app_commands.choices(mode=[app_commands.Choice(name="Hunting", value="hunting"), app_commands.Choice(name="Event", value="event")])
    async def config_bot(self, 
                         interaction: discord.Interaction, 
                         mode: app_commands.Choice[str], 
                         finannouncement_channel_kr: str=str(botils.config.CFG.BOT["bot"]["finannouncement_channel_kr"]), 
                         finannouncement_channel_kx: str=str(botils.config.CFG.BOT["bot"]["finannouncement_channel_kx"]), 
                         teambattle_channel: str=str(botils.config.CFG.BOT["bot"]["teambattle_channel"]), 
                         thumbnails_kr:str=botils.config.CFG.BOT["bot"]["thumbnails_kr"],
                         thumbnails_kx:str=botils.config.CFG.BOT["bot"]["thumbnails_kx"],) -> None:
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
                if f"cogs.{mode.value}" not in self.bot.extensions:
                    await self.bot.load_extension(f"cogs.{mode.value}")
            std.update_bot_config({"mode":mode.value, 
                                   "finannouncement_channel_kr":int(finannouncement_channel_kr), 
                                   "finannouncement_channel_kx":int(finannouncement_channel_kx), 
                                   "teambattle_channel":int(teambattle_channel), 
                                   "thumbnails_kr": thumbnails_kr,
                                   "thumbnails_kx": thumbnails_kx})
        except Exception as e:
            logger.error(e)
            await interaction.followup.send("Could not change modes. Check bot logs for further info")
        await interaction.followup.send(
            embed=_create_embed(title=f"Bot configuration", data=botils.config.CFG.BOT["bot"])
        )

    @cfg_group.command(name="hunting")
    async def config_bot(self, 
                         interaction: discord.Interaction, 
                         interval: int=botils.config.CFG.BOT["hunting"]["interval"], 
                         kr_mappack_count: int=botils.config.CFG.BOT["hunting"]["kr_mappack_count"], 
                         kx_mappack_count: int=botils.config.CFG.BOT["hunting"]["kx_mappack_count"], 
                         pb_limit: int=botils.config.CFG.BOT["hunting"]["pb_limit"], 
                         api: str=botils.config.CFG.BOT["hunting"]["api"]) -> None:
        """Set hunting configuration
        
        Args:
            api (str): Where to fetch finishes from
            interval (int): How often to refresh finish data of players
            kr_mappack_count (int): Current kacky reloaded mappack size
            kx_mappack_count (int): Current kacky remixed mappack size
            pb_limit (int): Limit for announcing PB finishes
        """
        await interaction.response.defer(thinking=True)
        logger.info("Configuring hunting")
        if interval != botils.config.CFG.BOT["hunting"]["interval"] and botils.config.CFG.BOT["bot"]["mode"] == "hunting":
            logger.info("Realoding hunting cog")
            await self.bot.unload_extension("cogs.hunting")
            await self.bot.load_extension("cogs.hunting")
        std.update_hunting_config({"api":api,
                                    "interval":interval, 
                                    "kr_mappack_count": kr_mappack_count, 
                                    "kx_mappack_count": kx_mappack_count, 
                                    "pb_limit":pb_limit})
        await interaction.followup.send(
            embed=_create_embed(title=f"Hunting configuration", data=botils.config.CFG.BOT["hunting"])
        )

    @cfg_group.command(name="event")
    async def config_bot(self, 
                         interaction: discord.Interaction, 
                         battle_interval: int=botils.config.CFG.BOT["event"]["battle_interval"], 
                         interval: int=botils.config.CFG.BOT["event"]["interval"], 
                         mappack_count: int=botils.config.CFG.BOT["event"]["mappack_count"], 
                         pb_limit: int=botils.config.CFG.BOT["event"]["pb_limit"], 
                         api: str=botils.config.CFG.BOT["event"]["api"], 
                         teams:  discord.Attachment=None, edition: int=botils.config.CFG.BOT["event"]["edition"]) -> None:
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
