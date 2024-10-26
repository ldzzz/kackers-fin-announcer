import asyncio

import discord
from botils.utils import CFG, _get_module_logger
from discord.ext import commands

logger = _get_module_logger(__name__)


class KackersFinAnnouncer(commands.Bot):
    fin_channel = discord.Object(id=CFG.bot.finannouncement_channel)
    server = discord.Object(id=CFG.bot.server_id)
    synced = False

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync()
            logger.info("Synced bot commands")
            self.synced = True


async def load_extensions(bot):
    for cog in CFG.bot.cogs:
        await bot.load_extension(f"cogs.{cog}")


async def main():
    kfa = KackersFinAnnouncer(
        intents=discord.Intents(messages=True, guilds=True, message_content=True),
        command_prefix="/",
    )
    async with kfa:
        await load_extensions(kfa)
        logger.info(f"Loaded extensions: {CFG.bot.cogs}")
        await kfa.start(CFG.bot.token)


if __name__ == "__main__":
    asyncio.run(main())
