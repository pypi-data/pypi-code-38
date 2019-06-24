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

config = {'server':{'host':'localhost', 'port':8889}, 'lspriv':0x1111111111111111111111111111111111111111111111111111111111111112}
syncer=Syncer()
public_static_key = PrivateKey((0x1111111111111111111111111111111111111111111111111111111111111111).to_bytes(32,'big'), raw=True).pubkey.serialize()
syncer.queues['NM'].put( {'action':'open connection', 'host': 'localhost', 'port':8888, 'static_key':public_static_key} )
syncer.queues['NM'].put({'action':'send ping'})
NM_launcher(syncer, config)
