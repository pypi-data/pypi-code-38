from leer.core.primitives.header import Header, PoPoW, VoteData, ContextHeader
from leer.core.lubbadubdub.address import Excess
from leer.tests.storage.storage_for_test import HeadersStorage
from leer.tests.storage.storage_for_test import HeadersManager

from leer.core.parameters.dynamic import max_reward, initial_target
import shutil, time

from leer.tests.storage.storage_for_test import test_storage_space, wipe_test_dirs, rebuild_test_storage_space

from secp256k1_zkp import PrivateKey, PublicKey, PedersenCommitment
from leer.core.shared_contexts import shared_ctx
from leer.core.lubbadubdub.constants import default_generator

def generate_merkles_for_supply(supply):
  '''
    Generate merkles such as 
     supply*G (calculated from supply) +excesses_root =commitments_root
  '''
  arbitrary_privkey = PrivateKey(ctx=shared_ctx)
  er = arbitrary_privkey.pubkey
  cr = PedersenCommitment(blinded_generator = default_generator, ctx=shared_ctx)
  cr.create(supply, arbitrary_privkey.private_key)
  return [cr.serialize()+b"\x01"*32, b"\x02"*32, er.serialize()+b"\x03"*32]

def headers_chains_test():
  #
  #
  #                /-> h11 =>h13 =>h14
  #               /            /=> h16(inv)
  #              |-> h10 => h12 =>h15(inv)
  #  genesis => h1  => h2
  #              \ 
  #		  h3  => h4 => h9
  #                 \ h5(inv) => h6 => h7 => h8

  test_storage_space = rebuild_test_storage_space()
  merkles=generate_merkles_for_supply(max_reward(0))
  genesis_header=Header(0, max_reward(0), merkles, PoPoW([]), VoteData(), int(time.time()), initial_target, 1, b"\x00"*15+b"\x00")
  #print("genesis head hash %s"%genesis_header.hash)
  hm=test_storage_space.headers_manager
  hm.set_genesis(genesis_header)
  assert test_storage_space.headers_storage[genesis_header.hash].connected_to_genesis
  assert not test_storage_space.headers_storage[genesis_header.hash].invalid
  assert test_storage_space.headers_storage[genesis_header.hash].descendants==set([])


  #header(height, supply, merkles, popow, votedata, timestamp, target, version, nonce)
  merkles=generate_merkles_for_supply(max_reward(1)+genesis_header.supply)
  h1 = Header(1, max_reward(1)+genesis_header.supply, merkles, genesis_header.next_popow(), VoteData(), int(time.time()+1), initial_target, 1, b"\x00"*15+b"\x01")
  merkles=generate_merkles_for_supply(max_reward(2)+h1.supply)
  h2  = Header(2    , max_reward(2)+h1.supply, merkles, h1.next_popow(), VoteData(), int(time.time()+2), initial_target, 1, b"\x00"*15+b"\x02")
  merkles=generate_merkles_for_supply(max_reward(2)+h1.supply)
  h3  = Header(2    , max_reward(2)+h1.supply, merkles, h1.next_popow(), VoteData(), int(time.time()+2), initial_target, 1, b"\x00"*15+b"\x03")
  merkles=generate_merkles_for_supply(max_reward(3)+h3.supply)
  h4  = Header(3    , max_reward(3)+h3.supply, merkles, h3.next_popow(), VoteData(), int(time.time()+3), initial_target, 1, b"\x00"*15+b"\x04")
  merkles=generate_merkles_for_supply(max_reward(0)+h3.supply)
  h5  = Header(10000, max_reward(0)+h3.supply, merkles, h3.next_popow(), VoteData(), int(time.time()+9), initial_target, 1, b"\x00"*15+b"\x05")
  merkles=generate_merkles_for_supply(max_reward(0)+h5.supply)
  h6  = Header(10001, max_reward(0)+h5.supply, merkles, h5.next_popow(), VoteData(), int(time.time()+9), initial_target, 1, b"\x00"*15+b"\x06")
  merkles=generate_merkles_for_supply(max_reward(0)+h6.supply)
  h7  = Header(10002, max_reward(0)+h6.supply, merkles, h6.next_popow(), VoteData(), int(time.time()+9), initial_target, 1, b"\x00"*15+b"\x07")
  merkles=generate_merkles_for_supply(max_reward(0)+h7.supply)
  h8  = Header(10003, max_reward(0)+h7.supply, merkles, h7.next_popow(), VoteData(), int(time.time()+9), initial_target, 1, b"\x00"*15+b"\x08")
  merkles=generate_merkles_for_supply(max_reward(4)+h4.supply)
  h9  = Header(4    , max_reward(4)+h4.supply, merkles, h4.next_popow(), VoteData(), int(time.time()+4), initial_target, 1, b"\x00"*15+b"\x09")
  merkles=generate_merkles_for_supply(max_reward(2)+h1.supply)
  h10 = Header(2    , max_reward(2)+h1.supply, merkles, h1.next_popow(), VoteData(), int(time.time()+2), initial_target, 1, b"\x00"*15+b"\x0a")
  merkles=generate_merkles_for_supply(max_reward(2)+h1.supply)
  h11 = Header(2    , max_reward(2)+h1.supply, merkles, h1.next_popow(), VoteData(), int(time.time()+2), initial_target, 1, b"\x00"*15+b"\x0b")
  merkles=generate_merkles_for_supply(max_reward(3)+h10.supply)
  h12 = Header(3    , max_reward(3)+h10.supply, merkles, h10.next_popow(), VoteData(), int(time.time()+3), initial_target, 1, b"\x00"*15+b"\x0c")
  merkles=generate_merkles_for_supply(max_reward(3)+h11.supply)
  h13 = Header(3    , max_reward(3)+h11.supply, merkles, h11.next_popow(), VoteData(), int(time.time()+3), initial_target, 1, b"\x00"*15+b"\x0d")
  merkles=generate_merkles_for_supply(max_reward(4)+h13.supply)
  h14 = Header(4    , max_reward(4)+h13.supply, merkles, h13.next_popow(), VoteData(), int(time.time()+4), initial_target, 1, b"\x00"*15+b"\x0d")
  merkles=generate_merkles_for_supply(max_reward(4)+h12.supply)
  h15 = Header(4    , max_reward(4)+h12.supply, merkles, h12.next_popow(), VoteData(), int(time.time()+4), initial_target, 1, b"\x00"*15+b"\x0d")
  h15.popow.pointers=h15.popow.pointers[:1]+[b"\xff"*32]+h15.popow.pointers[1:]
  merkles=generate_merkles_for_supply(max_reward(4)+h12.supply)
  h16 = Header(4    , max_reward(4)+h12.supply, merkles, h12.next_popow(), VoteData(), int(time.time()+4), initial_target, 1, b"\x00"*15+b"\x0d")
  h16.popow.pointers=h16.popow.pointers[:-1]+[b"\xff"*32]


  hm.add_header(h1)
  assert test_storage_space.headers_storage[genesis_header.hash].descendants==set([h1.hash])
  assert test_storage_space.headers_storage[h1.hash].connected_to_genesis




  hm.add_header(h2)
  assert test_storage_space.headers_storage[h1.hash].descendants==set([h2.hash])
  assert test_storage_space.headers_storage[h2.hash].connected_to_genesis
  hm.add_header(h4)

  assert (not test_storage_space.headers_storage[h4.hash].connected_to_genesis)
  assert (not test_storage_space.headers_storage[h4.hash].invalid)

  hm.add_header(h3)

  assert (test_storage_space.headers_storage[h4.hash].connected_to_genesis)
  assert (not test_storage_space.headers_storage[h4.hash].invalid)
  assert test_storage_space.headers_storage[h1.hash].descendants==set([h2.hash, h3.hash])
  assert test_storage_space.headers_storage[h3.hash].descendants==set([h4.hash])

  hm.add_header(h7)
  assert (not test_storage_space.headers_storage[h7.hash].connected_to_genesis)
  assert (not test_storage_space.headers_storage[h7.hash].invalid)
  hm.add_header(h6)
  assert (not test_storage_space.headers_storage[h7.hash].connected_to_genesis)
  assert (not test_storage_space.headers_storage[h7.hash].invalid)
  assert (not test_storage_space.headers_storage[h6.hash].connected_to_genesis)
  assert (not test_storage_space.headers_storage[h6.hash].invalid)
  assert (test_storage_space.headers_storage[h6.hash].descendants==set([h7.hash]))
  hm.add_header(h5)
  assert (test_storage_space.headers_storage[h7.hash].connected_to_genesis)
  assert (test_storage_space.headers_storage[h7.hash].invalid)
  assert (test_storage_space.headers_storage[h7.hash].reason=="Block height is out of sequence")
  assert (test_storage_space.headers_storage[h5.hash].connected_to_genesis)
  assert (test_storage_space.headers_storage[h5.hash].invalid)
  assert (test_storage_space.headers_storage[h5.hash].reason=="Block height is out of sequence")

  hm.add_header(h9)
  assert hm.best_tip[1]==4
  assert hm.best_tip[0]==h9.hash
  # Obsolete API has changed
  #assert hm.next_actions(h2.hash)==[("ROLLBACK", h1.hash), ("ADDBLOCK", h3.hash), ("ADDBLOCK", h4.hash), ("ADDBLOCK", h9.hash) ]

  hm.mark_subchain_invalid(h3.hash, "I said so")
  assert hm.best_tip[1]==2
  assert hm.best_tip[0]==h2.hash
  # Obsolete API has changed
  #assert hm.next_actions(h9.hash)==[("ROLLBACK", h1.hash), ("ADDBLOCK", h2.hash)]

  (h10, h11) = (h10,h11) if h10.hash>h11.hash else (h11,h10)
  hm.add_header(h10)
  hm.add_header(h11)
  hm.mark_subchain_invalid(h2.hash, "I said so")
  assert hm.best_tip[0]==h10.hash # h10.hash>h11.hash


  hm.add_header(h8)
  assert hm.find_bifurcation_point(h8.hash, h9.hash) == h3.hash
  assert hm.find_bifurcation_point(h8.hash, h11.hash) == h1.hash

  hm.add_header(h12)
  hm.add_header(h13)
  assert hm.best_tip[0]==h12.hash

  try:
    hm.add_header(h15)
    raise Exception("AssertionError should be raised before")
  except AssertionError:
    pass #h15 has wrong inherently wrong PoPoW and thus header is invalid


  hm.add_header(h16) #In contrast h16 has contextually wrong PoPoW (wrong genesis) 
  assert hm.best_tip[0]==h12.hash
  assert test_storage_space.headers_storage[h16.hash].invalid
  assert test_storage_space.headers_storage[h16.hash].reason == "PoPoW sequence is wrong"


  hm.add_header(h14)
  assert hm.best_tip[0]==h14.hash
  print("headers_chains_test OK")



