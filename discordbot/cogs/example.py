import discord
from discord.ext import commands

import asyncio
import logging

from discordbot.utils.logger import logger

class ExampleCommands:
	"""
	Example commands for discord bot.
	https://github.com/chrisootes/chrisbot2
	"""
	def __init__(self, bot):
		self.bot = bot

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
		await ctx.send("Full ctx is : ```{0}```".format(vars(ctx)))
		await ctx.send("Full bot is : ```{0}```".format(vars(self.bot)))

def setup(bot):
	bot.add_cog(ExampleCommands(bot))
