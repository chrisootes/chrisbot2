import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')

from gi.repository import Gst, GstApp

Gst.init(None)

import threading
import time
import math
import struct

class GstDiscord(threading.Thread):
	def __init__(self, voice, device):
		self.daemon = True
		self.event_end = threading.Event()
		self.voice = voice
		self.device = "alsa_output.pci-0000_00_05.0.analog-stereo.monitor"
		self.logger = logging.getLogger("audiostreamer")

	def run(self):
		gst_pipeline = Gst.Pipeline.new("test-pipeline")
		gst_source = Gst.ElementFactory.make("pulsesrc", "gst_source")
		gst_source.set_property("device", self.gst_device)
		gst_converter = Gst.ElementFactory.make("audioconvert", "gst_converter")
		gst_encoder = Gst.ElementFactory.make("opusenc", "gst_encoder")
		gst_encoder.set_property("bitrate",96000)

		#fake_sink = Gst.ElementFactory.make("fakesink")
		#fake_sink.set_property("sync", True)

		gst_sink = Gst.ElementFactory.make("appsink", "gst_sink")

		gst_pipeline.add(gst_source)
		gst_pipeline.add(gst_converter)
		gst_pipeline.add(gst_encoder)
		gst_pipeline.add(gst_sink)

		gst_source.link(gst_converter)
		gst_converter.link(gst_encode)
		gst_encoder.link(gst_sink)

		gst_pipeline.set_state(Gst.State.PLAYING)

		while not self.event_end.is_set():
			gst_sample = gst_sink.pull_sample()
			gst_buffer = gst_sample.get_buffer()
			gst_data = gst_buffer.extract_dup(0, gst_buffer.get_size())
			self.voice.play_audio(gst_data , False)

		#TODO end bytes to end stream
		#self.voice.play_audio(gst_data , False)

	def stop(self):
		print("Stopping")
		self.event_end.set()
