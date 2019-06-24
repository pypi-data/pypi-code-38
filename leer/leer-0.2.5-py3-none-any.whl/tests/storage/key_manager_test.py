from secp256k1_zkp import PrivateKey
from leer.core.storage.key_manager import KeyManagerClass
from leer.tests.storage.storage_for_test import wipe_test_dirs, wallet_path
from leer.core.shared_contexts import shared_ctx

def test_key_manager():
  wipe_test_dirs()
  km = KeyManagerClass(path=wallet_path)
  km.fill_pool(100)
  km2 = KeyManagerClass(path=wallet_path)
  assert km2.pool_size == 100
  wipe_test_dirs()
  km = KeyManagerClass(path=wallet_path)
  assert not km.pool_size
  random_key = PrivateKey(ctx=shared_ctx)
  try:
    km.priv_by_pub(random_key.pubkey)
    raise AssertionError("Key manager should raise KeyError")
  except KeyError:
    pass
  km.add_privkey(random_key)
  assert km.priv_by_pub(random_key.pubkey).private_key == random_key.private_key
    
  yark=PrivateKey(ctx=shared_ctx) #yet another random key
  km.wallet.add_privkey_to_pool(yark.pubkey.serialize(), yark.private_key)
  assert km.pool_size == 1
  extracted_key =  PrivateKey( km.wallet.get_privkey_from_pool() , raw=True, ctx=shared_ctx)
  assert extracted_key.private_key == yark.private_key
  assert km.pool_size == 0

  yark2=PrivateKey(ctx=shared_ctx) #yet another random key
  km.wallet.add_privkey_to_pool(yark2.pubkey.serialize(), yark2.private_key)
  assert km.pool_size == 1
  new_address = km.new_address()
  assert km.pool_size == 1
  assert new_address.pubkey.serialize()==yark2.pubkey.serialize()
  km.wallet.get_privkey_from_pool()
  assert km.pool_size == 0

  yark3=PrivateKey(ctx=shared_ctx) #yet another random key
  yark4=PrivateKey(ctx=shared_ctx) #yet another random key
  km.wallet.add_privkey_to_pool(yark3.pubkey.serialize(), yark3.private_key)
  km.wallet.add_privkey_to_pool(yark4.pubkey.serialize(), yark4.private_key)
  assert km.pool_size == 2
  new_address1 = km.new_address()
  new_address2 = km.new_address()
  assert km.pool_size == 2
  assert new_address1.pubkey.serialize()==yark3.pubkey.serialize()
  assert new_address2.pubkey.serialize()==yark4.pubkey.serialize()

  return True

