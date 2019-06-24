import asyncio
import logging
from functools import partial
from node import NetworkNode
from syncer import SyncerTestStub as Syncer

from lightning_noise.lightning_noise import Key
from secp256k1 import PrivateKey, PublicKey
from network_manager import NM_launcher

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s:%(message)s')

config = {'server':{'host':'localhost', 'port':8890}, 'lspriv':0x1111111111111111111111111111111111111111111111111111111111111122}
syncer=Syncer()
public_static_key = Key(key=PrivateKey((0x1111111111111111111111111111111111111111111111111111111111111111).to_bytes(32,'big'), raw=True)).pubkey()
syncer.queues['NM'].append( {'action':'open connection', 'host': 'localhost', 'port':8888, 'static_key':public_static_key} )
syncer.queues['NM'].append({'action':'send ping'})
NM_launcher(syncer, config)
