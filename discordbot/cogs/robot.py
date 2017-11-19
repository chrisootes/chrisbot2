import discord
from discord.ext import commands

import asyncio
import logging

logger = logging.getLogger(__name__)

class RobotCommands:
    """
    Robot commands for discord bot.
    https://github.com/chrisootes/chrisbot2
    """
    def __init__(self, bot):
        self.bot = bot

        self.robot_command = None
        self.robot_task = self.bot.loop.create_task(ExampleCommands.robot_loop(self))

    def __unload(self):
        self.robot_task.cancel()

    async def robot_loop(self):
        try:
            while not self.bot.is_closed():
                if self.robot_command is not None:
                    logger.info("robot command excuting {0[message]} in {0[channnel_id]}".format(self.robot_command))
                    robot_channel = self.bot.get_channel(self.robot_command['channnel_id'])
                    await robot_channel.send(self.robot_command['argument'])
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            pass
        except (OSError, discord.ConnectionClosed):
            self.device_task.cancel()

    @commands.group(pass_ctx=True, no_pm=True)
    async def robot(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid robot subcommand passed")

    @robot.command(pass_ctx=True)
    async def create(self, ctx, argument : str, time : int):
        """Repeats message."""
        logger.info("robot create command issued by {0}".format(ctx.message.author.name))
        self.robot_command = {}
        self.robot_command["channnel_id"] = ctx.message.channel.id
        self.robot_command["argument"] = argument
        self.robot_command["time"] = time
        logger.info("robot command list is  now {0}".format(self.robot_command))
        await ctx.send("New robot added")

def setup(bot):
    bot.add_cog(RobotCommands(bot))