def multiple_valid_headers_chains_test():
  #
  #
  #               /-> h11 =>h13 =>h14
  #              |             /=> h16
  #              |-> h10 => h12 =>h15
  #  genesis => h1 => h2
  #               \ 
  #		   -> h3 => h4 => h9
  #                    \
  #                      => h5 => h6 => h7 => h8
  #heights 0    1     2     3     4     5     6

  test_storage_space = rebuild_test_storage_space()
  merkles=generate_merkles_for_supply(max_reward(0))
  genesis_header=Header(0, max_reward(0), merkles, PoPoW([]), VoteData(), int(time.time()), initial_target, 1, b"\x00"*15+b"\x00")
  #print("genesis head hash %s"%genesis_header.hash)
  hm=test_storage_space.headers_manager
  hm.set_genesis(genesis_header)
  assert test_storage_space.headers_storage[genesis_header.hash].connected_to_genesis
  assert not test_storage_space.headers_storage[genesis_header.hash].invalid
  assert test_storage_space.headers_storage[genesis_header.hash].descendants==set([])

  merkles=generate_merkles_for_supply(max_reward(1)+genesis_header.supply)
  #header(height, supply, merkles, popow, votedata, timestamp, target, version, nonce)
  h1 = Header(1, max_reward(1)+genesis_header.supply, merkles, genesis_header.next_popow(), VoteData(), int(time.time()+1), initial_target, 1, b"\x00"*15+b"\x01")
  merkles=generate_merkles_for_supply(max_reward(2)+h1.supply)
  h2  = Header(2, max_reward(2)+h1.supply, merkles, h1.next_popow(), VoteData(), int(time.time()+2), initial_target, 1, b"\x01"*15+b"\x02")
  merkles=generate_merkles_for_supply(max_reward(2)+h1.supply)
  h3  = Header(2, max_reward(2)+h1.supply, merkles, h1.next_popow(), VoteData(), int(time.time()+2), initial_target, 1, b"\x02"*15+b"\x03")
  merkles=generate_merkles_for_supply(max_reward(3)+h3.supply)
  h4  = Header(3, max_reward(3)+h3.supply, merkles, h3.next_popow(), VoteData(), int(time.time()+3), initial_target, 1, b"\x03"*15+b"\x04")
  merkles=generate_merkles_for_supply(max_reward(3)+h3.supply)
  h5  = Header(3, max_reward(3)+h3.supply, merkles, h3.next_popow(), VoteData(), int(time.time()+3), initial_target, 1, b"\x04"*15+b"\x05")
  merkles=generate_merkles_for_supply(max_reward(4)+h5.supply)
  h6  = Header(4, max_reward(4)+h5.supply, merkles, h5.next_popow(), VoteData(), int(time.time()+4), initial_target, 1, b"\x05"*15+b"\x06")
  merkles=generate_merkles_for_supply(max_reward(5)+h6.supply)
  h7  = Header(5, max_reward(5)+h6.supply, merkles, h6.next_popow(), VoteData(), int(time.time()+5), initial_target, 1, b"\x06"*15+b"\x07")
  merkles=generate_merkles_for_supply(max_reward(6)+h7.supply)
  h8  = Header(6, max_reward(6)+h7.supply, merkles, h7.next_popow(), VoteData(), int(time.time()+6), initial_target, 1, b"\x07"*15+b"\x08")
  merkles=generate_merkles_for_supply(max_reward(4)+h4.supply)
  h9  = Header(4, max_reward(4)+h4.supply, merkles, h4.next_popow(), VoteData(), int(time.time()+4), initial_target, 1, b"\x08"*15+b"\x09")
  merkles=generate_merkles_for_supply(max_reward(2)+h1.supply)
  h10 = Header(2, max_reward(2)+h1.supply, merkles, h1.next_popow(), VoteData(), int(time.time()+2), initial_target, 1, b"\x09"*15+b"\x0a")
  merkles=generate_merkles_for_supply(max_reward(2)+h1.supply)
  h11 = Header(2, max_reward(2)+h1.supply, merkles, h1.next_popow(), VoteData(), int(time.time()+2), initial_target, 1, b"\x0a"*15+b"\x0b")
  merkles=generate_merkles_for_supply(max_reward(3)+h10.supply)
  h12 = Header(3, max_reward(3)+h10.supply, merkles, h10.next_popow(), VoteData(), int(time.time()+3), initial_target, 1, b"\x0b"*15+b"\x0c")
  merkles=generate_merkles_for_supply(max_reward(3)+h11.supply)
  h13 = Header(3, max_reward(3)+h11.supply, merkles, h11.next_popow(), VoteData(), int(time.time()+3), initial_target, 1, b"\x0c"*15+b"\x0d")
  merkles=generate_merkles_for_supply(max_reward(4)+h13.supply)
  h14 = Header(4, max_reward(4)+h13.supply, merkles, h13.next_popow(), VoteData(), int(time.time()+4), initial_target, 1, b"\x0d"*15+b"\x0d")
  merkles=generate_merkles_for_supply(max_reward(4)+h12.supply)
  h15 = Header(4, max_reward(4)+h12.supply, merkles, h12.next_popow(), VoteData(), int(time.time()+4), initial_target, 1, b"\x0e"*15+b"\x0d")
  merkles=generate_merkles_for_supply(max_reward(4)+h12.supply)
  h16 = Header(4    , max_reward(4)+h12.supply, merkles, h12.next_popow(), VoteData(), int(time.time()+4), initial_target, 1, b"\x0f"*15+b"\x0d")

  all_headers = [h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14, h15, h16]
  
  for _h in all_headers:
    hm.add_header(_h)
  hash_to_num = {}
  for i, _h in enumerate(all_headers):
    hash_to_num[_h.hash] = "h%d"%(i+1)

  for _h in all_headers:
    assert not test_storage_space.headers_storage[_h.hash].invalid
    assert test_storage_space.headers_storage[_h.hash].connected_to_genesis

  assert set(hm.all_descendants_with_height(h1.hash, 3)) ==set([h4.hash, h5.hash, h12.hash, h13.hash])
  next_actions = hm.next_actions(h1.hash)
  assert len(next_actions)==4
  assert len(next_actions[0])==5
  alternatives_hashes=[]
  for _chain in next_actions[1:]:
    alternatives_hashes.append(_chain[0][1])
  assert set(alternatives_hashes) == set([h2.hash, h10.hash, h11.hash])
  assert next_actions[0]==[('ADDBLOCK', h3.hash),('ADDBLOCK', h5.hash),('ADDBLOCK', h6.hash),('ADDBLOCK', h7.hash),('ADDBLOCK', h8.hash)]
  
  next_actions = hm.next_actions(h12.hash)
  assert len(next_actions)==5
  assert next_actions[0]==[('ROLLBACK', h1.hash),('ADDBLOCK', h3.hash),('ADDBLOCK', h5.hash),('ADDBLOCK', h6.hash),('ADDBLOCK', h7.hash),('ADDBLOCK', h8.hash)]

  assert [('ADDBLOCK', h15.hash)] in next_actions
  assert [('ADDBLOCK', h16.hash)] in next_actions
  assert [('ROLLBACK', h1.hash), ('ADDBLOCK', h11.hash), ('ADDBLOCK', h13.hash), ('ADDBLOCK', h14.hash)] in next_actions
  assert [('ROLLBACK', h1.hash), ('ADDBLOCK', h3.hash), ('ADDBLOCK', h4.hash), ('ADDBLOCK', h9.hash)] in next_actions

  assert hm.find_ancestor_with_height(h14.hash, 1)==h1.hash
  assert hm.find_ancestor_with_height(h14.hash, 3)==h13.hash
  assert hm.find_ancestor_with_height(h8.hash, 3)==h5.hash
  assert hm.find_ancestor_with_height(h8.hash, 6)==h8.hash

  print("multiple_valid_headers_chains_test OK")

