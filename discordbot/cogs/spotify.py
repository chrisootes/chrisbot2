import discord
from discord.ext import commands

import asyncio
import logging
import configparser
import time
import spotify

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

		logger.info("spotify clientid " + spotify_id)
		logger.info("spotify clientsecret " + spotify_secret)
		logger.info("spotify clientsecret " + spotify_refresh)

		spotify_auth = spotify.OAuth(spotify_id, spotify_secret, auto_refresh=True)
		spotify_auth.token = spotify_token

		self.spotify_client = spotify.Client(spotify_auth)
		self.spotify_device = None

	async def check_skip(self, say_status):
		listening = 0
		for member in self.voice.server.members:
			if member.voice.voice_channel == self.voice.channel:
				listening += 1
		logger.info("people listening " + str(listening))
		skippers_needed = math.floor(0.5*listening)
		logger.info("people needed " + str(skippers_needed))
		skippers_amount = len(self.skippers_list)
		logger.info("people voted " + str(skipper_amount))
		if skipper_amount >= skippers_needed:
			self.skippers_list = []
			self.spotify_client.api.me_player_next(device_id=self.spotify_device)
			await self.bot.send("Skipped current song")
		else:
			if say_status:
				await self.bot.send(str(skipper_amount) + " skippers out of " + str(skipper_needed))

	async def check_loop(self):
		while not self.bot.is_closed:
			#check if skip is needed
			await SpotifyCommands.check_skip(self, False)

			# TODO check if next song to reset self.skippers_list = []

			#check for spotify device
			devices = self.spotify_client.api.me_player_devices()
			for device in devices["devices"]:
				if device["is_active"]:
					self.spotify_device = device["id"]
					self.logger.info("spotify device " + self.spotify_device)
					break
			await asyncio.sleep(10)

	@commands.group(pass_ctx=True, no_pm=True)
	async def spotify(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("Invalid spotify subcommand passed")

	@spotify.command(pass_ctx=True)
	async def skip(self, ctx):
		"""Vote to skip song."""
		logger.info("skip command issued by " + ctx.message.author.name)
		for skipper in self.skippers_list:
			if skipper == ctx.message.author.id:
				await ctx.send("Cant skip twice")
				await SpotifyCommands.check_skip(self, True)
				return
		self.skippers_list.append(ctx.message.author.id)
		await SpotifyCommands.check_skip(self, True)

	@spotify.command(pass_ctx=True)
	async def summon(self, ctx):
		"""Summons player."""
		logger.info("summon command issued by " + ctx.message.author.name)
		if ctx.message.author.voice.channel is None:
			await ctx.send("You are not in a voice channel.")
			return
		if ctx.voice_client is not None:
			logger.info("moving to voice channel " + ctx.message.author.voice.channel.name)
			await ctx.voice.move_to(ctx.message.author.voice.channel)
		else:
			logger.info("joining voice channel " + ctx.message.author.voice.channel.name)
			await ctx.message.author.voice.channel.connect()
			logger.info("creating source")
			source = GstAudio("device")
			logger.info("playing source")
			ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
			logger.info("creating background task")
			self.bot.loop.create_task(SpotifyCommands.check_loop(self))
		return True

	@spotify.command(pass_ctx=True)
	async def stop(self, ctx):
		"""Stop player."""
		logger.info("stop command issued by " + ctx.message.author.name)
		if self.player is None:
			logger.info("with id " + ctx.message.author.id)
			await ctx.send("Nothin to stop")
		elif ctx.message.author.id == "100280813244936192":
			logger.info("stopping thread")
			self.player.stop()
			logger.info("joining thread")
			self.player.join()
			logger.info("joined thread")
		else:
			await ctx.send("Use the vote command instead")

def setup(bot):
	bot.add_cog(SpotifyCommands(bot))
