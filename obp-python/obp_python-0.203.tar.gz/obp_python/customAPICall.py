import requests
import os
import json
from .init import get_config

def customAPICall(endpoint=None, method=None, payload=None):
  """
  Make a custom api call
  """
  payload = payload

  OBP_AUTH_TOKEN = get_config('OBP_AUTH_TOKEN')
  OBP_API_HOST = get_config('OBP_API_HOST')

  authorization = 'DirectLogin token="{}"'.format(get_config('OBP_AUTH_TOKEN'))
  headers = {'Content-Type': 'application/json',
            'Authorization': authorization}


  url = get_config('obp_api_host') + '/{endpoint}'.format(endpoint=endpoint)

  if payload is None:
    req = requests.get(url, headers=headers)
  elif method == "POST":
    req = requests.post(url, headers=headers, json=payload)
  elif method == "PUT":
    req = requests.put(url, headers=headers, json=payload)
  elif method == "DELETE":
    req = requests.put(url, headers=headers )
  return req
