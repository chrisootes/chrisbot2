import discord
from discord.ext import commands

import asyncio
import logging

logger = logging.getLogger(__name__)

class ExampleCommands:
	"""
	Example commands for discord bot.
	https://github.com/chrisootes/chrisbot2
	"""
	def __init__(self, bot):
		self.bot = bot
		self.robot_list = []
		self.robot_task = self.bot.loop.create_task(ExampleCommands.robot_loop(self))

	def __unload(self):
		self.robot_task.cancel()

	async def robot_loop(self):
		try:
			while not self.bot.is_closed():
				logger.info("robot command list is  now {0}".format(self.robot_list))
				for robot_command in self.robot_list:
					logger.info("robot command excuting {0.message} in {0.channnel_id}".format(robot_command))
					robot_channel = self.bot.get_channel(robot_command.channnel_id)
					await robot_channel.send(robot_command.message)
				await asyncio.sleep(60)
		except asyncio.CancelledError:
			pass
		except (OSError, discord.ConnectionClosed):
			self.device_task.cancel()

	@commands.command(pass_ctx=True)
	async def robot(self, ctx, argument : str):
		"""Repeats message."""
		logger.info("robot command issued by {0}".format(ctx.message.author.name))
		robot_command = {}
		robot_command["channnel_id"] = ctx.message.channel.id
		robot_command["message"] = argument
		self.robot_list.append(robot_command)
		logger.info("robot command list is  now {0}".format(self.robot_list))
		await ctx.send("New robot added")

	@commands.command(pass_ctx=True)
	async def echo(self, ctx, argument : str):
		"""Repeats message."""
		logger.info("echo command issued by {0}".format(ctx.message.author.name))
		await ctx.send("Reply: {0}".format(argument))

	@commands.command(pass_ctx=True)
	async def reet(self, ctx, argument : int):
		"""Rates with buts."""
		logger.info("reet command issued by {0}".format(ctx.message.author.name))
		await ctx.send(argument*"<:reet:240860984086888449>" + " from {0.message.author}".format(ctx))

	@commands.command(pass_ctx=True)
	async def debug(self, ctx):
		"""Debug command."""
		logger.info("debug command issued by {0}".format(ctx.message.author.name))
		await ctx.send("Full ctx is: ```{0}```".format(vars(ctx)))
		await ctx.send("Full bot is: ```{0}```".format(vars(self.bot)))

def setup(bot):
	bot.add_cog(ExampleCommands(bot))
