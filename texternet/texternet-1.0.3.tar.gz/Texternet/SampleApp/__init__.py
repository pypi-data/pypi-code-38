#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import modules required for your project
# os and Texternet is suggested to always be imported

import os
from Texternet import Texternet

cwd = os.getcwd()

# The only 2 parameters given to an app is the message
# and the path of your app. Use os.chdir(path) to change
# your current working directory to your app directory. 

"""
        This is the file that Texternet looks for in your 
        app directory in order to run your app. You can 
        include more methods if you need, but this
         is the basic setup of an app.
"""

def main(x, path):

    """
            This is the method Texternet looks for that runs your app.
    """

    # The following is suggested to set up 
    # your app. However, your app may not require 
    # some of the features set up here like the
    # current working directory

    os.chdir(path)
    global cwd 
    cwd = os.getcwd()
    TN = Texternet('TWILIO_SID', 'TWILIO_TOKEN', "TWILIO_PHONE#")

    # A welcoming method/set up is also suggested
    # to set up the file system, if one is needed, 
    # of your app if a new user is using your app.

    if not x.from_ in os.listdir("./Users"):
        # x.from_ is the phone # of the user
        Welcoming(x.from_)

    # The rest of your app should be your processing
    # and sending of your result

    sampletext = "This is where your processing would happen"

    TN.sendMessage(x.from_, sampletext)

    # Please print the phone number and the message 
    # body for our system. The record isn't saved, 
    # it's just printed to the output to track errors.

    print(x.from_ + " " + x.body)

def Welcoming(Name):

    """
            This is a sample Welcoming method that takes in the name 
            of the folder you want to make for a new user. The way
            that is suggested to name folders is by phone number.
    """
    
    cwd = os.getcwd()
    os.chdir('Users/')
    os.makedirs(Name)

    # You could also do things such as make files for 
    # users or send them a welcome message if you want

    os.chdir(cwd)

"""
    You can include more methods if you need, but this is the basic setup of an app.
"""