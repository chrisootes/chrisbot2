import discord
import logging
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')

from gi.repository import Gst, GstApp

Gst.init(None)

logger = logging.getLogger(__name__)

class GstAudio(discord.AudioSource):
    def __init__(self, config):
        #TODO parse this from config for more dynamic setup
        #pipeline = parse(config)
        self.gst_device = "alsa_output.pci-0000_00_05.0.analog-stereo.monitor"
        self.gst_pipeline = Gst.Pipeline.new("test-pipeline")
        self.gst_source = Gst.ElementFactory.make("pulsesrc", "gst_source")
        self.gst_source.set_property("device", self.gst_device)
        self.gst_converter = Gst.ElementFactory.make("audioconvert", "gst_converter")
        self.gst_encoder = Gst.ElementFactory.make("opusenc", "gst_encoder")
        self.gst_encoder.set_property("bitrate",96000)

        #fake_sink = Gst.ElementFactory.make("fakesink")
        #fake_sink.set_property("sync", True)

        self.gst_sink = Gst.ElementFactory.make("appsink", "gst_sink")

        self.gst_pipeline.add(self.gst_source)
        self.gst_pipeline.add(self.gst_converter)
        self.gst_pipeline.add(self.gst_encoder)
        self.gst_pipeline.add(self.gst_sink)

        self.gst_source.link(self.gst_converter)
        self.gst_converter.link(self.gst_encoder)
        self.gst_encoder.link(self.gst_sink)

        self.gst_pipeline.set_state(Gst.State.PLAYING)

    def is_opus(self):
        return True

    def read(self):
        #TODO optimize?
        gst_sample = self.gst_sink.pull_sample()
        gst_buffer = gst_sample.get_buffer()
        return gst_buffer.extract_dup(0, gst_buffer.get_size())

    def cleanup(self):
        self.gst_pipeline.set_state(Gst.State.NULL)
