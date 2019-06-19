import pytest
import time
from unittest.mock import patch, call
import os
import subprocess
from .sb import *

def test_dsb__init__default():
    initial_value = 0
    final_value = 10
    used_space = len(
        'XXXX.X' + '% Complete, ' + 'XXXXX.X '
        + ' sec, (est. ' + "XXXXX.X" + ' sec left)')
    statusbar = dsb(initial_value,final_value)
    current_time = time.time()

    assert hasattr(statusbar,'time_array'), "self.time_array not initialized for dsb()"
    assert hasattr(statusbar,'start_time'), "self.start_time not initialized for dsb()"
    assert hasattr(statusbar,'time_left'), "self.time_left not initialized for dsb()"
    assert hasattr(statusbar,'terminal_width'), "self.terminal_width not initialized for dsb()"
    assert hasattr(statusbar,'statusbar_width'), "self.statusbar_width not initialized for dsb()"
    assert hasattr(statusbar,'title'), "self.title not initialized for dsb()"
    assert hasattr(statusbar,'initial_value'), "self.initial_value not initialized for dsb()"
    assert hasattr(statusbar,'final_value'), "self.final_value not initialized for dsb()"

    assert statusbar.time_array == [], \
        "Error initializing self.time_array. Should be [], instead of " + str(statusbar.time_array)
    assert abs(statusbar.start_time - current_time)<1e-4, \
        "Error initializing self.start_time. Should be " + str(current_time) + ", instead of " + str(statusbar.start_time)
    assert statusbar.time_left == "--", \
        "Error initializing self.time_array. Should be '--', instead of " + str(statusbar.time_left)
    assert statusbar.terminal_width == 80, \
        ("Error initializing self.terminal_width. Should be 80, instead of "
        + str(statusbar.terminal_width))
    assert statusbar.statusbar_width == 80-used_space-2, \
        ("Error initializing self.statusbar_width. Should be "
        + str(80-used_space-2)
        + ", instead of "
        + str(statusbar.statusbar_width))
    assert statusbar.title == "a Loop", \
        "Error initializing self.title. Should be 'a Loop', instead of " + str(statusbar.title)
    assert statusbar.initial_value == 0, \
        ("Error initializing self.initial_value. Should be 0, instead of "
        + str(statusbar.initial_value))
    assert statusbar.final_value == final_value, \
        ("Error initializing self.final_value. Should be "
        + str(final_value)
        + ", instead of "
        + str(statusbar.final_value))

    del(statusbar,
        current_time,
        initial_value,
        final_value,
        used_space)

def test_dsb__init__kwargs():
    initial_value = 0
    final_value = 10
    title = "Test"
    used_space = len(
        'XXXX.X' + '% Complete, ' + 'XXXXX.X '
        + ' sec, (est. ' + "XXXXX.X" + ' sec left)')
    statusbar = dsb(initial_value,final_value,title=title)
    current_time = time.time()

    assert hasattr(statusbar,'time_array'), "self.time_array not initialized for dsb()"
    assert hasattr(statusbar,'start_time'), "self.start_time not initialized for dsb()"
    assert hasattr(statusbar,'time_left'), "self.time_left not initialized for dsb()"
    assert hasattr(statusbar,'terminal_width'), "self.terminal_width not initialized for dsb()"
    assert hasattr(statusbar,'statusbar_width'), "self.statusbar_width not initialized for dsb()"
    assert hasattr(statusbar,'title'), "self.title not initialized for dsb()"
    assert hasattr(statusbar,'initial_value'), "self.initial_value not initialized for dsb()"
    assert hasattr(statusbar,'final_value'), "self.final_value not initialized for dsb()"

    assert statusbar.time_array == [], \
        "Error initializing self.time_array. Should be [], instead of " + str(statusbar.time_array)
    assert abs(statusbar.start_time - current_time)<1e-4, \
        "Error initializing self.start_time. Should be " + str(current_time) + ", instead of " + str(statusbar.start_time)
    assert statusbar.time_left == "--", \
        "Error initializing self.time_array. Should be '--', instead of " + str(statusbar.time_left)
    assert statusbar.terminal_width == 80, \
        ("Error initializing self.terminal_width. Should be 80, instead of "
        + str(statusbar.terminal_width))
    assert statusbar.statusbar_width == 80-used_space-2, \
        ("Error initializing self.statusbar_width. Should be "
        + str(80-used_space-2)
        + ", instead of "
        + str(statusbar.statusbar_width))
    assert statusbar.title == title, \
        ("Error initializing self.title. Should be "
        + title
        + ", instead of "
        + str(statusbar.title))
    assert statusbar.initial_value == initial_value, \
        ("Error initializing self.initial_value. Should be "
        + str(initial_value)
        + ", instead of "
        + str(statusbar.initial_value))
    assert statusbar.final_value == final_value, \
        ("Error initializing self.final_value. Should be "
        + str(final_value)
        + ", instead of "
        + str(statusbar.final_value))

    del(statusbar,
        current_time,
        final_value,
        used_space,
        initial_value,
        title)

