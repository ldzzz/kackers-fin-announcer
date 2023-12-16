import asyncio

import discord
from botils.utils import CFG, _get_module_logger
from discord.ext import commands

logger = _get_module_logger(__name__)


class KackersFinAnnouncer(commands.Bot):
    channel = discord.Object(id=CFG.bot.channel_id)
    server = discord.Object(id=CFG.bot.server_id)
    
    async def on_ready(self):
        self.tree.clear_commands(guild=self.server)
        self.tree.copy_global_to(guild=self.server)
        await self.tree.sync()
        logger.info("Synced bot commands")


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
