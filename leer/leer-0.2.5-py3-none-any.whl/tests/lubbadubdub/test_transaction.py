from secp256k1_zkp import PrivateKey
from leer.core.lubbadubdub.ioput import IOput
from leer.core.lubbadubdub.address import Address
from leer.core.lubbadubdub.transaction import Transaction
from leer.tests.storage.storage_for_test import test_storage_space
from leer.tests.chain_tests.block_connect import put_genesis


from leer.tests.storage.storage_for_test import rebuild_test_storage_space

from leer.core.storage.key_manager import KeyManagerClass
from leer.tests.storage.storage_for_test import wallet_path
KeyManager = KeyManagerClass(wallet_path)


adr1,adr2,adr3,adr4,adr5= [KeyManager.new_address() for i in range(5)]
another_KM=KeyManagerClass(wallet_path+"2")
alien_adr1 = another_KM.new_address()

def test_transaction():
  global test_storage_space
  test_storage_space = rebuild_test_storage_space()
  put_genesis(test_storage_space)
  tx_serialize_deserialize()
  test_storage_space = rebuild_test_storage_space()
  put_genesis(test_storage_space)
  tx_doubled_input()
  #ioput_proofs_info()
  #ioput_encrypted_messsage()

def fill_txos(storage):
  utxo_set = [(adr1, int(1e3*1e8)),(adr2, int(100e3)),(adr3, int(200e3)),(adr4, int(300e3))]
  outputs = []
  for output in utxo_set:
    _output=IOput()
    _output.fill(output[0], output[1])
    _output.generate()
    storage.confirmed.append(_output)
    outputs.append(_output)
  return outputs

def tx_serialize_deserialize():
  tx_storage =  test_storage_space.txos_storage
  outputs = fill_txos(tx_storage)
  tx1=Transaction(txos_storage = tx_storage, key_manager = KeyManager)
  tx1.push_input(tx_storage.confirmed[outputs[0].serialized_index])
  tx1.push_input(tx_storage.confirmed[outputs[1].serialized_index])
  tx1.push_input(tx_storage.confirmed[outputs[2].serialized_index])
  tx1.add_destination( (alien_adr1, 40) )
  tx1.generate()

  tx2=Transaction(raw_tx=tx1.serialize(), txos_storage = tx_storage, key_manager=KeyManager)
  assert tx1.serialize()==tx2.serialize()

  
  """
  #This is example of attack for the case when additional excesses can be signature of empty string
  # thus, address can be transformed to excsess without knowing privkey (proof of knowing actually doesn't proof anything).
  # So basically scheme is as follows:
  # Attacker create output which pays to victim: OutputCommitment: (blinding_key)*G+(private_key)*H,
  # where (private_key)*H is public key (part of address).
  # Attacker doesn't know private_key and thus from first glance can't spend this output.
  # However if attacker manage to create signature for pubkey (-private_key)*H, she can create
  # transaction:
  # Commitment[(blinding_key)*G+(private_key)*H] -> Commitment[(blinding_key)*G +(attacker's_address)] + AdditionalExcsess[(-private_key)*H]
  # THis vulnerability is closed by forcing every address to be proven by signing empty string, and every additional excess by signing one of
  # transaction output.
  for i in tx1.outputs:
    if i.value==40:
      target_output = i
  tx_storage.confirmed[target_output.serialized_index]=target_output
  from secp256k1_zkp import PrivateKey, PedersenCommitment, RangeProof
  another_pk = PrivateKey()
  address_f = Address()
  address_f.from_private_key(another_pk)
  output = IOput()
  output.fill(address_f, 40, blinding_key=target_output.blinding_key)
  output.generate()
  inverse_alien_adr1 = Address() 
  inverse_alien_adr_pk = -another_KM.priv_by_address(alien_adr1)
  inverse_alien_adr1.from_private_key(inverse_alien_adr_pk)
  tx_attack = Transaction(txos_storage = tx_storage, key_manager = KeyManager)
  tx_attack.inputs = [target_output]
  tx_attack.outputs = [output]
  tx_attack.additional_excesses = [inverse_alien_adr1]
  assert target_output.value == output.value
  #sum(inputs)+sum(additional_excesses)+sum(outputs_excesses)+sum(minted_coins) == sum(outputs) + sum(fee)
  assert (target_output.blinding_key+another_KM.priv_by_address(alien_adr1)+inverse_alien_adr_pk+another_pk).serialize() == \
         (output.blinding_key + another_pk).serialize()
  from leer.core.lubbadubdub.constants import default_generator
  pc=PedersenCommitment(blinded_generator=default_generator)
  pc2=PedersenCommitment(blinded_generator=default_generator)
  pc.create(40, (target_output.blinding_key+another_KM.priv_by_address(alien_adr1)).private_key)
  assert target_output.authorized_pedersen_commitment.serialize() == pc.serialize()
  print("\n"*5,"target_output computed", pc.serialize())
  print("inverse_alien_adr_pk", inverse_alien_adr_pk.pubkey.to_pedersen_commitment().serialize())
  print("another_pk", another_pk.pubkey.to_pedersen_commitment().serialize())
  pc2.create(40, (target_output.blinding_key+another_pk).private_key)
  assert output.authorized_pedersen_commitment.serialize() == pc2.serialize()
  print("output apc computed", pc2.serialize())
  pc = (pc.to_public_key() +  inverse_alien_adr_pk.pubkey + another_pk.pubkey).to_pedersen_commitment()
  tx_attack.verify()
  """

def tx_doubled_input():
  tx_storage =  test_storage_space.txos_storage
  outputs = fill_txos(tx_storage)
  tx1=Transaction(txos_storage = tx_storage, key_manager = KeyManager)
  tx1.inputs = [tx_storage.confirmed[outputs[0].serialized_index], tx_storage.confirmed[outputs[0].serialized_index] ]
  tx1.add_destination( (alien_adr1, 1) )
  tx2=Transaction(txos_storage = tx_storage, key_manager = KeyManager)
  tx2.inputs = [tx_storage.confirmed[outputs[1].serialized_index]]
  tx2.add_destination( (alien_adr1, 1) )
  tx2.generate()
  try:
    tx1.generate()
    raise Exception("Double spend")
  except AssertionError as e:
    pass