def test_get_terminal_width():
    assert get_terminal_width() == 80, "Error with get_terminal_width(). Should be 80 (default pytest terminal size), instead of " + str(get_terminal_width())
    assert int(subprocess.check_output(["tput","cols"])) == 80, "Error with get_terminal_width() ImportError mode. The value of int(subprocess.check_output(['tput','cols'])) should be 80 (default pytest terminal size), instead of " + str(int(subprocess.check_output(["tput","cols"])))

def test_dsb_reset_default():
    initial_value = 0
    final_value = 10
    statusbar = dsb(initial_value,final_value)
    for i in range(final_value):
        time.sleep(0.1)
        statusbar.update(i)
    statusbar.reset()
    current_time = time.time()

    assert not hasattr(statusbar,"bar_indices"), "Error resetting dsb(). bar_indices should not exist."

    assert hasattr(statusbar,'time_array'), "self.time_array not initialized for dsb()"
    assert hasattr(statusbar,'start_time'), "self.start_time not initialized for dsb()"
    assert hasattr(statusbar,'time_left'), "self.time_left not initialized for dsb()"
    assert hasattr(statusbar,'terminal_width'), "self.terminal_width not initialized for dsb()"
    assert hasattr(statusbar,'statusbar_width'), "self.statusbar_width not initialized for dsb()"
    assert hasattr(statusbar,'title'), "self.title not initialized for dsb()"
    assert hasattr(statusbar,'initial_value'), "self.initial_value not initialized for dsb()"
    assert hasattr(statusbar,'final_value'), "self.final_value not initialized for dsb()"

    assert statusbar.time_array == [], \
        "Error initializing self.time_array. Should be [], instead of " + str(statusbar.time_array)
    assert abs(statusbar.start_time - current_time)<1e-4, \
        "Error initializing self.start_time. Should be " + str(current_time) + ", instead of " + str(statusbar.start_time)
    assert statusbar.time_left == "--", \
        "Error initializing self.time_array. Should be '--', instead of " + str(statusbar.time_left)
    assert statusbar.title == "a Loop", \
        "Error initializing self.title. Default should be 'a Loop', instead of " + str(statusbar.title)
    assert statusbar.initial_value == 0, \
        ("Error initializing self.initial_value. Should be 0, instead of "
        + str(statusbar.initial_value))
    assert statusbar.final_value == final_value, \
        ("Error initializing self.final_value. Should be "
        + str(final_value)
        + ", instead of "
        + str(statusbar.final_value))

    del(statusbar,current_time,initial_value,final_value)

