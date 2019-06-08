"""This mmodule provides some modified widgets of Tkinter work better 
with macOS and some more useful functions and classes as well. 
For example background and foreground colors of a tkmacosx Button 
widget can be changed unlike of the native tkinter button.
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
