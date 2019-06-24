from leer.tests.storage.storage_for_test import test_storage_space, wipe_test_dirs
#from leer.tests.storage.storage_for_test import HeadersStorage
#from leer.tests.storage.storage_for_test import BlocksStorage
#from leer.tests.storage.storage_for_test import ExcessesStorage

#from leer.tests.storage.storage_for_test import HeadersManager
#from leer.tests.storage.storage_for_test import Blockchain


from leer.core.lubbadubdub.ioput import IOput
from leer.tests.storage.storage_for_test import Transaction
from leer.tests.storage.storage_for_test import rebuild_test_storage_space

from leer.core.primitives.header import Header
from leer.core.primitives.block import generate_genesis, generate_block_template
from leer.core.primitives.transaction_skeleton import TransactionSkeleton

from leer.core.parameters.dynamic import max_reward 
from leer.core.parameters.constants import coinbase_maturity, output_creation_fee, initial_reward



import time
from leer.core.storage.key_manager import KeyManagerClass
from leer.tests.storage.storage_for_test import wallet_path
KeyManager = KeyManagerClass(wallet_path)
address = KeyManager.new_address()

last_coinbase = None

def generate_arbitrary_genesis(storage_space=test_storage_space, key_manager=KeyManager):
  global last_coinbase
  value = max_reward(0)
  coinbase = IOput()
  coinbase.fill(key_manager.new_address(), value, relay_fee = 0, coinbase=True, lock_height = storage_space.blockchain.current_height + 1 + coinbase_maturity)
  coinbase.generate()
  last_coinbase = coinbase
  storage_space.txos_storage.mempool[coinbase.serialized_index]=coinbase
  tx=Transaction(txos_storage = storage_space.txos_storage, key_manager= key_manager)

  tx.add_coinbase(coinbase)

  tx.compose_block_transaction()

  block = generate_genesis(tx, storage_space)

  block.header.nonce=(int.from_bytes(block.header.nonce, "big")+1).to_bytes(16,"big")

  #assert block.verify()
  return block

def put_genesis(storage_space):
  '''
    Some other tests require blockchain with genesis block
  '''
  genesis = generate_arbitrary_genesis()
  storage_space.headers_manager.set_genesis(genesis.header)
  storage_space.headers_manager.context_validation(genesis.header.hash)
  genesis.non_context_verify()
  storage_space.blockchain.add_block(genesis)


def generate_next_block(tx=None, maturity = coinbase_maturity, value = None, coinbase_flag=True, storage_space=test_storage_space, key_manager=KeyManager):
  global last_coinbase
  height = storage_space.blocks_storage[storage_space.blockchain.current_tip].header.height
  value = value if value else max_reward(height+1)
  coinbase = IOput()
  
  #Note we cannot generate transaction where coinbase has bad lock_height. But such malformed tx can be uploaded from tx.
  #Thus for testing we will change tx after generation.
  coinbase.fill(key_manager.new_address(), value, relay_fee = 0, coinbase = coinbase_flag, lock_height = storage_space.blockchain.current_height+1 + coinbase_maturity)
  coinbase.generate()
  last_coinbase = coinbase
  block_tx= Transaction(txos_storage = storage_space.txos_storage, key_manager=key_manager)

  block_tx.add_coinbase(coinbase)
  block_tx.compose_block_transaction(tx)
  block_tx.coinbase.lock_height = storage_space.blockchain.current_height+1 + maturity

  coinbase.version = bool(not coinbase_flag)
  storage_space.txos_storage.mempool[coinbase.serialized_index]=coinbase


  block = generate_block_template(block_tx, storage_space)

  block.header.nonce=(int.from_bytes(block.header.nonce, "big")+1).to_bytes(16,"big")

  #assert block.verify()
  return block