def test_dsb_reset_kwargs():
    initial_value = 0
    final_value = 10
    a_different_initial_value = 5
    a_different_final_value = 20
    a_different_title = "Test"

    statusbar = dsb(initial_value,final_value)
    for i in range(final_value):
        time.sleep(0.1)
        statusbar.update(i)
    statusbar.reset(
        initial_value=a_different_initial_value,
        final_value=a_different_final_value,
        title=a_different_title)
    current_time = time.time()

    assert not hasattr(statusbar,"bar_indices"), "Error resetting dsb(). bar_indices should not exist."

    assert hasattr(statusbar,'time_array'), "self.time_array not initialized for dsb()"
    assert hasattr(statusbar,'start_time'), "self.start_time not initialized for dsb()"
    assert hasattr(statusbar,'time_left'), "self.time_left not initialized for dsb()"
    assert hasattr(statusbar,'terminal_width'), "self.terminal_width not initialized for dsb()"
    assert hasattr(statusbar,'statusbar_width'), "self.statusbar_width not initialized for dsb()"
    assert hasattr(statusbar,'title'), "self.title not initialized for dsb()"
    assert hasattr(statusbar,'initial_value'), "self.initial_value not initialized for dsb()"
    assert hasattr(statusbar,'final_value'), "self.final_value not initialized for dsb()"

    assert statusbar.time_array == [], \
        "Error initializing self.time_array. Should be [], instead of " + str(statusbar.time_array)
    assert abs(statusbar.start_time - current_time)<1e-4, \
        "Error initializing self.start_time. Should be " + str(current_time) + ", instead of " + str(statusbar.start_time)
    assert statusbar.time_left == "--", \
        "Error initializing self.time_array. Should be '--', instead of " + str(statusbar.time_left)
    assert statusbar.title == a_different_title, \
        ("Error initializing self.title. Default should be "
        + a_different_title
        +", instead of "
        + str(statusbar.title))
    assert statusbar.initial_value == a_different_initial_value, \
        ("Error initializing self.initial_value. Should be "
        + str(a_different_initial_value)
        + ", instead of "
        + str(statusbar.initial_value))
    assert statusbar.final_value == a_different_final_value, \
        ("Error initializing self.final_value. Should be "
        + str(a_different_final_value)
        + ", instead of "
        + str(statusbar.final_value))

    del(statusbar,
        current_time,
        initial_value,
        final_value,
        a_different_title,
        a_different_initial_value,
        a_different_final_value)

def test_dsb_automatic_reset():
    initial_value = 0
    final_value = 10
    statusbar = dsb(initial_value,final_value)
    for i in range(final_value):
        time.sleep(0.1)
        statusbar.update(i)
    statusbar.update(0)
    current_time = time.time()
    test_bar_indices = [0,1,2,3,4,5,6,7,8,9,10]

    assert hasattr(statusbar,'bar_indices'), "self.bar_indices not initialized for i == statusbar.initial_value."
    assert hasattr(statusbar,'time_array'), "self.time_array not initialized for dsb()"
    assert hasattr(statusbar,'start_time'), "self.start_time not initialized for dsb()"
    assert hasattr(statusbar,'time_left'), "self.time_left not initialized for dsb()"
    assert hasattr(statusbar,'terminal_width'), "self.terminal_width not initialized for dsb()"
    assert hasattr(statusbar,'statusbar_width'), "self.statusbar_width not initialized for dsb()"
    assert hasattr(statusbar,'title'), "self.title not initialized for dsb()"
    assert hasattr(statusbar,'initial_value'), "self.initial_value not initialized for dsb()"
    assert hasattr(statusbar,'final_value'), "self.final_value not initialized for dsb()"

    assert statusbar.bar_indices == test_bar_indices, "Error resetting dsb(). bar_indices should be [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], not " + str(statusbar.bar_indices)
    assert statusbar.time_array == [], \
        "Error initializing self.time_array. Should be [], instead of " + str(statusbar.time_array)
    assert abs(statusbar.start_time - current_time)<1e-2, \
        "Error initializing self.start_time. Should be " + str(current_time) + ", instead of " + str(statusbar.start_time)
    assert statusbar.time_left == "--", \
        "Error initializing self.time_array. Should be '--', instead of " + str(statusbar.time_left)
    assert statusbar.title == "a Loop", \
        "Error initializing self.title. Default should be 'a Loop', instead of " + str(statusbar.title)
    assert statusbar.initial_value == 0, \
        ("Error initializing self.initial_value. Should be 0, instead of "
        + str(statusbar.initial_value))
    assert statusbar.final_value == final_value, \
        ("Error initializing self.final_value. Should be "
        + str(final_value)
        + ", instead of "
        + str(statusbar.final_value))
    del(statusbar,
        current_time,
        initial_value,
        final_value,
        test_bar_indices)
