from discord import User
from discord.ext import commands

from botils.utils import _get_module_logger

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
        await ctx.send(f"Added user: **{username}**")

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
        await ctx.send(f"Removed user: **{username}**")

    @commands.command(name="update")
    @commands.dm_only()
    @commands.is_owner()
    async def update_user(
        self,
        ctx,
        old_name: str = commands.parameter(description="Username to remove"),
        new_name: str = commands.parameter(description="Username to track"),
    ):
        """Updates player name that is tracked"""
        logger.info(
            f"{ctx.author.name} wants to update user: {old_name} with {new_name}"
        )
        await ctx.send(f"Replaced **{old_name}** with **{new_name}** succesfully")

    @commands.command(name="fins")
    @commands.dm_only()
    async def list_user_fins(
        self,
        ctx,
        username: str = commands.parameter(description="Username of player"),
    ):
        """Lists player finishes"""
        logger.info(f"{ctx.author.name} wants to list user: {username} finishes")
        await ctx.send(f"Player: **{username}** has following finishes:")

    @add_user.error
    @update_user.error
    @remove_user.error
    @list_user_fins.error
    async def flip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            logger.debug(f"Invalid command received: {error}")
            await ctx.send("Missing arguments. Please read !help")


async def setup(bot):
    await bot.add_cog(KFADm(bot))
