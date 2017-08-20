import discord
from discord.ext import commands

import asyncio
import logging
import configparser
import time
import spotify
from urllib.parse import urlparse
import os.path

from discordbot.utils.logger import logger
from discordbot.utils.arguments import arguments
from discordbot.utils.config import config
from discordbot.utils.source import GstAudio

class SpotifyCommands:
	"""
	Spotify commands for discord bot.
	https://github.com/chrisootes/chrisbot2
	"""
	def __init__(self, bot):
		self.bot = bot

		spotify_id = config.get('spotify', "Clientid")
		spotify_secret = config.get('spotify', "Clientsecret")
		spotify_refresh = config.get('spotify', "Refreshtoken")

		spotify_token = {}
		spotify_token["access_token"] = spotify_refresh
		spotify_token["expires_at"] = int(time.time()) + 300

		logger.info("spotify clientid {0}".format(spotify_id))
		logger.info("spotify clientsecret {0}".format(spotify_secret))
		logger.info("spotify clientrefresh {0}".format(spotify_refresh))

		self.spotify_auth = spotify.OAuth(spotify_id, spotify_secret, auto_refresh=True)
		self.spotify_auth.token = spotify_token

		self.spotify_client = spotify.Client(spotify_auth)
		self.spotify_device = None

		self.spotify_context_uri = None #TODO memeplaylist

		self.song_list = []
		self.skippers_list = []

	async def check_skip(self, say_status):
		listening = 0
		for member in self.voice.server.members:
			if member.voice.voice_channel == self.voice.channel:
				listening += 1
		logger.info("people listening {0}".format(listening))
		skippers_needed = math.floor(0.5*listening)
		logger.info("people needed {0}".format(skippers_needed))
		skippers_amount = len(self.skippers_list)
		logger.info("people voted {0}".format(skipper_amount))
		if skipper_amount >= skippers_needed:
			self.skippers_list = []
			self.spotify_client.api.me_player_next(device_id=self.spotify_device) #blocking?
			return True
		else:
			return skipper_amount, skipper_needed

	async def check_loop(self):
		while not self.bot.is_closed:
			self.spotify_device = None
			devices = self.spotify_client.api.me_player_devices()
			for device in devices["devices"]:
				if device["is_active"]:
					self.spotify_device = device["id"]
					logger.info("spotify device {0}".format(self.spotify_device))
					break

			if self.spotify_device is None:
				logger.info("cant find spotify device")
			else:
				await SpotifyCommands.check_skip(self, False)

			await asyncio.sleep(5)

	async def song_player(self):
		while not self.bot.is_closed:
			if len(self.song_list) == 0:
				await asyncio.sleep(1)
			elif self.spotify_device is not None:
				spotify_track = self.song_list.pop(0)
				logger.info("playing {0.name}".format(spotify_track))
				self.spotify_client.api.me_player_play(device_id=self.spotify_device, context_uri=self.spotify_context_uri, uris=spotify_track.uri) #blocking?
				await asyncio.sleep(song_legth)
				self.skippers_list = []
			else:
				await asyncio.sleep(5)

	@commands.group(pass_ctx=True, no_pm=True)
	async def spotify(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("Invalid spotify subcommand passed")

	@spotify.command(pass_ctx=True)
	async def token(self, ctx, spotify_refresh : str):
		"""New refresh toke for player."""
		logger.info("toke command issued by {0}".format(ctx.message.author.name))

		#remove message ctx.message.

		spotify_token = {}
		spotify_token["access_token"] = spotify_refresh
		spotify_token["expires_at"] = int(time.time()) + 300

		logger.info("spotify clientrefresh {0}".format(spotify_refresh))

		self.spotify_auth.token = spotify_token

	@spotify.command(pass_ctx=True)
	async def summon(self, ctx):
		"""Summons player."""
		logger.info("summon command issued by {0}".format(ctx.message.author.name))
		if ctx.message.author.voice is None:
			await ctx.send("You are not in a voice channel.")
		elif ctx.voice_client is not None:
			logger.info("moving to voice channel " + ctx.message.author.voice.channel.name)
			await ctx.voice.move_to(ctx.message.author.voice.channel)
		else:
			logger.info("joining voice channel " + ctx.message.author.voice.channel.name)
			await ctx.message.author.voice.channel.connect()
			logger.info("creating source")
			source = GstAudio(config.get('spotify', "Gstreamer"))
			logger.info("playing source")
			ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
			logger.info("creating background check loop")
			self.bot.loop.create_task(SpotifyCommands.check_loop(self))
			await ctx.send("Spotify player is online")

	@spotify.command(pass_ctx=True)
	async def add(self, ctx, url_string : str):
		"""adds songs url to playlist."""
		logger.info("add command issued by {0} with {1}".format(ctx.message.author.name, url_string))
		if self.spotify_device is None:
			await ctx.send("No device playing")
			return
		#https://open.spotify.com/track/66MGk6BwVMx5O1TJqDAX4Y
		try:
			url_parsed = urlparse(url_string)
		except:
			await ctx.send("invalid spotify url")
			return
		url_split = os.path.split(url_parsed.path)
		logger.info("type is {0[0]} and id is {0[1]}".format(url_split))
		self.song_list.append(self.spotify_client.api.track(id=url_split[1])) #blocking?

	@spotify.command(pass_ctx=True)
	async def skip(self, ctx):
		"""Vote to skip current song."""
		logger.info("skip command issued by {0}".format(ctx.message.author.name))
		if self.spotify_device is None:
			await ctx.send("No device playing")
			return
		skipper_double = False
		for skipper in self.skippers_list:
			if skipper == ctx.message.author.id:
				skipper_double = True
		if not skipper_double:
			self.skippers_list.append(ctx.message.author.id)
		check_skip_results = await SpotifyCommands.check_skip(self, True)
		if check_skip_results is True:
			await ctx.send("Skipped current song")
		else:
			await ctx.send("There are {0[0]} people out of {0[1]} needed to skip this song".format(check_skip_results))

	@spotify.command(pass_ctx=True)
	async def stop(self, ctx):
		"""Stops player."""
		logger.info("stop command issued by {0}".format(ctx.message.author.name))
		if self.spotify_device is None:
			await ctx.send("No device playing")
		elif ctx.voice_client is None:
			logger.info("tried stopping with id {0.message.author.id}".format(ctx))
			await ctx.send("No voice to stop")
		elif ctx.message.author.id == "100280813244936192":
			logger.info("disconnecting voice")
			ctx.voice_client.disconnect()
		else:
			await ctx.send("Use the vote command instead")

def setup(bot):
	bot.add_cog(SpotifyCommands(bot))
