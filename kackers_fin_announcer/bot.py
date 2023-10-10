import asyncio
from dis import disco
from pathlib import Path

import discord
from botils.utils import CFG, _get_module_logger
from discord.ext import commands

logger = _get_module_logger(__name__)


class KackersFinAnnouncer(commands.Bot):
    channel = discord.Object(id=CFG.bot.channel_id)
    server = discord.Object(id=CFG.bot.server_id)
    
    async def on_ready(self):
        self.tree.clear_commands()
        self.tree.copy_global_to(guild=self.server)
        logger.info("Syncing bot commands")
        await self.tree.sync()


async def load_extensions(bot):
    for cog in CFG.bot.cogs:
        await bot.load_extension(f"cogs.{cog}")


async def main():
    kfa = KackersFinAnnouncer(
        intents=discord.Intents(messages=True, guilds=True, message_content=True), command_prefix="/")
    async with kfa:
        await load_extensions(kfa)
        logger.info(f"Loaded extensions: {CFG.bot.cogs}")
        await kfa.start(CFG.bot.token)


if __name__ == "__main__":
    asyncio.run(main())
