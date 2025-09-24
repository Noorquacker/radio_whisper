#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: RadioWhisper Demod
# Author: Noorquacker
# GNU Radio version: 3.10.12.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import network
import osmosdr
import time
import threading




class radiowhisper_demod(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "RadioWhisper Demod", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.volume = volume = 1
        self.samp_rate = samp_rate = 2048e3
        self.rfGain = rfGain = 10
        self.rfFreq = rfFreq = 444525000
        self.manualSquelch = manualSquelch = -55
        self.ctcssLevel = ctcssLevel = 0.01

        ##################################################
        # Blocks
        ##################################################

        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(rfFreq, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(rfGain, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=3,
                decimation=32,
                taps=[],
                fractional_bw=0)
        self.network_udp_sink_0 = network.udp_sink(gr.sizeof_float, 1, '127.0.0.1', 2000, 0, 1400, False)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                192000,
                8000,
                2000,
                window.WIN_BLACKMAN,
                6.76))
        self.high_pass_filter_0 = filter.fir_filter_fff(
            3,
            firdes.high_pass(
                1,
                48000,
                250,
                50,
                window.WIN_BLACKMAN,
                6.76))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(volume)
        self.analog_simple_squelch_cc_0 = analog.simple_squelch_cc(manualSquelch, 1)
        self.analog_nbfm_rx_0 = analog.nbfm_rx(
        	audio_rate=48000,
        	quad_rate=192000,
        	tau=(75e-6),
        	max_dev=5e3,
          )
        self.analog_ctcss_squelch_ff_0 = analog.ctcss_squelch_ff(48000, 162.2, ctcssLevel, 0, 0, True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_ctcss_squelch_ff_0, 0), (self.high_pass_filter_0, 0))
        self.connect((self.analog_nbfm_rx_0, 0), (self.analog_ctcss_squelch_ff_0, 0))
        self.connect((self.analog_simple_squelch_cc_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.network_udp_sink_0, 0))
        self.connect((self.high_pass_filter_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_simple_squelch_cc_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.rational_resampler_xxx_0, 0))


    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_0.set_k(self.volume)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def get_rfGain(self):
        return self.rfGain

    def set_rfGain(self, rfGain):
        self.rfGain = rfGain
        self.rtlsdr_source_0.set_gain(self.rfGain, 0)

    def get_rfFreq(self):
        return self.rfFreq

    def set_rfFreq(self, rfFreq):
        self.rfFreq = rfFreq
        self.rtlsdr_source_0.set_center_freq(self.rfFreq, 0)

    def get_manualSquelch(self):
        return self.manualSquelch

    def set_manualSquelch(self, manualSquelch):
        self.manualSquelch = manualSquelch
        self.analog_simple_squelch_cc_0.set_threshold(self.manualSquelch)

    def get_ctcssLevel(self):
        return self.ctcssLevel

    def set_ctcssLevel(self, ctcssLevel):
        self.ctcssLevel = ctcssLevel
        self.analog_ctcss_squelch_ff_0.set_level(self.ctcssLevel)




def main(top_block_cls=radiowhisper_demod, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    tb.wait()


if __name__ == '__main__':
    main()
