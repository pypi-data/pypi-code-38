#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""
import device_drivers_parent_path
device_drivers_parent_path.insert()

from gateway_helpers import logger


class DummyScope(object):

    def __init__(self, *args, **kwargs):
        self._analog_channel_names = ['ch1', 'ch2']
        self._channels = []
        for name in self._analog_channel_names:
            channel = DummyScopeChannel(name=name)
            self._channels.append(channel)
        self._timebase = DummyTimeBase()
        self._trigger = DummyTrigger()
        self._horizontal_divisions = 10
        self._vertical_divisions = 10
        self._display = DummyDisplay()
        self._acquisition = DummyAcquisition()
        self.int_prop = 0  # sample int property
        self.outputs = [DummyOutput()]

    @property
    def channels(self):
        return self._channels

    @property
    def timebase(self):
        return self._timebase

    @property
    def trigger(self):
        return self._trigger

    @property
    def display(self):
        return self._display

    @property
    def acquisition(self):
        return self._acquisition

    @property
    def int_prop(self):
        return self._int_prop

    @int_prop.setter
    def int_prop(self, val):
        max_val = 1000
        min_val = 0
        if val < min_val:
            self._int_prop = min_val
        elif val > max_val:
            self._int_prop = max_val
        else:
            self._int_prop = val

    def write(self, arg=''):
        logger.info("DummyScope.write() calls ._write()")
        return self._write(arg)

    def _write(self, arg=''):
        logger.info("DummyScope._write {}".format(arg))
        return arg

    def _ask(self, arg=''):
        logger.info("DummyScope._ask() calls ._write()")
        return self._write(arg)


class DummyScopeChannel(object):

    def __init__(self, name='ch1', *args, **kwargs):
        self._name = name
        self._enabled = False
        self.probe_id = 'dummy probe_id'

    @property
    def name(self):
        return self._name

    @property
    def enabled(self):
        return self._enabled


class DummyTimeBase(object):

    def __init__(self, *args, **kwargs):
        self._range = 1
        self._position = 0
        self._scale = 0

    @property
    def range(self):
        return self._range

    @property
    def position(self):
        return self._position

    @property
    def scale(self):
        return self._scale


class DummyDisplay(object):

    dummy_screenshot_file = 'dummy_screenshot.png'

    def fetch_screenshot(self):
        try:
            with open(self.dummy_screenshot_file, 'rb') as f:
                return f.read()
        except:
            logger.info("cannot read {}".format(self.dummy_screenshot_file))

        logger.info("returning dummy string instead of dummy_screenshot")
        return "Dummy String Placeholder for Screenshot"


class DummyTrigger(object):

    def __init__(self, source='dummy source', *args, **kwargs):
        self._source = source
        self._type = 'dummy type'
        self._coupling = 'dummy coupling'
        self.level = 'dummy level'
        self.edge = DummyEdge()

    @property
    def source(self):
        return self._source

    @property
    def type(self):
        return self._type

    @property
    def coupling(self):
        return self._coupling


class DummyEdge(object):

    def __init__(self, *args, **kwargs):
        self.slope = 0


class DummyAcquisition(object):

    def __init__(self, *args, **kwargs):
        self.record_length = 0
        self.number_of_points_minimum = 0
        self.start_time = 0
        self.time_per_record = 0
        self.number_of_envelopes = 0
        self.number_of_averages = 0
        self.type = 'dummy'


class DummyOutput(object):

    def __init__(self, *args, **kwargs):
        self.standard_waveform = {}
        self.impedance = 0
        self.enabled = False
        self.noise = DummyNoise()


class DummyNoise(object):

    def __init__(self, *args, **kwargs):
        self.percent = 0
