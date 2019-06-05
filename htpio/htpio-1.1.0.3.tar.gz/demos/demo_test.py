#!/usr/bin/env python

# Compatibility imports
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

# System imports
import time
import platform
import threading

# Project imports
from htpio import bridge
from htpio import socketio
from htpio import telnetio
from htpio.decorators import Logger
from htpio.decorators import Countcalls


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# StaticTask : Process without user interaction
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@Logger("netx_test.log")
def application():
    print("Press CTRL+C (Linux) / CTRL + BREAK (Windows) to stop... ")

    Logger.log.info("# ---------- START TASK ---------- #")

    @Countcalls
    def set_and_log(pin, value):
        gpio.set(pin, value)
        Logger.log.info(set_and_log.count())

    # Setup
    board = socketio.RaspberryPi('192.168.199.31')
    gpio = bridge.RemoteAccess(board)
    gpio.lock(14)
    gpio.configure(14, gpio.OUTPUT)

    # Command sequence
    try:
        while True:

            time_on = 0.25

            while time_on <= 3.5:
                set_and_log(14, 1)
                time.sleep(time_on)
                set_and_log(14, 0)
                time.sleep(1)
                time_on += 0.01
                print("TIME ON = {0}".format(time_on))

            # Add some logic to stop the process
            # For example the status of RDYRUN

    except KeyboardInterrupt:
        raise

    finally:

        # Cleanup
        gpio.unlock(14)
        gpio.deconfigure(14)
        gpio.logout()


"""
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   Main program
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
"""

if __name__ == "__main__":
    print("Python version  : " + platform.python_version())
    thread = threading.Thread(target=application)
    thread.start()
