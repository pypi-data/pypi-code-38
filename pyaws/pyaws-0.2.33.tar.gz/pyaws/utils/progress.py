#!/usr/bin/env python3

import os
import sys
import time

try:
    import tkinter
    native = False          # do not use Linux native programs
except Exception:
    import subprocess
    native = True           # use Linux native


def screen_dimensions():
    """
    Returns:
        rows x columns, TYPE:  tuple (int, int)
    """
    rows, columns = os.popen('stty size', 'r').read().split()
    return rows, columns


def progress_meter(timer=30, delay=0.1, pattern='.', tabspaces=8, width=None):
    """
    Summary.

        Graphical progress meter

    Args:
        :timer (int): runtime in seconds
        :pattern (str): Character to print in pattern
        :tabspaces (int): lhs print margin, spaces
        :width (int): Width of pattern to print (columns)
        :delay (int): Delay between prints (seconds)

    Returns:
        stdout pattern

    """
    t = 0
    i = 0
    tab = '\t'.expandtabs(tabspaces)

    if width is None:
        stop = int(int(screen_dimensions()[1]) / 2)
    else:
        stop = int(width)

    while t < (timer * int(1 / delay)):

        if i == 0:
            sys.stdout.write('{}{}'.format(tab, pattern))
            time.sleep(delay)
            sys.stdout.flush()

        elif i > stop:
            sys.stdout.write('\n{}{}'.format(tab, pattern))
            sys.stdout.flush()
            i = 0

        else:
            sys.stdout.write('%s' % pattern)
            sys.stdout.flush()
            time.sleep(delay)

        # increment counter, timer
        i += 1
        t += 1


def screen_d(width=True, height=False):
    """
    Summary.

        Uses TKinter module in the standard library to find screen dimensions

    Args:
        :width (bool):  If True, return screen width in columns (DEFAULT)
        :height (bool): If True, return screen height in rows

    Returns:
        Screen width, height, TYPE: int

    """
    if native:
        cols = subprocess.getoutput('tput cols')
        rows = subprocess.getoutput('tput lines')
    else:
        root = tkinter.Tk()
        cols = root.winfo_screenwidth()
        rows = root.winfo_screenheight()

    if height:
        return int(rows)
    elif width and height:
        return int(cols), int(rows)
    return int(cols)
