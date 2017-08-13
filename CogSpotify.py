import asyncio
import discord
from discord.ext import commands

import logging
import configparser
import spotify

import CogSpotifyHelper from CogSpotifyHelper

class CogSpotify:
	"""
	Spotify commands for discord bot.
	https://github.com/chrisootes/chrisbot
	"""
	def __init__(self, bot, config):
		self.bot = bot
		self.logger = logging.getLogger("discord.cog.spotify")

		spotify_id = config.get("Clientid")
		spotify_secret = config.get("Clientsecret")
		spotify_refresh = config.get("Refreshtoken")

		spotify_token = {}
		spotify_token['access_token'] = spotify_refresh
		spotify_token['expires_at'] = int(time.time()) + 300

		self.logger.info("spotify clientid " + spotify_id)
		self.logger.info("spotify clientsecret " + spotify_secret)
		self.logger.info("spotify clientsecret " + spotify_refresh)

		spotify_auth = spotify.OAuth(spotify_id, spotify_secret, auto_refresh=True)
		spotify_auth.token = spotify_token

		self.spotify_client = spotify.Client(spotify_auth)
		self.spotify_device = None

		self.voice = None
		self.player = None

	async def check_spotify(self):
		while not self.bot.is_closed:
			# TODO ceck currentn song to resset self.list_skippers = []
			devices = self.spotify_client.api.me_player_devices()
			for device in devices['devices']:
				if device['is_active']:
					self.spotify_device = device['id']
					self.logger.info("spotify device " + self.spotify_device)
			await asyncio.sleep(100)

	async def check_skip(self, say_status):
		total_listening = 0
		for member in self.voice.server.members:
			if member.voice.voice_channel == self.voice.channel:
				total_listening += 1
		self.logger.info("people listening " + str(total_listening))
		skipper_needed = math.floor(0.5*total_listening)
		self.logger.info("people needed " + str(skipper_needed))
		skipper_amount = len(self.list_skippers)
		self.logger.info("people voted " + str(skipper_amount))
		if skipper_amount >= skipper_needed:
			self.list_skippers = []
			self.spotify_client.api.me_player_next(device_id=self.spotify_device)
			await self.bot.say('Skipped current song')
		else:
			if say_status:
				await self.bot.say(str(skipper_amount) + ' skippers out of ' + str(skipper_needed))

	async def check_loop(self):
		while not self.bot.is_closed:
			await CogSpotify.check_skip(self, False)
			await asyncio.sleep(10)

	@commands.command(pass_context=True)
	async def skip(self, ctx):
		"""Vote to skip song."""
		await self.bot.delete_message(ctx.message)
		self.logger.info("skip command issued by " + ctx.message.author.name)
		for skipper in self.list_skippers:
			if skipper == ctx.message.author.id:
				await self.bot.say('Cant skip twice')
				await CogSpotify.check_skip(self, True)
				return True
		self.list_skippers.append(ctx.message.author.id)
		await CogSpotify.check_skip(self, True)
		return True

	@commands.command(pass_context=True, no_pm=True)
	async def summon(self, ctx):
		"""Summons player."""
		await self.bot.delete_message(ctx.message)
		self.logger.info("summon command issued by " + ctx.message.author.name)
		if ctx.message.author.voice_channel is None:
			await self.bot.say("You are not in a voice channel.")
			return False
		if self.voice == None:
			self.logger.info("joining voice channel " + ctx.message.author.voice_channel.name)
			self.voice = await self.bot.join_voice_channel(ctx.message.author.voice_channel)
			self.logger.info("creating thread")
			self.player = CogSpotifyHelper(self.voice)
			self.player.setName('Player')
			self.player.start()
			self.logger.info("creating background task")
			self.bot.loop.create_task(CogSpotify.check_spotify(self))
			self.bot.loop.create_task(CogSpotify.check_loop(self))
		else:
			self.logger.info("moving to voice channel " + ctx.message.author.voice_channel.name)
			await self.voice.move_to(ctx.message.author.voice_channel)
		return True

	@commands.command(pass_context=True)
	async def stop(self, ctx):
		"""Stop player."""
		await self.bot.delete_message(ctx.message)
		self.logger.info("stop command issued by " + ctx.message.author.name)
		if self.player is None:
			self.logger.info("with id " + ctx.message.author.id)
			await self.bot.say('Nothin to stop')
		elif ctx.message.author.id == '100280813244936192':
			self.logger.info("stopping thread")
			self.player.stop()
			self.logger.info("joining thread")
			self.player.join() #bugged
			self.logger.info("joined thread")
		else:
			await self.bot.say('Vote to skip')
