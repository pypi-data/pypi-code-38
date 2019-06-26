import requests
import os
import json
from .init import get_config

def updateCustomerGeneralData(bank_id=None, customer_id=None, customer_general_data=None):
  """
  Update customer general_data

  """

  payload = {
      "customer_general_data": customer_general_data
    }

  url = get_config('OBP_API_HOST') + '/obp/v3.1.0/banks/bnpp-irb.01.dz.dz/customers/{customer_id}/general-data'.format(bank_id=bank_id, customer_id=customer_id)

  authorization = 'DirectLogin token="{}"'.format(get_config('OBP_AUTH_TOKEN'))
  headers = {'Content-Type': 'application/json',
            'Authorization': authorization}
  req = requests.post(url, headers=headers, json=payload)

  return req
