#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 15:13:04 2018

@author: andrew
"""

import requests
from authorization import get_authorization

def get_proposals(username, password):
    auth = get_authorization(username, password)
    if auth != None:
        proposals = []
        r = requests.get('https://observe.lco.global/api/proposals', headers=auth).json()
        results = r['results']
        num_proposals = len(results)
        for i in range(num_proposals):
            proposals.append(results[i]['id'])
        return proposals