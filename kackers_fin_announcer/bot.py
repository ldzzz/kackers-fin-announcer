import asyncio
from pathlib import Path

import discord
from botils.utils import CFG, _get_module_logger
from discord.ext import commands

logger = _get_module_logger(__name__)


class KackersFinAnnouncer(commands.Bot):
    channel_id = None  # Which channel to report to, server is chosen from config

    async def on_ready(self):
        # TODO: rework to save one guild one channel i think its fine for now
        for guild in self.guilds:
            if str(guild.id) == CFG.bot.server_id:
                logger.info(f"Found server {guild.name}")
                for ch in guild.text_channels:
                    if ch.name == CFG.bot.fin_channel:
                        self.channel_id = ch.id
                        logger.info(f"Found {ch.name} in {guild.name}")
                        break
                else:
                    logger.error(
                        f"Didn't find channel {CFG.bot.get.fin_channel} in {guild.name}"
                    )
                break
        else:
            logger.error(f"Didn't find server with id: {CFG.bot.server_id}")


async def load_extensions(bot):
    for cog in CFG.bot.cogs:
        await bot.load_extension(f"cogs.{cog}")


async def main():
    kfa = KackersFinAnnouncer(
        intents=discord.Intents(messages=True, guilds=True, message_content=True),
        command_prefix="!",
    )
    async with kfa:
        await load_extensions(kfa)
        logger.info("Loaded extensions: {kfa.}")
        await kfa.start(CFG.bot.token)


if __name__ == "__main__":
    asyncio.run(main())
