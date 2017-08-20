import discord
from discord.ext import commands

import asyncio
import logging

from discordbot.utils.logger import logger

class ExampleCommands:
	"""
	Chris commands for discord bot.
	https://github.com/chrisootes/chrisbot
	"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def echo(self, context, argument : str):
		"""Repeats message."""
		logger.info("echo command issued by {0}".format(context.message.author.name))
		await context.send("Reply: {0}".format(argument))

	@commands.command(pass_context=True)
	async def reet(self, context, argument : int):
		"""Rates with buts."""
		logger.info("reet command issued by {0}".format(context.message.author.name))
		await context.send("<:reet:240860984086888449> {0} from {1}".format(argument, context.message.author))

	@commands.command(pass_context=True)
	async def debug(self, context):
		"""Current ids."""
		logger.info("checkid command issued by {0}".format(context.message.author.name))
		await context.send("Full context is : ```{0}```".format(vars(context)))

def setup(bot):
	bot.add_cog(ExampleCommands(bot))
