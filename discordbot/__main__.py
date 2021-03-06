import sys
import logging
import argparse

from discordbot import bot
from discordbot.utils.config import config

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(prog="bot", description="A discord bot")
    parser.add_argument("config", help="config to run the bot with")
    arguments = parser.parse_args()
    logger.info("loading bot with {0}".format(arguments.config))
    config.read(arguments.config)
    #logger.info("loading bot with {0}".format(config._sections))
    discordbot = bot.Bot(
        command_prefix=config.get('DEFAULT', 'prefix'),
        description=config.get('DEFAULT', 'description'),
        pm_help=config.getboolean('DEFAULT', 'pm_help')
    )
    discordbot.run(config.get('DEFAULT', 'token'))

if __name__ == '__main__':
    sys.exit(main())
