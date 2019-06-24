import shutil, os, time
from secp256k1_zkp import PrivateKey

from leer.core.lubbadubdub.ioput import IOput
from leer.core.lubbadubdub.address import Address
from leer.tests.storage.storage_for_test import test_storage_space, wipe_test_dirs, rebuild_test_storage_space, generate_arbitrary_storage_space, txo_storage_path
from leer.core.storage.txos_storage import TXOsStorage

from leer.core.storage.key_manager import KeyManagerClass
from leer.tests.storage.storage_for_test import wallet_path
KeyManager = KeyManagerClass(wallet_path)

def test_txo_storage():
  wipe_test_dirs()
  test_empty_storage()
  wipe_test_dirs()
  test_shared_state()
  wipe_test_dirs()
  test_addition_to_confirmed()
  wipe_test_dirs()
  test_addition_to_mempool()
  wipe_test_dirs()
  test_deletion_from_confirmed()
  wipe_test_dirs()
  test_movement_from_mempool_to_confirmed()
  wipe_test_dirs()
  test_known()
  wipe_test_dirs()
  test_spend()
  wipe_test_dirs()
  test_spend_revert()
  wipe_test_dirs()


def test_empty_storage():
  test_storage_space = rebuild_test_storage_space()
  storage = test_storage_space.txos_storage
  assert storage.confirmed.get_commitment_root()==b"\x00"*65
  assert storage.confirmed.get_txo_root()==b"\x00"*65
  print("test_empty_storage OK")



def test_addition_to_confirmed():
  test_storage_space = rebuild_test_storage_space()
  storage = test_storage_space.txos_storage

  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x11\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr1 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x12\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr2 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x13\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr3 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x14\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr4 = Address().from_private_key(privkey)

  _set = [(adr1, int(1e3*1e8)),(adr2, 100),(adr3, 200),(adr4, 300)]

  _indexes=[]
  for output in _set:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.confirmed[_output.serialized_index]=_output
    _indexes.append(_output.serialized_index)

  for _index in _indexes:
    assert _index in storage.confirmed
  assert storage.confirmed.get_commitment_root()
  assert storage.confirmed.get_txo_root()
  print("test_addition_to_confirmed OK")


def test_shared_state():
  test_storage_space = rebuild_test_storage_space()
  storage1 = test_storage_space.txos_storage
  # storage1 and storage1_but_another are different objects but should be borgs with the same state
  storage1_but_another = TXOsStorage(test_storage_space, txo_storage_path)

  test_storage_space2 = generate_arbitrary_storage_space("2")
  storage2 = test_storage_space2.txos_storage

  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x11\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr1 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x12\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr2 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x13\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr3 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x14\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr4 = Address().from_private_key(privkey)

  _set = [(adr1, int(1e3*1e8)),(adr2, 100),(adr3, 200),(adr4, 300)]

  _indexes=[]
  for output in _set:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage1.confirmed[_output.serialized_index]=_output
    _indexes.append(_output.serialized_index)

  for _index in _indexes:
    assert _index in storage1_but_another.confirmed
    assert not _index in storage2.confirmed

  print("test_shared_state OK")

def test_addition_to_mempool():
  test_storage_space = rebuild_test_storage_space()
  storage = test_storage_space.txos_storage

  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x11\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr1 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x12\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr2 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x13\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr3 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x14\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr4 = Address().from_private_key(privkey)

  _set = [(adr1, int(1e3*1e8)),(adr2, 100),(adr3, 200),(adr4, 300)]

  _indexes=[]
  for output in _set:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.mempool[_output.serialized_index]=_output
    _indexes.append(_output.serialized_index)

  for _index in _indexes:
    assert _index in storage.mempool
  print("test_addition_to_mempool OK")


