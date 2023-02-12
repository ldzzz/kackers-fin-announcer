import db.dm_ops as dmops
from botils.fetch import fetch_player_fins
from botils.utils import _cleanup_fins, _get_module_logger
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
        logger.info(f"{ctx.author.name} wants to add user: {username}")
        print(ctx.author.name, ctx.author.id)
        fins = fetch_player_fins(username)
        s = None
        if not fins:
            logger.warn(f"User {username} not found")
            s = f"User **{username}** doesn't exist"
        else:
            ret = dmops.add_player(username, fins)
            s = (
                f"Added user: **{username}**"
                if ret
                else f"Couldn't add user: **{username}**. Contact djinner."
            )
        await ctx.send(s)

    @commands.command(name="remove")
    @commands.dm_only()
    @commands.is_owner()
    async def remove_user(
        self,
        ctx,
        username: str = commands.parameter(description="Username to remove"),
    ):
        """Removes player that was tracked"""
        logger.info(f"{ctx.author.name} wants to remove user: {username}")
        ret = dmops.remove_player(username)
        logger.debug(f"Remove player ret = {ret}")
        s = (
            f"Removed user: **{username}**"
            if ret
            else f"Couldn't remove user: **{username}**. Contact djinner"
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
        logger.info(f"{ctx.author.name} wants to update user: {old_name}->{new_name}")
        ret = dmops.update_username(old_name, new_name)
        logger.debug(f"Remove player ret = {ret}")
        s = (
            f"Replaced **{old_name}** with **{new_name}** succesfully"
            if ret
            else f"Couldn't update user: **{old_name}**->**{new_name}**. Contact djinner"
        )
        await ctx.send(s)


async def setup(bot):
    await bot.add_cog(KFADm(bot))
