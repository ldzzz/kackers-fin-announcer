from botils.utils import CFG, build_announce_embed
from discord.ext import commands, tasks


class KFAFin(commands.Cog, name="FinishAnnouncerCog"):
    def __init__(self, bot):
        self.bot = bot
        # self.fetch_fins.start() TODO: uncomment

    def cog_unload(self):
        self.fetch_fins.cancel()

    @tasks.loop(seconds=10)
    async def fetch_fins(self):
        print("imma send it ")
        # TODO: fetch data for list of members
        # TODO: update data in db
        # TODO: if change send one msg for each change
        await self.bot.get_channel(self.bot._data[0].get("finch_id")).send(
            embed=build_announce_embed()
        )

    @fetch_fins.before_loop
    async def fetcher_before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(KFAFin(bot))
