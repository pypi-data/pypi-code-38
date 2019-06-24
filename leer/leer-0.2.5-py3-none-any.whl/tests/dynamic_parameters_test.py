from leer.core.primitives.header import Header, PoPoW, VoteData, ContextHeader
from leer.tests.storage.storage_for_test import HeadersStorage
from leer.tests.storage.storage_for_test import HeadersManager

from leer.core.utils import encode_target, decode_target
from leer.core.parameters.dynamic import max_reward, initial_target, next_target, next_reward
from leer.tests.storage.storage_for_test import test_storage_space, wipe_test_dirs, rebuild_test_storage_space
import shutil, time

def reward_test():
  '''
    Headers are invalid, but it is ok. We only check work of next_reward func which is independent from  headers validity.
  '''
  test_storage_space = rebuild_test_storage_space()
  merkles=[b"\x01"*65,b"\x02"*32,b"\x03"*65]
  genesis_header=Header(0, max_reward(0), merkles, PoPoW([]), VoteData(), int(time.time()), initial_target, 1, b"\x00"*15+b"\x00")

  hm=test_storage_space.headers_manager
  hm.set_genesis(genesis_header)
  runner=genesis_header
  for i in range(1,1027):
    runner = Header(i, max_reward(i)+runner.supply, merkles, runner.next_popow(), 
                    VoteData(miner_subsidy_vote=b"\x00"), int(runner.timestamp+1), 
                    next_target(runner.hash, headers_storage=test_storage_space.headers_storage), 1, b"\x00"*16)
    hm.add_header(runner)
  assert(next_reward(runner.hash,headers_storage=test_storage_space.headers_storage)==0)
  #assert not test_storage_space.headers_storage[runner.prev].invalid #It is invalid: merkles
  #assert test_storage_space.headers_storage[runner.hash].invalid
  #assert test_storage_space.headers_storage[runner.hash].reason=="Supply is wrong"
  runner = Header(1026, runner.supply, merkles, runner.next_popow(), 
                  VoteData(miner_subsidy_vote=b"\xff"), int(runner.timestamp+1), 
                  next_target(runner.hash, headers_storage=test_storage_space.headers_storage), 1, b"\x00"*16)
  hm.add_header(runner)
  assert(next_reward(runner.hash,headers_storage=test_storage_space.headers_storage)==int(max_reward(1027)/1024))
  for i in range(1027,2050):
    runner = Header(i, max_reward(i)+runner.supply, merkles, runner.next_popow(), 
                    VoteData(miner_subsidy_vote=b"\xff"), int(runner.timestamp+1), 
                    next_target(runner.hash, headers_storage=test_storage_space.headers_storage), 1, b"\x00"*16)
    hm.add_header(runner)
  assert(next_reward(runner.hash,headers_storage=test_storage_space.headers_storage)==max_reward(2050))
  
  print("reward_test OK")

def target_test():
  test_storage_space = rebuild_test_storage_space()
  merkles=[b"\x01"*65,b"\x02"*32,b"\x03"*65]
  genesis_header=Header(0, max_reward(0), merkles, PoPoW([]), VoteData(), int(time.time()), initial_target, 1, b"\x00"*15+b"\x00")

  hm=test_storage_space.headers_manager
  hm.set_genesis(genesis_header)
  runner=genesis_header
  for i in range(1,22):
    assert next_target(runner.hash, headers_storage=test_storage_space.headers_storage)==initial_target
    runner = Header(i, max_reward(i)+runner.supply, merkles, runner.next_popow(), 
                    VoteData(miner_subsidy_vote=b"\x00"), int(runner.timestamp+1), 
                    next_target(runner.hash, headers_storage=test_storage_space.headers_storage), 1, b"\x00"*16)
    hm.add_header(runner)
  assert next_target(runner.hash, headers_storage=test_storage_space.headers_storage)==decode_target(*encode_target(initial_target*0.8))

  runner=genesis_header
  for i in range(1,22):
    runner = Header(i, max_reward(i)+runner.supply, merkles, runner.next_popow(), 
                    VoteData(miner_subsidy_vote=b"\x00"), int(runner.timestamp+60), 
                    next_target(runner.hash, headers_storage=test_storage_space.headers_storage), 1, b"\x00"*16)
    hm.add_header(runner)
  assert next_target(runner.hash, headers_storage=test_storage_space.headers_storage)==decode_target(*encode_target(initial_target))

  runner=genesis_header
  for i in range(1,22):
    runner = Header(i, max_reward(i)+runner.supply, merkles, runner.next_popow(), 
                    VoteData(miner_subsidy_vote=b"\x00"), int(runner.timestamp+59), 
                    next_target(runner.hash, headers_storage=test_storage_space.headers_storage), 1, b"\x00"*16)
    hm.add_header(runner)
  assert next_target(runner.hash, headers_storage=test_storage_space.headers_storage)==decode_target(*encode_target(initial_target*59./60))
  print("target_test OK")
