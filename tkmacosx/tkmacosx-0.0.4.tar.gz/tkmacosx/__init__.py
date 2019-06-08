"""This module provides some modified widgets of Tkinter which works better on macos
and some more useful functions and classes as well. For example Button of tkmacosx which 
looks and feels exaclty like a native tkinter button can change its background 
and foreground colors.

Read more about tkmacosx in detail on
https://github.com/Saadmairaj/tkmacosx/tree/master/tkmacosx."""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from basewidget import *
from variables import *
from widget import *
from colors import *

if __name__ == "__main__":
    demo_sframe()
    demo_button()
    demo_colorvar()
