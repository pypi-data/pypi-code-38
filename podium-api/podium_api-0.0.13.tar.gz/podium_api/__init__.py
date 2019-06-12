#!/usr/bin/env python
# -*- coding: utf-8 -*-
from podium_api.types.application import PodiumApplication
from podium_api.types.exceptions import PodiumApplicationAlreadyRegistered
"""
The podium_api module allows you to asynchronously interact with the Podium
API. It is built on top of Kivy's UrlRequest. 

**Module Attributes:**
"""

"""

    **PODIUM_APP** (PodiumApplication): The instance of a PodiumApplication
    storing the app uuid and secret for the Podium API. Starts out as None,
    your program must call **register_podium_application** with the uuid and
    app secret before making any calls to podium_api.
    
"""

PODIUM_APP = None

def register_podium_application(app_id, app_secret, podium_url = None):
    """Registers an id and secret for the application for use with the Podium
    API. Should only ever be invoked once per run of program. If invoked more
    than once, a PodiumApplicationAlreadyRegistered exception will be 
    raised.

    Args:
        app_id (string): The UUID for your application as registered with
        the Podium API.

        app_secret (string): The secret for your application as registered with
        the Podium API.
        
        podium_url (String): Optional podium url. defaults to https://podium.live
    """
        
    if PODIUM_APP is not None:
        raise PodiumApplicationAlreadyRegistered()
    else:
        global PODIUM_APP
        PODIUM_APP = PodiumApplication(app_id, app_secret, podium_url=podium_url)

def unregister_podium_application():
    global PODIUM_APP
    PODIUM_APP = None
