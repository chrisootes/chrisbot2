import asyncio
import discord
from discord.ext import commands

from gi.repository import Gst

Gst.init(None)

import threading
import time
import math
import struct
import configparser

class CogSpotifyHelper(threading.Thread):
	"""
	Spotify commands for discord bot.
	https://github.com/chrisootes/chrisbot
	"""
	def __init__(self, voice, config):
		self.daemon = True
		self.voice = voice
		self.event_end = threading.Event()
		self.logger = logging.getLogger("discord.cog.spotify.helper")
		self.list_skippers = []

		pipeline = Gst.Pipeline.new("test-pipeline")

		source = Gst.parse_bin_from_description("pulsesrc device='alsa_output.pci-0000_00_05.0.analog-stereo.monitor' ! audioconvert ! opusenc bitrate=96000", ghost_unlinked_pads=True)

		fakesink = Gst.ElementFactory.make('fakesink')
		fakesink.set_property('sync', True)
		sink = Gst.ElementFactory.make("appsink", "sink")

	def run(self):
		while not self.event_end.is_set():


		time_delay = 0.02
		while not self.bot.is_closed:
			time_start = time.time()

			try:
				self.voice.play_audio()
			except Exception as e:
				print(e)

			time_end = time.time()
			delay = max(0, time_delay - (time_end - time_start))
			self.bot_logger.info("block " + str(time_end - time_start))
			self.bot_logger.info("delay " + str(delay))
			await asyncio.sleep(delay)

	def stop(self):
		print('Stopping')
		self.event_end.set()

	def skip(self):
		self.event_next.clear()
