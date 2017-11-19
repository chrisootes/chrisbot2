import discord
from discord.ext import commands

import asyncio
import logging
import traceback

from discordbot.utils.config import config

logger = logging.getLogger(__name__)

class Bot(commands.Bot):
    def __init__(self, **options):
        super().__init__(**options)
        for cog in config.sections():
            if config.getboolean(cog, "Load"):
                logger.info("loading cog {0}".format(cog))
                try:
                    self.load_extension("discordbot.cogs.{0}".format(cog))
                except Exception as e:
                    logger.warning("cannot load cog {0} due to {1.__class__.__name__}: {1}".format(cog, e))
                    traceback.print_exc()

        logger.info("finished loading cogs")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("This command is not found.")
            logger.warning("command error in {0.invoked_with}".format(ctx))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("This command is missing an argument.")
            logger.warning("command error in {0.invoked_with}".format(ctx))
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send("This command is given to many arguments.")
            logger.warning("command error in {0.invoked_with}".format(ctx))
        elif isinstance(error, commands.BadArgument):
            await ctx.send("This command is given a bad argument.")
            logger.warning("command error in {0.invoked_with}".format(ctx))
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command cannot be used in private messages.")
            logger.warning("command error in {0.invoked_with}".format(ctx))
        elif isinstance(error, commands.NotOwner):
            await ctx.send("This command can only used by the owner.")
            logger.warning("command error in {0.invoked_with}".format(ctx))
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("This command is disabled and cannot be used.")
            logger.warning("command error in {0.invoked_with}".format(ctx))
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("This command crashed.")
            logger.error("command raised an exception: {0.__class__.__name__}: {0}".format(error.original))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("This command is on cooldown, retry after: {0.retry_after}".format(error))
            logger.warning("command error in {0.invoked_with}".format(ctx))

    async def on_ready(self):
        logger.info("logged in as {0} with id {0.id}".format(self.user))