def test_deletion_from_confirmed():
  test_storage_space = rebuild_test_storage_space()
  storage = test_storage_space.txos_storage
  assert storage.confirmed.get_commitment_root()==b"\x00"*65

  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x11\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr1 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x12\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr2 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x13\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr3 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x14\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr4 = Address().from_private_key(privkey)

  _set = [(adr1, int(1e3*1e8)),(adr2, 100),(adr3, 200),(adr4, 300)]

  _indexes = []
  _comm_indexes = []
  for output in _set:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.confirmed[_output.serialized_index]=_output
    _indexes.append(_output.serialized_index)
    _comm_indexes.append(_output.commitment_index)


  storage.confirmed.remove(3)
  assert storage.confirmed.get_commitment_root()==_comm_indexes[0]
  assert not _indexes[1] in storage.confirmed
  print("test_deletion_from_confirmed OK")


def test_movement_from_mempool_to_confirmed():
  test_storage_space = rebuild_test_storage_space()
  storage = test_storage_space.txos_storage

  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x11\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr1 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x12\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr2 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x13\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr3 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x14\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr4 = Address().from_private_key(privkey)

  _set = [(adr1, int(1e3*1e8)),(adr2, 100),(adr3, 200),(adr4, 300)]

  _indexes=[]
  for output in _set:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.mempool[_output.serialized_index]=_output
    _indexes.append(_output.serialized_index)

  for _index in _indexes:
    storage.confirm(_index)
    assert not _index in storage.mempool
    assert _index in storage.confirmed
  print("test_movement_from_mempool_to_confirmed OK")


def test_known():
  test_storage_space = rebuild_test_storage_space()
  storage = test_storage_space.txos_storage

  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x11\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr1 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x12\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr2 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x13\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr3 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x14\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr4 = Address().from_private_key(privkey)

  _set = [(adr1, int(1e3*1e8)),(adr2, 100),(adr3, 200),(adr4, 300)]

  _indexes=[]
  for output in _set[:2]:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.mempool[_output.serialized_index]=_output
    _indexes.append(_output.serialized_index)
  for output in _set[2:]:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.confirmed[_output.serialized_index]=_output
    _indexes.append(_output.serialized_index)

  for _index in _indexes:
    assert storage.known(_index)
  print("test_known OK")



def test_spend():
  test_storage_space = rebuild_test_storage_space()
  storage = test_storage_space.txos_storage

  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x11\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr1 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x12\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr2 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x13\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr3 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x14\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr4 = Address().from_private_key(privkey)

  _set = [(adr1, int(1e3*1e8)),(adr2, 100),(adr3, 200),(adr4, 300)]

  _outputs=[]
  
  for output in _set:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.confirmed[_output.serialized_index]=_output
    _outputs.append(_output)

  storage.confirmed.spend(_outputs[-1])

  for _output in _outputs[:-1]:
    _index = _output.serialized_index
    assert storage.known(_index)

  assert not storage.known(_outputs[-1].serialized_index)

  print("test_spend OK")


def test_spend_revert():
  test_storage_space = rebuild_test_storage_space()
  storage = test_storage_space.txos_storage

  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x11\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr1 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x12\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr2 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x13\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr3 = Address().from_private_key(privkey)
  privkey = PrivateKey(b'\xbe\xf2%\x18\xefU\x14\xc3\x86\xe0?.\x8d\xd3\xdf\xb8\xae+\xc2|\x98\x82\xf50\x89>.\xa6\x07\x10\x841', raw=True)
  adr4 = Address().from_private_key(privkey)

  _set = [(adr1, int(1e3*1e8)),(adr2, 100),(adr3, 200),(adr4, 300)]

  _outputs=[]
  
  for output in _set:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.confirmed[_output.serialized_index]=_output
    _outputs.append(_output)

  revert_obj = storage.confirmed.spend(_outputs[-1], return_revert_obj =True)

  for _output in _outputs[:-1]:
    _index = _output.serialized_index
    assert storage.known(_index)

  assert not storage.known(_outputs[-1].serialized_index)

  storage.confirmed.unspend(revert_obj)
  assert storage.known(_outputs[-1].serialized_index)

  print("test_spend OK")