def generate_block_on_top_of(block, tx = None, storage_space=test_storage_space):
  """
    1. Rollback to bifurcation point and append another branch if necessery.
    2. generate_next_block
    3. Rollback to bifurcation point and append first branch
  """
  current_tip = storage_space.blockchain.current_tip
  bif = storage_space.headers_manager.find_bifurcation_point(current_tip, block.hash)
  path, back_path = [], []
  if not bif==current_tip:
    path.append(("ROLLBACK", bif))
    _sc = storage_space.headers_manager.get_subchain(bif, current_tip)
    for bh in _sc:
      back_path.append( ("ADDBLOCK", bh))
  _sc = storage_space.headers_manager.get_subchain(bif, block.hash)
  for bh in _sc:
      path.append( ("ADDBLOCK", bh))
  back_path = [("ROLLBACK", bif)]
  
  storage_space.blockchain.process_path(path)
  new_block = generate_next_block(tx=tx, storage_space=storage_space)
  storage_space.blockchain.process_path(back_path)
  return new_block

import pprint
def nice_print_path(actions, _vars):
  block_dict = {}
  for v in _vars:
    if ("block" in v) and ("transaction_skeleton" in _vars[v].__dict__):
      block_dict[_vars[v].hash] = v
  ret_a =[]
  for _path in actions:
    processed_path = []
    for step in _path:
      processed_path.append( (step[0], block_dict.get(step[1], "unknown: %s"%step[1][:10]) ) )
    ret_a.append(processed_path)
  pp = pprint.PrettyPrinter(indent=2)
  pp.pprint(ret_a)
    
