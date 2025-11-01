import asyncio

import discord
from botils.load_config_logger import CFG, SECRETS, logger
from botils.shelfer import (
    get_config,
    update_bot_config,
    update_event_config,
    update_hunting_config,
)
from discord.ext import commands


class KackersFinAnnouncer(commands.Bot):
    logger.info("Starting bot init")
    logger.info("Checking if there is pre-saved config")
    saved_cfg = get_config()
    logger.info(f"Saved config: {saved_cfg}")
    if saved_cfg:
        CFG = saved_cfg
    else:
        update_bot_config(CFG["bot"])
        update_hunting_config(CFG["hunting"])
        update_event_config(CFG["event"])
    fin_channel = discord.Object(id=CFG["bot"]["finannouncement_channel"])
    server = discord.Object(id=SECRETS["server_id"])
    synced = False

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync()
            logger.info("Synced bot commands")
            self.synced = True


async def load_extensions(bot):
    await bot.load_extension(f"cogs.dm")
    await bot.load_extension(f"cogs.{CFG['bot']['mode']}")


async def main():
    kfa = KackersFinAnnouncer(
        intents=discord.Intents(messages=True, guilds=True, message_content=True),
        command_prefix="/",
    )
    async with kfa:
        await load_extensions(kfa)
        logger.info(f"Loaded extensions")
        await kfa.start(SECRETS["token"])


if __name__ == "__main__":
    asyncio.run(main())
