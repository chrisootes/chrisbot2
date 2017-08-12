import asyncio
import discord
from discord.ext import commands

import time
import configparser
import spotify

class CogSpotify:
	"""
	Spotify commands for discord bot.
	https://github.com/chrisootes/chrisbot
	"""
	def __init__(self, bot, bot_logger, config):
		self.bot = bot
		self.bot_logger = bot_logger

		spotify_id = config.get("Clientid")
		spotify_secret = config.get("Clientsecret")

		spotify_token = {}
		spotify_token['access_token'] = config.get("Refreshtoken")
		spotify_token['expires_at'] = int(time.time()) + 300

		self.bot_logger.info("spotify clientid " + spotify_id)
		self.bot_logger.info("spotify clientsecret " + spotify_secret)

		spotify_auth = spotify.OAuth(spotify_id, spotify_secret, auto_refresh=True)
		spotify_auth.token = spotify_token

		self.spotify_client = spotify.Client(spotify_auth)
		self.spotify_device = None

	async def refresh_device(self):
		while not self.bot.is_closed:
			devices = self.spotify_client.api.me_player_devices()
			for device in devices['devices']:
				if device['is_active']:
					self.spotify_device = device['id']
					self.bot_logger.info("spotify device " + self.spotify_device)
			await asyncio.sleep(100)

	@commands.command(pass_context=True, no_pm=True)
	async def summon(self, ctx):
		"""Summons player."""
		await self.bot.delete_message(ctx.message)
		self.bot_logger.info("summon command issued")
		self.bot.loop.create_task(CogSpotify.refresh_device(self))
		return True

	@commands.command(pass_context=True)
	async def skip(self, ctx):
		"""Skips song."""
		await self.bot.delete_message(ctx.message)
		self.bot_logger.info("skip command issued")
		self.spotify_client.api.me_player_next(device_id=self.spotify_device)
		return True
