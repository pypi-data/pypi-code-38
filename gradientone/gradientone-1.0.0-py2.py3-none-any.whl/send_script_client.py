"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import json
import requests
import grequests
import time   # time is a module here
import math
import datetime
import threading
from send_script_post import Script



#Default settings.  MY_RATE & MY_SIZE are configurable.  This may change.
COMPANYNAME = 'Acme'
GATEWAY_ID ='Tahoe'
instrument_ivi_type = 'agilentMSO7014A'
name = 'myscope'
config = {'channel_probe_id': u'None', 'timebase_window_position': u'0.0', 'channel_scale': u'None', 'channel_input_impedance': u'None',
    'timebase_position': u'0.0', 'display_labels': u'True', 'acquisition_time_per_record': u'None', 'digital_channel_name': u'None',
    'digital_channel_count': u'0', 'acquisition_type': u'None', 'channel_name': u'None', 'timebase_window_range': u'5e-06',
    'measurement_status': u'None', 'channel_invert': u'None', 'channel_bw_limit': u'None', 'trigger_edge_slope': u'None', 'channel_offset': u'None',
    'timebase_range': u'0.001', 'channel_input_frequency_max': u'None', 'acquisition_start_time': u'None', 'trigger_type': u'None', 'timebase_mode': u'main',
    'channel_probe_attenuation': u'None', 'timebase_scale': u'0.0001', 'trigger_source': u'None', 'timebase_reference': u'center',
    'acquisition_record_length': u'None', 'memory_size': u'10.0', 'timebase_window_scale': u'5e-07', 'display_vectors': u'True',
    'channel_range': u'None', 'channel_probe_skew': u'None', 'bandwidth': u'100000000.0', 'channel_enabled': u'None', 'vertical_divisions': u'8',
    'channel_label': u'None', 'trigger_level': u'None', 'horizontal_divisions': u'10', 'channel_count': u'None', 'self_test_delay': u'40.0',
    'analog_channel_name': u'None', 'channel_coupling': u'None', 'acquisition_segmented_index': u'1.0', 'trigger_holdoff': u'None',
    'trigger_coupling': u'None', 'analog_channel_count': u'4', 'acquisition_number_of_points_minimum': u'None', 'acquisition_segmented_count': u'2.0'}

def send_config(config, name, instrument_ivi_type):
    """send the config info to the post program"""
    context = Script(config,name,instrument_ivi_type)
    context.transmit_config()

send_config(config, name, instrument_ivi_type)
