import requests
import os
import json
from .init import get_config

def createBank(bankname=None, email=None, password=None, 
                first_name=None, last_name=None):

## TODO 
"""
curl -X POST http://127.0.0.1:8080/obp/v3.1.0/banks -H 'Content-Type: application/json' -H 'Authorization: DirectLogin token="eyJhbGciOiJIUzI1NiJ9.eyIiOiIifQ.PKtmuOn_1NDWJeAIB1ecVxFUDk3_MV4AaNA9UbURGEc"' -d '{  "id":"gh.29.uk.x",  "full_name":"uk",  "short_name":"uk",  "logo_url":"https://static.openbankproject.com/images/sandbox/bank_x.png",  "website_url":"https://www.example.com",  "swift_bic":"IIIGGB22",  "national_identifier":"UK97ZZZ1234567890",  "bank_routing":{    "scheme":"BIC",    "address":"OKOYFIHH"  }}'
"""
## TODO

  payload = {
    }
  
  url = get_config('OBP_API_HOST') + '/obp/v3.1.0/.....'
  
  authorization = 'DirectLogin token="{}"'.format(get_config('OBP_AUTH_TOKEN'))
  headers = {'Content-Type': 'application/json',
            'Authorization': authorization}
  req = requests.post(url, headers=headers, json=payload)

  return req
