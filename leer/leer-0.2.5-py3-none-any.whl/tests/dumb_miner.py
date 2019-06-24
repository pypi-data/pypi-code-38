from leer.core.primitives.header import Header

from leer.core.hash.mining_canary import mining_canary_hash


import requests
import json
import base64
from time import time, sleep

def p2p_port_by_id(server_id):
  return 8888+server_id

def rpc_port_by_id(server_id):
  return p2p_port_by_id(server_id)+350

def basic_request(server_id, method, params=[]):
   url = "http://0.0.0.0:%d"%(rpc_port_by_id(server_id))
   headers = {'content-type': 'application/json'} 
   payload = {
               "method": method,
               "params": params,
               "jsonrpc": "2.0",
               "id": 0,
             }
   response = requests.post( url, data=json.dumps(payload), headers=headers)
   result = json.loads(response.text)
   if 'error' in result:
     raise Exception(result['error'])
   return result['result']

def check_solution(partial_template, int_nonce, target):
  _hash = mining_canary_hash(partial_template+int_nonce.to_bytes(16,'big'))
  if int.from_bytes(_hash, "big") < target:
    return True
  return False 


def start_mining(server_id, after_block_delay = 0):
  while True:
    print("Start mining new block")
    initial_time = time()
    block_template = basic_request(server_id, 'getblocktemplate')
    block_template = base64.b64decode(block_template.encode())
    header = Header()
    header.deserialize(block_template)
    print("Got template. Block height %d. Block target %d (* 2**220). Average hashes for block %d. Block timestamp %d"%(header.height,header.target/2**220, 2**256/header.target, header.timestamp)) 
     
    partial_template = block_template[:-16]
    nonce = 0
    next_level=4096
    while not check_solution(partial_template, nonce, header.target):
      nonce+=1
      if not nonce%next_level:
        next_level*=2
        print("Nonce reached %d"%nonce)
    final_time = time()
    print("Get solution. Nonce = %d. Hashrate %d H/s"%(nonce, int(nonce/(final_time-initial_time))))
    solution =partial_template +nonce.to_bytes(16,'big')
    encoded_solution = base64.b64encode(solution).decode()
    res = basic_request(server_id, 'validatesolution', [encoded_solution])
    print("Submitted block. Result %s"%res)
    sleep(after_block_delay)
