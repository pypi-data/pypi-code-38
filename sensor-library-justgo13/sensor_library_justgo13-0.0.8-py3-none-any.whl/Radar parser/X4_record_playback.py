#!/usr/bin/env python
from __future__ import print_function, division

import sys
from optparse import OptionParser
from time import sleep

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import pymoduleconnector
from pymoduleconnector import DataType

__version__ = 3


def reset(device_name):
    """
    Resets the device profile and restarts the device

    Parameter:

    device_name: str
        Identifies the device being used for recording using it's port number.
    """
    mc = pymoduleconnector.ModuleConnector(device_name)
    xep = mc.get_xep()
    xep.module_reset()
    mc.close()
    sleep(3)


def on_file_available(data_type, filename):
    """
    Returns the file name that is available after recording.

    Parameter:

    data_type: str
        data type of the recording file.
    filename: str
        file name of recording file.
    """
    print("new file available for data type: {}".format(data_type))
    print("  |- file: {}".format(filename))
    if data_type == DataType.FloatDataType:
        print("processing Float data from file")


def on_meta_file_available(session_id, meta_filename):
    """
    Returns the meta file name that is available after recording.

    Parameters:

    session_id: str
        unique id to identify meta file
    filename: str
        file name of meta file.
    """
    print("new meta file available for recording with id: {}".format(session_id))
    print("  |- file: {}".format(meta_filename))


def clear_buffer(mc):
    """
    Clears the frame buffer

    Parameter:

    mc: object
        module connector object

    """
    xep = mc.get_xep()
    while xep.peek_message_data_float():
        xep.read_message_data_float()


def simple_xep_plot(device_name, record=False, baseband=False):
    """
    Plots the recorded data.

    Parameters:

    device_name: str
        port that device is connected to.
    record: boolean
        check if device is recording.
    baseband: boolean
        check if recording with baseband iq data.

    Return:

    Simple plot of range bin by amplitude.
    """
    FPS = 10
    directory = '.'
    reset(device_name)
    mc = pymoduleconnector.ModuleConnector(device_name)

    # Assume an X4M300/X4M200 module and try to enter XEP mode
    app = mc.get_x4m300()
    # Stop running application and set module in manual mode.
    try:
        app.set_sensor_mode(0x13, 0)  # Make sure no profile is running.
    except RuntimeError:
        # Profile not running, OK
        pass

    try:
        app.set_sensor_mode(0x12, 0)  # Manual mode.
    except RuntimeError:
        # Maybe running XEP firmware only?
        pass

    if record:
        recorder = mc.get_data_recorder()
        recorder.subscribe_to_file_available(pymoduleconnector.AllDataTypes, on_file_available)
        recorder.subscribe_to_meta_file_available(on_meta_file_available)

    xep = mc.get_xep()
    # Set DAC range
    xep.x4driver_set_dac_min(900)
    xep.x4driver_set_dac_max(1150)

    # Set integration
    xep.x4driver_set_iterations(16)
    xep.x4driver_set_pulses_per_step(26)

    xep.x4driver_set_downconversion(int(baseband))
    # Start streaming of data
    xep.x4driver_set_fps(FPS)

    def read_frame():
        """Gets frame data from module"""
        d = xep.read_message_data_float()
        frame = np.array(d.data)
        # Convert the resulting frame to a complex array if downconversion is enabled
        if baseband:
            n = len(frame)
            frame = frame[:n // 2] + 1j * frame[n // 2:]
        return frame

    def animate(i):
        if baseband:
            line.set_ydata(abs(read_frame()))  # update the data
        else:
            line.set_ydata(read_frame())
        return line,

    fig = plt.figure()
    fig.suptitle("example version %d " % (__version__))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_ylim(0 if baseband else -0.03, 0.03)  # keep graph in frame (FIT TO YOUR DATA)
    frame = read_frame()
    if baseband:
        frame = abs(frame)
    line, = ax.plot(frame)

    clear_buffer(mc)

    if record:
        recorder.start_recording(DataType.BasebandApDataType | DataType.FloatDataType, directory)

    ani = FuncAnimation(fig, animate, interval=FPS)
    try:
        plt.show()
    finally:
        # Stop streaming of data
        xep.x4driver_set_fps(0)


def playback_recording(meta_filename, baseband=False):
    """
    Plays back the recording.

    Parameters:

    meta_filename: str
        Name of meta file.
    baseband: boolean
        Check if recording with baseband iq data.
    """
    print("Starting playback for {}".format(meta_filename))
    player = pymoduleconnector.DataPlayer(meta_filename, -1)
    dur = player.get_duration()
    mc = pymoduleconnector.ModuleConnector(player)
    xep = mc.get_xep()
    player.set_playback_rate(1.0)
    player.set_loop_mode_enabled(True)
    player.play()

    print("Duration(ms): {}".format(dur))

    def read_frame():
        """Gets frame data from module"""
        d = xep.read_message_data_float()
        frame = np.array(d.data)
        if baseband:
            n = len(frame)
            frame = frame[:n // 2] + 1j * frame[n // 2:]
        return frame

    def animate(i):
        if baseband:
            line.set_ydata(abs(read_frame()))  # update the data
        else:
            line.set_ydata(read_frame())
        return line,

    fig = plt.figure()
    fig.suptitle("Plot playback")
    ax = fig.add_subplot(1, 1, 1)
    frame = read_frame()
    line, = ax.plot(frame)
    ax.set_ylim(0 if baseband else -0.03, 0.03)  # keep graph in frame (FIT TO YOUR DATA)
    ani = FuncAnimation(fig, animate, interval=10)
    plt.show()

    player.stop()


def main():
    """
    Creates a parser with subcatergories.

    Return:

    A simple XEP plot of live feed from X4 radar.
    """
    parser = OptionParser()
    parser.add_option(
        "-d",
        "--device",
        dest="device_name",
        help="device file to use",
        metavar="FILE")
    parser.add_option(
        "-b",
        "--baseband",
        action="store_true",
        default=False,
        dest="baseband",
        help="Enable baseband, rf data is default")
    parser.add_option(
        "-r",
        "--record",
        action="store_true",
        default=False,
        dest="record",
        help="Enable recording")
    parser.add_option(
        "-f",
        "--file",
        dest="meta_filename",
        metavar="FILE",
        help="meta file from recording")

    (options, args) = parser.parse_args()
    if not options.device_name:
        if options.meta_filename:
            playback_recording(options.meta_filename,
                               baseband=options.baseband)
        else:
            parser.error("Missing -d or -f. See --help.")
    else:
        simple_xep_plot(options.device_name, record=options.record,
                        baseband=options.baseband)


if __name__ == "__main__":
    main()
