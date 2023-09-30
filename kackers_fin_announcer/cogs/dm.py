import db.dm_ops as dmops
from botils.fetch import fetch_player_finishes
from botils.utils import _get_module_logger
from discord.ext import commands

logger = _get_module_logger(__name__)


class KFADm(commands.Cog, name="DMCog"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add")
    @commands.dm_only()
    @commands.is_owner()
    async def add_user(
        self,
        ctx,
        username: str = commands.parameter(description="Username to add"),
    ):
        """Adds player to be tracked"""
        if username in list(map(lambda player: player["username"], dmops.get_all_players())):
            await ctx.send(f"Player **{username}** aleady added.")
            return
        fins = fetch_player_finishes(username)
        if fins and dmops.add_player(username, fins):
            await ctx.send(f"Added player: **{username}** with **{len(fins)} fins**.")
        else:
            await ctx.send(f"Couldn't add player: **{username}** (Player doesn't exist or Kacky API not reachable).")        

    @commands.command(name="remove")
    @commands.dm_only()
    @commands.is_owner()
    async def remove_user(
        self,
        ctx,
        username: str = commands.parameter(description="Username to remove"),
    ):
        """Removes player that was tracked"""
        ret = dmops.remove_player(username)
        logger.debug(f"Remove player ret = {ret}")
        s = (
            f"Removed user: **{username}**"
            if ret
            else f"Couldn't remove user: **{username}**."
        )
        await ctx.send(s)

    @commands.command(name="update")
    @commands.dm_only()
    @commands.is_owner()
    async def update_user(
        self,
        ctx,
        old_name: str = commands.parameter(description="Old username"),
        new_name: str = commands.parameter(description="New username"),
    ):
        """Updates player username"""
        await ctx.invoke(self.bot.get_command('remove'), query=old_name)
        await ctx.invoke(self.bot.get_command('add'), query=new_name)

    @commands.command(name="list")
    @commands.dm_only()
    @commands.is_owner()
    async def list_users(self, ctx):
        players = dmops.get_all_players()
        s = f"Total amount of registered players: **{len(players)}**\n\n"
        for player in players:
            s += f"{player['username']}: **{player['fincount']}**\n"
        await ctx.send(s)


async def setup(bot):
    await bot.add_cog(KFADm(bot))
