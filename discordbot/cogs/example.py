import discord
from discord.ext import commands

import asyncio
import logging

from discordbot.utils.config import config

logger = logging.getLogger(__name__)

class ExampleCommands:
    """
    Example commands for discord bot.
    https://github.com/chrisootes/chrisbot2
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def echo(self, ctx, *argument : str):
        """Repeats message."""
        logger.info("echo command issued by {0}".format(ctx.message.author.name))
        await ctx.send("Echo: {0}".format(" ".join(argument)))

    @commands.command(pass_context=True)
    async def reet(self, ctx, argument : int):
        """Rates with buts."""
        logger.info("reet command issued by {0}".format(ctx.message.author.name))
        if(argument >= 1 and argument <= 5):
            await ctx.send(argument*"<:reet:381582414499282951>" + " from {0.message.author}".format(ctx))
        else:
            await ctx.send("Your rating it wrong {0.message.author}!".format(ctx))

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def debug(self, ctx, argument : str):
        """Debug command."""
        logger.info("debug command issued by {0}".format(ctx.message.author.name))
        await ctx.send("Full ctx is: ```{0}```".format(vars(ctx)))
        await ctx.send("Full bot is: ```{0}```".format(vars(self.bot)))
        await ctx.send("Full arg is: ```{0}```".format(argument))

def setup(bot):
    bot.add_cog(ExampleCommands(bot))
