import asyncio

import botils.config
import discord
import traceback
from botils.load_config_logger import get_module_logger
from botils.shelfer import (
    get_config,
    update_bot_config,
    update_event_config,
    update_hunting_config,
)
from discord.ext import commands

logger = get_module_logger(__name__)

class KackersFinAnnouncer(commands.Bot):
    logger.info("Starting bot init")
    logger.info("Checking if there is pre-saved config")
    #saved_cfg = get_config()
    #logger.info(f"Saved config: {saved_cfg}")
    #if saved_cfg:
    #    botils.config.CFG.BOT = saved_cfg
    #else:
    update_bot_config(botils.config.CFG.BOT["bot"])
    update_hunting_config(botils.config.CFG.BOT["hunting"])
    update_event_config(botils.config.CFG.BOT["event"])
    
    kr_fin_channel = discord.Object(id=botils.config.CFG.BOT["bot"]["finannouncement_channel_kr"])
    kx_fin_channel = discord.Object(id=botils.config.CFG.BOT["bot"]["finannouncement_channel_kx"])
    aprilFoolsChannel = discord.Object(id=1469374356499988627)
    server = discord.Object(id=botils.config.CFG.SECRETS["server_id"])
    synced = False

    async def on_ready(self):
        if not self.synced:
            sync = await self.tree.sync()
            logger.info(sync)
            self.synced = True


async def load_extensions(bot):
    logger.info(f"Loading extension: cogs.dm")
    await bot.load_extension(f"cogs.dm")
    logger.info(f"Loading extension: cogs.{botils.config.CFG.BOT['bot']['mode']}")
    await bot.load_extension(f"cogs.{botils.config.CFG.BOT['bot']['mode']}")


async def main():
    kfa = KackersFinAnnouncer(
        intents=discord.Intents(messages=True, guilds=True, message_content=True),
        command_prefix="/",
    )

    # Global error logging for prefix commands (if you use any)
    @kfa.event
    async def on_error(event_method, *args, **kwargs):
        traceback.print_exc()

    @kfa.event
    async def on_command_error(ctx, error):
        traceback.print_exc()

    # Slash/app command errors
    from discord import app_commands, Interaction

    @kfa.tree.error
    async def on_app_command_error(interaction: Interaction, error: app_commands.AppCommandError):
        traceback.print_exc()
        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"Error: {error}", ephemeral=True)
            else:
                await interaction.response.send_message(f"Error: {error}", ephemeral=True)
        except Exception:
            pass

    async with kfa:
        await load_extensions(kfa)
        logger.info(f"Loaded extensions")
        await kfa.start(botils.config.CFG.SECRETS["token"])


if __name__ == "__main__":
    asyncio.run(main())