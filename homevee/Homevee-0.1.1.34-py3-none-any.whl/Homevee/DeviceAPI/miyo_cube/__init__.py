#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib.error
import urllib.parse
import urllib.request


def get_api_key(cube_ip):
    contents = urllib.request.urlopen("http://"+cube_ip+"/api/link").read()

    data = json.loads(contents)

    if(data['status'] == 'success'):
        api_key = data['apiKey']

        #save_api_key

        return True
    elif(data['status'] == 'error'):
        #maybe forgot to press button?
        return False