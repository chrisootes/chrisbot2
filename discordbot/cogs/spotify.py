import asyncio
import discord
from discord.ext import commands

import logging
import configparser
import time
import spotify

from discordbot.utils.logger import logger
from discordbot.utils.arguments import arguments
from discordbot.utils.config import config
import discordbot.utils.audio import GstDiscord

class SpotifyCommands:
	"""
	Spotify commands for discord bot.
	https://github.com/chrisootes/chrisbot
	"""
	def __init__(self, bot):
		self.bot = bot

		spotify_id = config.get("Clientid")
		spotify_secret = config.get("Clientsecret")
		spotify_refresh = config.get("Refreshtoken")

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

		self.voice = None
		self.player = None

	async def check_skip(self, say_status):
		listening = 0
		for member in self.voice.server.members:
			if member.voice.voice_channel == self.voice.channel:
				listening += 1
		self.logger.info("people listening " + str(listening))
		skippers_needed = math.floor(0.5*listening)
		self.logger.info("people needed " + str(skippers_needed))
		skippers_amount = len(self.skippers_list)
		self.logger.info("people voted " + str(skipper_amount))
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

	@commands.group(pass_context=True)
	async def spotify(self, context):
	    if context.invoked_subcommand is None:
	        await context.send("Invalid spotify command passed...")

	@spotify.command(pass_context=True)
	async def skip(self, context):
		"""Vote to skip song."""
		logger.info("skip command issued by " + context.message.author.name)
		for skipper in self.skippers_list:
			if skipper == context.message.author.id:
				await context.send("Cant skip twice")
				await SpotifyCommands.check_skip(self, True)
				return
		self.skippers_list.append(context.message.author.id)
		await SpotifyCommands.check_skip(self, True)

	@spotify.command(pass_context=True, no_pm=True)
	async def summon(self, context):
		"""Summons player."""
		logger.info("summon command issued by " + context.message.author.name)
		if context.message.author.voice_channel is None:
			await context.send("You are not in a voice channel.")
			return
		if self.voice == None:
			logger.info("joining voice channel " + context.message.author.voice_channel.name)
			self.voice = await self.bot.join_voice_channel(context.message.author.voice_channel)
			logger.info("creating thread")
			self.player = GstDiscord(self.voice)
			self.player.setName("Player")
			self.player.start()
			logger.info("creating background task")
			self.bot.loop.create_task(SpotifyCommands.check_loop(self))
		else:
			logger.info("moving to voice channel " + context.message.author.voice_channel.name)
			await self.voice.move_to(context.message.author.voice_channel)
		return True

	@spotify.command(pass_context=True)
	async def stop(self, context):
		"""Stop player."""
		logger.info("stop command issued by " + context.message.author.name)
		if self.player is None:
			logger.info("with id " + context.message.author.id)
			await context.send("Nothin to stop")
		elif context.message.author.id == "100280813244936192":
			logger.info("stopping thread")
			self.player.stop()
			logger.info("joining thread")
			self.player.join()
			logger.info("joined thread")
		else:
			await context.send("Use the vote command instead")

def setup(bot):
    bot.add_cog(SpotifyCommands(bot))
