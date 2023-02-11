import asyncio
from pathlib import Path

import discord
from botils.utils import CFG
from discord.ext import commands


class KackersFinAnnouncer(commands.Bot):
    _data = []  # TODO: move to db

    async def on_ready(self):
        # TODO: rework to save one guild one channel i think its fine for now
        for guild in self.guilds:
            if str(guild.id) == CFG.bot.server_id:
                print(f"Found server {guild.name}")
                for ch in guild.text_channels:
                    if ch.name == CFG.bot.fin_channel:
                        self._data.append({"guild_id": guild.id, "finch_id": ch.id})
                        print(f"Found {ch.name} in {guild.name}")
                        break
                else:
                    print(
                        f"Didn't find channel {CFG.bot.get.fin_channel} in {guild.name}"
                    )
                break
        else:
            print(f"Didn't find server with id: {CFG.bot.server_id}")
        # await self.get_channel(finch).send(embed=_build_fin_embed())


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
        await kfa.start(CFG.bot.token)


if __name__ == "__main__":
    asyncio.run(main())
