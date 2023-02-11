from discord import User
from discord.ext import commands


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
        await ctx.send(f"Replaced **{old_name}** with **{new_name}** succesfully")

    @commands.command(name="finishes")
    @commands.dm_only()
    async def list_user_fins(
        self,
        ctx,
        username: str = commands.parameter(description="Username of player"),
    ):
        """Lists player finishes"""
        await ctx.send(f"Player: **{username}** has following finishes:")

    @add_user.error
    @update_user.error
    @remove_user.error
    @list_user_fins.error
    async def flip_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing arguments. Please read !help")


async def setup(bot):
    await bot.add_cog(KFADm(bot))
