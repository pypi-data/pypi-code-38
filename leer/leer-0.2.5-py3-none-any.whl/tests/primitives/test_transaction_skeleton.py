from leer.core.primitives.transaction_skeleton import TransactionSkeleton

from secp256k1_zkp import PrivateKey
from leer.core.lubbadubdub.ioput import IOput
from leer.core.lubbadubdub.address import Address
from leer.core.lubbadubdub.transaction import Transaction
from leer.core.storage.txos_storage import TXOsStorage
from leer.tests.storage.storage_for_test import test_storage_space, wipe_test_dirs

from leer.tests.chain_tests.block_connect import put_genesis


from leer.tests.storage.storage_for_test import rebuild_test_storage_space

from leer.core.storage.key_manager import KeyManagerClass
from leer.tests.storage.storage_for_test import wallet_path
KeyManager = KeyManagerClass(wallet_path)

adr1,adr2,adr3,adr4,adr5= [KeyManager.new_address() for i in range(5)]
another_KM=KeyManagerClass(wallet_path+"2")
alien_adr1 = another_KM.new_address()

def test_transaction_skeleton():
  global test_storage_space
  test_storage_space = rebuild_test_storage_space()
  put_genesis(test_storage_space)
  tx_skeleton_serialize_deserialize()
  #ioput_proofs_info()
  #ioput_encrypted_messsage()

def fill_txos(storage):
  utxo_set = [(adr1, int(1e3*1e8)),(adr2, 100),(adr3, 200),(adr4, 300)]
  outputs = []
  for output in utxo_set:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.confirmed[_output.serialized_index]=_output
    outputs.append(_output)
  return outputs

def generate_tx():
  tx_storage =  test_storage_space.txos_storage

  outputs = fill_txos(tx_storage)
  tx1=Transaction(txos_storage = tx_storage, key_manager=KeyManager)
  tx1.push_input(tx_storage.confirmed[outputs[0].serialized_index])
  tx1.push_input(tx_storage.confirmed[outputs[1].serialized_index])
  tx1.push_input(tx_storage.confirmed[outputs[2].serialized_index])
  tx1.add_destination( (alien_adr1, 40) )
  tx1.generate()

  return tx1

def tx_skeleton_serialize_deserialize():
  tx = generate_tx()
  skeleton = TransactionSkeleton(tx=tx)
  skeleton_sd = TransactionSkeleton()
  skeleton_sd.deserialize(skeleton.serialize())
  assert skeleton == skeleton_sd

