import discord
from discord.ext import commands

import asyncio
import logging
import configparser
import time
import math
import urllib.parse
import os.path
import spotipy
import spotipy.util

from discordbot.utils.config import config
from discordbot.utils.audio import GstAudio

logger = logging.getLogger(__name__)

class SpotifyCommands:
	"""
	Spotify commands for discord bot.
	https://github.com/chrisootes/chrisbot2
	"""
	def __init__(self, bot):
		self.bot = bot

		self.spotify_username = config.get('spotify', 'Username')
		self.spotify_id = config.get('spotify', 'Id')
		self.spotify_secret = config.get('spotify', 'Secret')
		self.spotify_refresh = config.get('spotify', 'Refresh')
		self.spotify_scope = "user-read-playback-state user-modify-playback-state"

		self.spotify_client = None

		self.spotify_device = None
		self.spotify_context = None #TODO standard playlist?

		self.song_list = []
		self.skip_list = []

		self.device_task = None
		self.player_task = None

	def __unload(self):
		if device_task is not None:
			self.device_task.cancel()
		if player_task is not None:
			self.player_task.cancel()

	async def device_loop(self):
		try:
			while not self.bot.is_closed():
				self.spotify_device = None
				if self.spotify_client is not None:
					devices = self.spotify_client.current_user_player_devices()
					for device in devices["devices"]:
						if device["is_active"]:
							self.spotify_device = device["id"]
							logger.info("spotify device {0}".format(self.spotify_device))
							#logger.info("refresh token is {0}".format(self.spotify_auth.token))
							break
					await asyncio.sleep(60)
				else:
					await asyncio.sleep(5)
		except asyncio.CancelledError:
			pass
		except (OSError, discord.ConnectionClosed):
			self.device_task.cancel()
		except Exception as e:
			print(e)
			self.player_task.cancel()

	async def player_loop(self):
		try:
			while not self.bot.is_closed():
				if self.spotify_device is not None:
					if len(self.song_list) != 0:
						spotify_track_id = self.song_list.pop(0)
						logger.info("playing {0}".format(spotify_track_id))
						self.spotify_client.current_user_player_play(device_id=self.spotify_device, context_uri=self.spotify_context, tracks=spotify_track_id) #blocking?
					await asyncio.sleep(1)
					spotify_current = self.spotify_client.current_user_player_playing() #blocking?
					if "item" in spotify_current:
						logger.info("playing {0[item][name]}".format(spotify_current))
						player_game = discord.Game(name=str(spotify_current['item']['name']))
						await self.bot.change_presence(status=discord.Status.online, game=player_game)
						player_sleep = (float(spotify_current['item']['duration_ms'])-float(spotify_current['progress_ms'])+1.0)/1000
						logger.info("sleeping {0}".format(player_sleep))
						await asyncio.sleep(player_sleep)
						logger.info("next song")
					else:
						player_game = discord.Game(name="Beep Boop")
						await self.bot.change_presence(status=discord.Status.idle, game=player_game)
						await asyncio.sleep(5)
				else:
					await asyncio.sleep(5)
		except asyncio.CancelledError:
			pass
		except (OSError, discord.ConnectionClosed):
			self.player_task.cancel()
		except Exception as e:
			print(e)
			self.player_task.cancel()

	@commands.group(pass_ctx=True, no_pm=True)
	async def spotify(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("Invalid spotify subcommand passed")

	@spotify.command(pass_ctx=True)
	async def token(self, ctx):
		"""New refresh toke for player."""
		logger.info("token command issued by {0}".format(ctx.message.author.name))
		await ctx.message.delete()
		spotify_token = spotipy.util.prompt_for_user_token_auto(self.spotify_username, self.spotify_scope, self.spotify_id, self.spotify_secret)
		self.spotify_client = spotipy.Spotify(auth=spotify_token)
		await ctx.send("Spotify refresh token updated")

	@spotify.command(pass_ctx=True)
	async def summon(self, ctx):
		"""Summons player."""
		logger.info("summon command issued by {0}".format(ctx.message.author.name))
		if ctx.message.author.voice is None:
			await ctx.send("You are not in a voice channel.")
		elif ctx.voice_client is not None:
			logger.info("moving to voice channel " + ctx.message.author.voice.channel.name)
			await ctx.send("Moved voice channel.")
			await ctx.voice_client.move_to(ctx.message.author.voice.channel)
		else:
			logger.info("creating spotify client")
			spotify_token = spotipy.util.prompt_for_user_token_auto(self.spotify_username, self.spotify_scope, self.spotify_id, self.spotify_secret)
			self.spotify_client = spotipy.Spotify(auth=spotify_token)
			logger.info("joining voice channel " + ctx.message.author.voice.channel.name)
			await ctx.message.author.voice.channel.connect()
			logger.info("creating source")
			source = GstAudio(config.get('spotify', "Gstreamer"))
			logger.info("playing source")
			ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
			logger.info("create tasks")
			self.device_task = self.bot.loop.create_task(SpotifyCommands.device_loop(self))
			self.player_task = self.bot.loop.create_task(SpotifyCommands.player_loop(self))
			await ctx.send("Spotify player is online")

	@spotify.command(pass_ctx=True)
	async def add(self, ctx, url_string : str):
		"""adds songs url to playlist."""
		logger.info("add command issued by {0} with {1}".format(ctx.message.author.name, url_string))
		if self.spotify_device is None:
			await ctx.send("No device playing")
		elif ctx.voice_client is None:
			await ctx.send("No voice to skip")
		else:
			try:
				url_parsed = urllib.parse.urlparse(url_string)
			except:
				await ctx.send("invalid spotify url")
				return
			url_split = url_parsed.path
			url_split, url_id = os.path.split(url_split)
			url_split, url_type = os.path.split(url_split)
			logger.info("type is {0} and id is {1}".format(url_type, url_id))
			if url_type == 'track':
				self.song_list.append(url_id)
				await ctx.send("Added song")
			else:
				await ctx.send("Only single tracks for now")

	@spotify.command(pass_ctx=True)
	async def skip(self, ctx):
		"""Vote to skip current song."""
		logger.info("skip command issued by {0}".format(ctx.message.author.name))
		if self.spotify_device is None:
			await ctx.send("No device to skip")
		elif ctx.voice_client is None:
			await ctx.send("No voice to skip")
		else:
			skip_double = False
			for skip_member in self.skip_list:
				if skip_member == ctx.message.author.id:
					skipper_double = True
			if not skip_double:
				self.skip_list.append(ctx.message.author.id)

			skip_listening = len(ctx.voice_client.channel.members)
			logger.info("people listening {0}".format(skip_listening))
			skip_needed = math.floor(0.5*skip_listening)
			logger.info("people needed {0}".format(skip_needed))
			skip_amount = len(self.skip_list)
			logger.info("people voted {0}".format(skip_amount))

			if skip_amount >= skip_needed:
				await ctx.send("Skipped current song")
				self.skip_list = []
				if len(self.song_list) == 0:
					self.spotify_client.current_user_player_next(device_id=self.spotify_device) #blocking?
				self.player_task.cancel()
				await asyncio.sleep(1)
				self.player_task = self.bot.loop.create_task(SpotifyCommands.player_loop(self))
			else:
				await ctx.send("There are {0} people out of {1} needed to skip this song".format(skip_amount, skip_needed))

	@spotify.command(pass_ctx=True)
	async def stop(self, ctx):
		"""Stops player."""
		logger.info("stop command issued by {0}".format(ctx.message.author.name))
		if self.spotify_device is None:
			await ctx.send("No device to skip")
		elif ctx.voice_client is None:
			await ctx.send("No voice to stop")
		elif ctx.message.author.id == "100280813244936192":#TODO fix this broken piexe of shit
			logger.info("disconnecting voice")
			ctx.voice_client.disconnect()
		else:
			await ctx.send("Use the vote command instead")

def setup(bot):
	bot.add_cog(SpotifyCommands(bot))
