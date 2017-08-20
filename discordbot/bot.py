import discord
from discord.ext import commands

import asyncio

from discordbot.utils.logger import logger
from discordbot.utils.arguments import arguments
from discordbot.utils.config import config

class Bot(commands.Bot):
	def __init__(self):
		super().__init__(
			command_prefix=commands.when_mentioned_or(config.get('DEFAULT', 'Prefix')),
			description=config.get('DEFAULT', 'Description'),
			pm_help=config.get('DEFAULT', 'PMhelp')
		)

		for cog in config.sections():
			if config.getboolean(cog, "Load"):
				logger.info("loading cog {0}".format(cog))
				try:
					self.load_extension("discordbot.cogs.{0}".format(cog))
				except Exception as e:
					logger.warning("cannot load cog {0} due to {1.__class__.__name__}: {1}".format(cog, e))

	async def on_ready(self):
		logger.info("logged in as {0} with id {0.id}".format(self.user))