def block_connect_test():
  #
  #
  #        
  #         -> 2 -> 3 -> (a lot of wrong blocks)
  #        |
  #  0-> 1 --> 4 -> 5 ->  6 -> 12
  #        |
  #        |           -> 9
  #        |         /
  #         -> 7 -> 8 --> 10 -> 11 -> 13 -> 14 -> 15
  #
  test_storage_space = rebuild_test_storage_space()
  start = time.time()
  genesis = generate_arbitrary_genesis()
  test_storage_space.headers_manager.set_genesis(genesis.header)
  test_storage_space.headers_manager.context_validation(genesis.header.hash)
  assert genesis.non_context_verify()
  test_storage_space.blockchain.add_block(genesis)
  assert test_storage_space.blocks_storage.is_block_downloaded(genesis.hash)
  assert test_storage_space.blockchain.current_tip == genesis.hash
  assert (test_storage_space.excesses_storage.get_root()[:33] ==
         (genesis.tx.coinbase.address.pubkey + 
          genesis.tx.additional_excesses[0].pubkey).serialize()[:33])

  block1 = generate_next_block()
  test_storage_space.headers_manager.add_header(block1.header)
  test_storage_space.headers_manager.context_validation(block1.header.hash)
  print(test_storage_space.headers_storage[block1.header.hash].reason)
  block1.non_context_verify()#just for building tx
  assert block1.tx.coinbase.serialized_index in test_storage_space.txos_storage.mempool
  test_storage_space.blockchain.add_block(block1)
  assert not (block1.tx.coinbase.serialized_index in test_storage_space.txos_storage.mempool)
  

  block2 = generate_next_block()
  test_storage_space.headers_manager.add_header(block2.header)
  test_storage_space.headers_manager.context_validation(block2.header.hash)
  test_storage_space.blockchain.add_block(block2)

  block3 = generate_next_block()
  test_storage_space.headers_manager.add_header(block3.header)
  test_storage_space.headers_manager.context_validation(block3.header.hash)
  test_storage_space.blockchain.add_block(block3)
  assert test_storage_space.blockchain.current_tip == block3.hash

  #maturity = coinbase_maturity, value = None, coinbase_flag=True
  block_bad_maturity = generate_next_block(maturity=0)
  test_storage_space.headers_manager.add_header(block_bad_maturity.header)
  test_storage_space.headers_manager.context_validation(block_bad_maturity.header.hash)
  try:
    test_storage_space.blockchain.add_block(block_bad_maturity)
  except AssertionError:
    pass
  assert test_storage_space.blockchain.current_tip == block3.hash
  assert test_storage_space.headers_storage[block_bad_maturity.hash].invalid == True

  block_bad_subsidy = generate_next_block(value=initial_reward+1)
  block_bad_subsidy_big = generate_next_block(value=20**8)
  test_storage_space.headers_manager.add_header(block_bad_subsidy.header)
  test_storage_space.headers_manager.add_header(block_bad_subsidy_big.header)
  # headers_manager check only that supply is less than maximal possible at this block
  # we cannot detect on header level `too low supply issue` since supply can be decreased
  # by big number of new outputs which can not be checked by header.
  # The same thing with too big coinbase can be checked 
  test_storage_space.headers_manager.context_validation(block_bad_subsidy.header.hash)
  try:
    test_storage_space.headers_manager.context_validation(block_bad_subsidy_big.header.hash)
    raise Exception("Should be raised before")
  except AssertionError:
    pass

  assert test_storage_space.headers_storage[block_bad_subsidy_big.hash].invalid == True
  assert "Supply is wrong" in test_storage_space.headers_storage[block_bad_subsidy_big.hash].reason
  assert test_storage_space.headers_storage[block_bad_subsidy.hash].invalid == False
  #this addition will not raise, but header become invalid
  test_storage_space.blockchain.add_block(block_bad_subsidy)
  assert test_storage_space.headers_storage[block_bad_subsidy.hash].invalid == True
  assert "failed non-context validation" in test_storage_space.headers_storage[block_bad_subsidy.hash].reason
  

  assert test_storage_space.blockchain.current_tip == block3.hash
  assert test_storage_space.headers_storage[block_bad_subsidy.hash].invalid == True

  # For now block with bad coinbase (when coinbase is regular txout can not be generated)
  # this should be tested
  '''
  block_bad_coinbase = generate_next_block(coinbase_flag=False)
  test_storage_space.headers_manager.add_header(block_bad_coinbase.header)
  test_storage_space.headers_manager.context_validation(block_bad_coinbase.header.hash)
  try:
    test_storage_space.blockchain.add_block(block_bad_coinbase)
  except AssertionError:
    pass
  assert test_storage_space.blockchain.current_tip == block3.hash
  assert test_storage_space.headers_storage[block_bad_coinbase.hash].invalid == True
  '''
  
  block4 = generate_block_on_top_of(block1)
  test_storage_space.headers_manager.add_header(block4.header)
  test_storage_space.headers_manager.context_validation(block4.header.hash)
  test_storage_space.blockchain.add_block(block4)
  assert test_storage_space.blockchain.current_tip == block3.hash

  block5 = generate_block_on_top_of(block4)
  test_storage_space.headers_manager.add_header(block5.header)
  test_storage_space.headers_manager.context_validation(block5.header.hash)
  test_storage_space.blockchain.add_block(block5)

  block6 = generate_block_on_top_of(block5)
  test_storage_space.headers_manager.add_header(block6.header)
  test_storage_space.headers_manager.context_validation(block6.header.hash)
  test_storage_space.blockchain.add_block(block6)
  assert test_storage_space.blockchain.current_tip == block6.hash
 
  block12 = generate_block_on_top_of(block6)
  test_storage_space.headers_manager.add_header(block12.header)
  test_storage_space.headers_manager.context_validation(block12.header.hash)
  test_storage_space.blockchain.add_block(block12)
  assert test_storage_space.blockchain.current_tip == block12.hash
  test_storage_space.blockchain._forget_top() #12
  assert test_storage_space.blockchain.current_tip == block6.hash
  test_storage_space.blockchain._forget_top() # 6
  assert test_storage_space.blockchain.current_tip == block5.hash
  test_storage_space.blockchain._forget_top() # 5
  assert test_storage_space.blockchain.current_tip == block4.hash
  test_storage_space.blockchain._forget_top() # 4
  test_storage_space.blockchain.update(reason="branch was forgotten")
  assert test_storage_space.blockchain.current_tip == block3.hash

  
  block7 = generate_block_on_top_of(block1)
  test_storage_space.headers_manager.add_header(block7.header)
  test_storage_space.headers_manager.context_validation(block7.header.hash)
  test_storage_space.blockchain.add_block(block7)

  block8 = generate_block_on_top_of(block7)
  test_storage_space.headers_manager.add_header(block8.header)
  test_storage_space.headers_manager.context_validation(block8.header.hash)
  test_storage_space.blockchain.add_block(block8)

  block9 = generate_block_on_top_of(block8)
  test_storage_space.headers_manager.add_header(block9.header)
  test_storage_space.headers_manager.context_validation(block9.header.hash)
  test_storage_space.blockchain.add_block(block9)

  #print(nice_print_path(test_storage_space.headers_manager.next_actions(test_storage_space.blockchain.current_tip), vars()))

  # Now block9 is better than block3, but worse than block12. Nevertheless blocks (4, 5, 6, 12)
  # are unavailable 
  assert test_storage_space.blockchain.current_tip == block9.hash

  """
  test_storage_space.blockchain.add_block(block12)
  test_storage_space.blockchain.add_block(block6)
  test_storage_space.blockchain.add_block(block5)
  test_storage_space.blockchain.add_block(block4)
  assert test_storage_space.blockchain.current_tip == block9.hash # transactions are not downloaded yet
  
  for b in [block4, block5, block6, block12]:
    for o in b.tx.outputs:
      test_storage_space.txos_storage.mempool[o.serialized_index]=o
  test_storage_space.blockchain.update(reason="txouts were uploaded")
  
  assert test_storage_space.blockchain.current_tip == block12.hash
  """
  block10 = generate_block_on_top_of(block8)
  test_storage_space.headers_manager.add_header(block10.header)
  test_storage_space.headers_manager.context_validation(block10.header.hash)
  test_storage_space.blockchain.add_block(block10)

  block11 = generate_block_on_top_of(block10)
  test_storage_space.headers_manager.add_header(block11.header)
  test_storage_space.headers_manager.context_validation(block11.header.hash)
  test_storage_space.blockchain.add_block(block11)


  block13 = generate_block_on_top_of(block11)
  test_storage_space.headers_manager.add_header(block13.header)
  test_storage_space.headers_manager.context_validation(block13.header.hash)
  test_storage_space.blockchain.add_block(block13)

  block14 = generate_block_on_top_of(block13)
  test_storage_space.headers_manager.add_header(block14.header)
  test_storage_space.headers_manager.context_validation(block14.header.hash)
  test_storage_space.blockchain.add_block(block14)

  calced_excess_sum = (genesis.tx.coinbase.address.pubkey + genesis.tx.additional_excesses[0].pubkey)
  #0 -> 1 -> 7 -> 8 --> 10 -> 11 -> 13 -> 14 -> 15
  for _block in [block1, block7, block8, block10, block11, block13, block14]:
    calced_excess_sum += _block.tx.coinbase.address.pubkey + _block.tx.additional_excesses[0].pubkey
  assert calced_excess_sum.serialize()==test_storage_space.excesses_storage.get_root()[:33]
  b14_supply = block14.header.supply
  #b14_commitments

  adr1,adr2,adr3,adr4,adr5= [KeyManager.new_address() for i in range(5)]
  assert len(test_storage_space.utxo_index.get_all_unspent(adr1.pubkey))==0
  spend_tx = Transaction(txos_storage = test_storage_space.txos_storage, key_manager=KeyManager)
  spend_tx.push_input(block1.tx.coinbase)
  spend_tx.add_destination((adr1, 10))
  spend_tx.add_destination((adr2, 20))
  spend_tx.add_destination((adr3, 30))
  spend_tx.add_destination((adr3, 30))
  spend_tx.generate(change_address=adr4)
  spend_tx.verify()

  block15 = generate_block_on_top_of(block14, tx=spend_tx)
  new_excess_sum = calced_excess_sum + \
                     last_coinbase.address.pubkey + block15.transaction_skeleton.additional_excesses[0].pubkey +\
                     adr1.pubkey + adr2.pubkey + adr3.pubkey + adr3.pubkey + adr4.pubkey

  assert (new_excess_sum.serialize() == block15.header.merkles[2][:33])
  assert block15.header.supply == b14_supply + max_reward(block15.header.height) - spend_tx.calc_new_outputs_fee(len(spend_tx.inputs), len(spend_tx.outputs))


  test_storage_space.headers_manager.add_header(block15.header)
  test_storage_space.headers_manager.context_validation(block15.header.hash)
  test_storage_space.blockchain.add_block(block15)
  assert test_storage_space.blockchain.current_tip == block15.hash
  assert not test_storage_space.txos_storage.known(block1.tx.coinbase.serialized_index)
  assert len(test_storage_space.utxo_index.get_all_unspent(adr1.pubkey))==1  

  #import pprint
  #pp = pprint.PrettyPrinter(indent=4)
  #pp.pprint(KeyManager.get_confirmed_balance_stats(test_storage_space.utxo_index, test_storage_space.txos_storage, test_storage_space.blockchain.current_height)) #TODO get_confirmed_balance_stats should be checked here

  #combine_tx
  spend_tx16 = Transaction(txos_storage = test_storage_space.txos_storage, key_manager=KeyManager)
  combine_summ = 0 
  for i in range(5):
    combine_summ += spend_tx.outputs[i].value 
    spend_tx16.push_input(spend_tx.outputs[i])
  spend_tx16.add_destination((adr5, 1))
  spend_tx16.generate(change_address=adr5)
  spend_tx16.verify()
  assert spend_tx16.outputs[0].value +spend_tx16.outputs[1].value == combine_summ + output_creation_fee*3
  assert spend_tx16.inputs[0].serialized_index in test_storage_space.txos_storage.confirmed
  test_storage_space.mempool_tx.add_tx(spend_tx16)
  block16 = generate_block_on_top_of(block15, storage_space = test_storage_space)

  test_storage_space.headers_manager.add_header(block16.header)
  test_storage_space.headers_manager.context_validation(block16.header.hash)
  test_storage_space.blockchain.add_block(block16)
  assert test_storage_space.blockchain.current_tip == block16.hash
  assert not test_storage_space.txos_storage.known(spend_tx.outputs[0].serialized_index)
  assert spend_tx16.outputs[0].serialized_index in test_storage_space.txos_storage.confirmed
  assert not spend_tx16.inputs[0].serialized_index in test_storage_space.txos_storage.confirmed
  assert len(test_storage_space.utxo_index.get_all_unspent(adr1.pubkey))==0  
  assert len(test_storage_space.utxo_index.get_all_unspent(adr5.pubkey))==1  

  #pp.pprint(KeyManager.get_confirmed_balance_stats(test_storage_space.utxo_index, test_storage_space.txos_storage, test_storage_space.blockchain.current_height))

  #and now rollback block with actual tx

  block17 = generate_block_on_top_of(block14)
  test_storage_space.headers_manager.add_header(block17.header)
  test_storage_space.headers_manager.context_validation(block17.header.hash)
  test_storage_space.blockchain.add_block(block17)


  block18 = generate_block_on_top_of(block17)
  test_storage_space.headers_manager.add_header(block18.header)
  test_storage_space.headers_manager.context_validation(block18.header.hash)
  test_storage_space.blockchain.add_block(block18)

  block19 = generate_block_on_top_of(block18)
  test_storage_space.headers_manager.add_header(block19.header)
  test_storage_space.headers_manager.context_validation(block19.header.hash)
  test_storage_space.blockchain.add_block(block19)

  assert test_storage_space.blockchain.current_tip == block19.hash
  assert test_storage_space.txos_storage.known(block1.tx.coinbase.serialized_index)
  assert len(test_storage_space.utxo_index.get_all_unspent(adr1.pubkey))==0  
  assert len(test_storage_space.utxo_index.get_all_unspent(adr5.pubkey))==0  
  

  print("Ok", time.time()-start)
