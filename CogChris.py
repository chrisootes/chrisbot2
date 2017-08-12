import asyncio
import discord
from discord.ext import commands

import configparser

class CogChris:
	"""
	Chris commands for discord bot.
	https://github.com/chrisootes/chrisbot
	"""
	def __init__(self, bot, bot_logger, config):
		self.bot = bot

	@commands.command(pass_context=True)
	async def echo(self, ctx, msg : str):
		"""Repeats message."""
		await self.bot.delete_message(ctx.message)
		await asyncio.sleep(1)
		await self.bot.say("Reply: " + msg)

	@commands.command(pass_context=True)
	async def reet(self, ctx, reeten : int):
		"""Rates with buts."""
		await self.bot.delete_message(ctx.message)
		await self.bot.say(str("<:reet:240860984086888449> ") * reeten + " from " + str(ctx.message.author))

	@commands.command(pass_context=True)
	async def debug(self, ctx):
		"""Current ids."""
		await self.bot.delete_message(ctx.message)
		await self.bot.say("You are: " + str(ctx.message.author.id))
		await self.bot.say("You are in: " + str(ctx.message.author.voice_channel.id))
