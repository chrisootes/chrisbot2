import sys
import logging

from discordbot import bot
from discordbot.utils.logger import logger
from discordbot.utils.arguments import arguments
from discordbot.utils.config import config

def main():
	logging.basicConfig(level=logging.INFO)
	logger.info("loading bot with {0}".format(arguments.config))
	config.read(arguments.config)
	logger.info("loading bot with {0}".format(config._sections))
	discordbot = bot.Bot()
	discordbot.run(config.get('DEFAULT', 'Token'))

if __name__ == '__main__':
    sys.exit(main())
