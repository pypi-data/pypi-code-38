import asyncio
import logging
from functools import partial

from secp256k1_zkp import PrivateKey, PublicKey
from leer.syncer import Syncer
from leer.transport.network_manager import NM_launcher
from leer.rpc.rpc_manager import RPCM_launcher
from leer.core.core_loop import core_loop
import multiprocessing
import time

from os.path import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')

def p2p_port_by_id(server_id):
  return 8888+server_id

def rpc_port_by_id(server_id):
  return p2p_port_by_id(server_id)+350

def priv_key_by_id(server_id):
  return 0x1111111111111111111111111111111111111111111111111111111111111111 + server_id

def pub_key_by_id(server_id):
  return PrivateKey((priv_key_by_id(server_id)).to_bytes(32,'big'), raw=True).pubkey.serialize()

def basedir_by_id(server_id):
  home = expanduser("~")
  base_dir = join(home, ".leertest")
  return join(base_dir, str(server_id))

def config_generator(server_id):
    config = {'p2p':{'host':'0.0.0.0', 'port':p2p_port_by_id(server_id), 'lspriv':priv_key_by_id(server_id)},
              'rpc':{'host':'0.0.0.0', 'port':rpc_port_by_id(server_id)},
              'location':{'basedir':basedir_by_id(server_id)}
             }
    return config


async def start_server(server_id, connected_to, delay_before_connect=5):
    if not isinstance(server_id, int) or not (0<=server_id<=300):
      raise Exception("Server id should be integer between 0 and 300")
    if not isinstance(connected_to, list):
      raise Exception("connected_to is list which contains id of servers")
    config = config_generator(server_id)
    syncer=Syncer()
    #NM_launcher(syncer, config)
    nm = multiprocessing.Process(target=NM_launcher, args=(syncer, config))
    nm.start()
    rpcm = multiprocessing.Process(target=RPCM_launcher, args=(syncer, config))
    rpcm.start()
    core = multiprocessing.Process(target=core_loop, args=(syncer, config))
    core.start()
    await asyncio.sleep(delay_before_connect)
    for node in connected_to:
      print("Require connection from %d to %d: %s:%s:%s"%(server_id, node, 'localhost', p2p_port_by_id(node), pub_key_by_id(node)))
      syncer.queues['NetworkManager'].put(
        {'action':'open connection', 
         'host':'localhost','port':p2p_port_by_id(node),
         'static_key':pub_key_by_id(node), 
         'id':int((time.time()*1e5)%1e5),
         'sender': "RPC"})
    while True:
      await asyncio.sleep(delay_before_connect)
      syncer.queues['NetworkManager'].put({'action':'print connection num'})
