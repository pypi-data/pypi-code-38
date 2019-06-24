from secp256k1_zkp import PrivateKey
from leer.core.lubbadubdub.ioput import IOput
from leer.core.lubbadubdub.address import Address
from leer.core.lubbadubdub.transaction import Transaction
#from leer.core.lubbadubdub.stubs import KeyManager, KeyManagerClass
from leer.tests.storage.storage_for_test import test_storage_space
from leer.tests.chain_tests.block_connect import put_genesis


from leer.tests.storage.storage_for_test import rebuild_test_storage_space
from leer.tests.lubbadubdub.test_transaction import fill_txos, alien_adr1, KeyManager


def test_mempool_tx():
  global test_storage_space
  test_storage_space = rebuild_test_storage_space()
  put_genesis(test_storage_space)
  mempool_tx_addition()
  test_storage_space = rebuild_test_storage_space()
  put_genesis(test_storage_space)
  mempool_tx_contradiction()


def mempool_tx_addition():
  mptx = test_storage_space.mempool_tx
  tx_storage =  test_storage_space.txos_storage
  outputs = fill_txos(tx_storage)
  tx1=Transaction(txos_storage = tx_storage, key_manager = KeyManager)
  tx1.push_input(tx_storage.confirmed[outputs[0].serialized_index])
  tx1.add_destination( (alien_adr1, 3) )
  tx1.generate()
  mptx.add_tx(tx1)
  assert mptx.give_tx().serialize()==tx1.serialize()

  tx2=Transaction(txos_storage = tx_storage, key_manager = KeyManager)
  tx2.push_input(tx_storage.confirmed[outputs[1].serialized_index])
  tx2.add_destination( (alien_adr1, 2) )
  tx2.generate()
  mptx.add_tx(tx2)
  assert mptx.give_tx().serialize()==tx1.merge(tx2).serialize()
  


def mempool_tx_contradiction():
  mptx = test_storage_space.mempool_tx
  tx_storage =  test_storage_space.txos_storage
  outputs = fill_txos(tx_storage)
  tx1=Transaction(txos_storage = tx_storage, key_manager = KeyManager)
  tx1.push_input(tx_storage.confirmed[outputs[0].serialized_index])
  tx1.push_input(tx_storage.confirmed[outputs[1].serialized_index])
  tx1.push_input(tx_storage.confirmed[outputs[2].serialized_index])
  tx1.add_destination( (alien_adr1, 3) )
  tx1.generate()
  #mptx.add_tx(tx1)
  #assert mptx.give_tx().serialize()==tx1.serialize()

  tx2=Transaction(txos_storage = tx_storage, key_manager = KeyManager)
  tx2.push_input(tx_storage.confirmed[outputs[1].serialized_index])
  tx2.push_input(tx_storage.confirmed[outputs[2].serialized_index])
  tx2.add_destination( (alien_adr1, 2) )
  tx2.generate()
  
  mptx.add_tx(tx2)
  mptx.add_tx(tx1)
  #tx2 contradicts with tx1, but tx1 has more inputs
  assert mptx.give_tx().serialize()==tx1.serialize()

