import argparse
parser = argparse.ArgumentParser(prog="bot", description="A discord bot")
parser.add_argument("config", help="config to run the bot with")
arguments = parser.parse_args()
