import os
from leer.core.primitives.block import Block
from leer.core.lubbadubdub.transaction import Transaction
from leer.tests.storage.storage_for_test import test_storage_space, wipe_test_dirs
from leer.tests.storage.storage_for_test import rebuild_test_storage_space
from leer.tests.chain_tests.block_connect import generate_arbitrary_genesis, generate_next_block

from leer.core.storage.key_manager import KeyManagerClass
from leer.tests.storage.storage_for_test import wallet_path
KeyManager = KeyManagerClass(wallet_path)


def test_blocks():
  global test_storage_space
  test_storage_space = rebuild_test_storage_space()
  test_block_serialization()

def test_block_serialization():
  genesis = generate_arbitrary_genesis(storage_space=test_storage_space, key_manager=KeyManager)
  test_storage_space.headers_manager.set_genesis(genesis.header)
  test_storage_space.headers_manager.context_validation(genesis.header.hash)
  genesis.non_context_verify()
  genesis_sd=Block(storage_space=test_storage_space)
  genesis_sd.deserialize(genesis.serialize())
  assert genesis.hash==genesis_sd.hash
  test_storage_space.blockchain.add_block(genesis)
  for i in range(10):
    next_block = generate_next_block(storage_space=test_storage_space, key_manager=KeyManager)
    test_storage_space.headers_manager.add_header(next_block.header)
    test_storage_space.headers_manager.context_validation(next_block.header.hash)
    test_storage_space.blockchain.add_block(next_block)
  next_block_sd = Block(storage_space=test_storage_space)
  next_block_sd.deserialize(next_block.serialize())
  assert next_block.hash == next_block_sd.hash

  adr1,adr2,adr3,adr4,adr5= [KeyManager.new_address() for i in range(5)]
  spend_tx = Transaction(txos_storage = test_storage_space.txos_storage, key_manager=KeyManager)
  spend_tx.push_input(genesis.tx.coinbase)
  spend_tx.add_destination((adr1, 10))
  spend_tx.add_destination((adr2, 20))
  spend_tx.add_destination((adr3, 30))
  spend_tx.generate(change_address=adr4)

  block_with_tx = generate_next_block(tx=spend_tx, storage_space=test_storage_space, key_manager=KeyManager)
  test_storage_space.headers_manager.add_header(block_with_tx.header)
  test_storage_space.headers_manager.context_validation(block_with_tx.header.hash)

  block_with_tx_sd = Block(storage_space=test_storage_space)
  poor_serialization = block_with_tx.serialize()
  block_with_tx_sd.deserialize(poor_serialization)
  assert block_with_tx.hash == block_with_tx_sd.hash
  #Rich format
  assert spend_tx.outputs[0].serialized_index in test_storage_space.txos_storage.mempool
  rich_serialization = block_with_tx.serialize(rich_block_format=True)
  test_storage_space.txos_storage.mempool.flush()
  assert not (spend_tx.outputs[0].serialized_index in test_storage_space.txos_storage.mempool)
  block_with_tx_sd.deserialize(rich_serialization)
  assert spend_tx.outputs[0].serialized_index in test_storage_space.txos_storage.mempool
  rich_but_poor_serialization = block_with_tx.serialize(rich_block_format=True, max_size = len(poor_serialization))
  test_storage_space.txos_storage.mempool.flush()
  assert len(rich_but_poor_serialization) == len(poor_serialization)
  block_with_tx_sd.deserialize(rich_but_poor_serialization)
  assert not (spend_tx.outputs[0].serialized_index in test_storage_space.txos_storage.mempool)
  print("test_block_serialization OK")


