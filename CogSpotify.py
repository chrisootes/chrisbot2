import asyncio
import discord
from discord.ext import commands

import time
import math
import struct
import configparser
import spotify
import alsaaudio

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
		spotify_refresh = config.get("Refreshtoken")

		spotify_token = {}
		spotify_token['access_token'] = spotify_refresh
		spotify_token['expires_at'] = int(time.time()) + 300

		self.bot_logger.info("spotify clientid " + spotify_id)
		self.bot_logger.info("spotify clientsecret " + spotify_secret)
		self.bot_logger.info("spotify clientsecret " + spotify_refresh)

		spotify_auth = spotify.OAuth(spotify_id, spotify_secret, auto_refresh=True)
		spotify_auth.token = spotify_token

		self.spotify_client = spotify.Client(spotify_auth)
		self.spotify_device = None

		self.voice = None
		self.list_skippers = []

	async def background_song(self):
		capture = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL, device="hw:CARD=Loopback,DEV=1")
		capture.setrate(48000)
		capture.setformat(alsaaudio.PCM_FORMAT_S16_LE)
		capture.setperiodsize(960)
		time_delay = 0.02
		while not self.bot.is_closed:
			time_start = time.time()
			data = capture.read()
			if data[0] == 960:
				try:
					self.voice.play_audio(data[1])
				except Exception as e:
					print(e)
			else:
				self.bot_logger.warning("bytes " + str(data[0]))
			time_end = time.time()
			delay = max(0, time_delay - (time_end - time_start))
			self.bot_logger.info("delay " + str(time_end - time_start))
			#await asyncio.sleep(delay)

	async def refresh_device(self):
		while not self.bot.is_closed:
			devices = self.spotify_client.api.me_player_devices()
			for device in devices['devices']:
				if device['is_active']:
					self.spotify_device = device['id']
					self.bot_logger.info("spotify device " + self.spotify_device)
			await asyncio.sleep(100)

	async def check_skip(self, say_status):
		total_listening = 0
		for member in self.voice.server.members:
			if member.voice.voice_channel == self.voice.channel:
				total_listening += 1
		self.bot_logger.info("people listening " + str(total_listening))
		skipper_needed = math.floor(0.5*total_listening)
		self.bot_logger.info("people needed " + str(skipper_needed))
		skipper_amount = len(self.list_skippers)
		self.bot_logger.info("people voted " + str(skipper_amount))
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

	@commands.command(pass_context=True, no_pm=True)
	async def summon(self, ctx):
		"""Summons player."""
		await self.bot.delete_message(ctx.message)
		self.bot_logger.info("summon command issued by " + ctx.message.author.name)
		if ctx.message.author.voice_channel is None:
			await self.bot.say("You are not in a voice channel.")
			return False
		if self.voice == None:
			self.bot_logger.info("joining voice channel " + ctx.message.author.voice_channel.name)
			self.voice = await self.bot.join_voice_channel(ctx.message.author.voice_channel)
			self.bot_logger.info("creating background task")
			self.bot.loop.create_task(CogSpotify.background_song(self))
			#self.bot.loop.create_task(CogSpotify.refresh_device(self))
			#self.bot.loop.create_task(CogSpotify.check_loop(self))
		else:
			self.bot_logger.info("moving to voice channel " + ctx.message.author.voice_channel.name)
			await self.voice.move_to(ctx.message.author.voice_channel)
		return True

	@commands.command(pass_context=True)
	async def skip(self, ctx):
		"""Vote to skip song."""
		await self.bot.delete_message(ctx.message)
		self.bot_logger.info("skip command issued by " + ctx.message.author.name)
		for skipper in self.list_skippers:
			if skipper == ctx.message.author.id:
				await self.bot.say('Cant skip twice')
				await CogSpotify.check_skip(self, True)
				return True
		self.list_skippers.append(ctx.message.author.id)
		await CogSpotify.check_skip(self, True)
		return True
