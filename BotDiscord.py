import asyncio
import discord
from discord.ext import commands

import logging
import configparser
import importlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord.bot")

bot_config = configparser.ConfigParser()
bot_config.read("BotDiscord.ini")
bot_token = bot_config.get("DEFAULT", "Token")
bot_prefix = bot_config.get("DEFAULT", "Prefix")
bot_description = bot_config.get("DEFAULT", "Description")

bot = commands.Bot(command_prefix=bot_prefix, description=bot_description)

for cog_name in bot_config.sections():
	if bot_config.getboolean(cog_name, "Load"):
		logger.info("loading cog " + cog_name)
		try:
			cog_import = importlib.import_module(cog_name)
			cog = getattr(cog_import, cog_name)
			cog_config = bot_config[cog_name]
			bot.add_cog(cog(bot, cog_config))
		except Exception as e:
			print(e)
			logger.warning("cannot load " + str(cog_name))
	else:
		logger.warning("not loading " + str(cog_name))


@bot.event
async def on_ready():
	logger.info("logged in as " + str(bot.user))
	logger.info("user id " + str(bot.user.id))

bot.run(bot_token)
