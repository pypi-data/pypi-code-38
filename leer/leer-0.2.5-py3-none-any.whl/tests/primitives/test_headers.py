import os
from leer.core.primitives.header import Header, ContextHeader, VoteData, PoPoW
'''
from secp256k1_zkp import PrivateKey
from leer.core.lubbadubdub.ioput import IOput
from leer.core.lubbadubdub.address import Address
from leer.core.lubbadubdub.stubs import KeyManager, KeyManagerClass
from leer.core.lubbadubdub.transaction import Transaction
from leer.tests.stubs.txos_storage_stub import TXOsStorageStub
'''
def test_headers_and_aux():
  test_popow()
  test_votedata()
  test_headers()
  test_context_header()

def test_popow():
  #Should be separated to a few test functions
  a = PoPoW([])
  assert a._get_level(b"\x00"*3+b"\xff"*29)==1, "Wrong level detection"
  assert a._get_level(b"\x00"*5+b"\xff"*27)==3, "Wrong level detection"
  assert a._get_level(b"\x01"*32)==-2, "Wrong level detection"
  genesis= b"\x33"*16+b"\x22"*16
  lvl0= b"\x00"*2+b"\x03"*30
  lvl1= b"\x00"*3+b"\x03"*29
  lvl2= b"\x00"*4+b"\x03"*28
  lvl3= b"\x00"*5+b"\x03"*27
  lvl4= b"\x00"*6+b"\x03"*26
  slvl1= b"\x00"*1+b"\x03"*31
  slvl2= b"\x03"*32
  b = PoPoW([slvl2, lvl0, lvl2,lvl3, genesis])
  c=PoPoW()
  c.generate_from_prev(b, lvl4)
  assert c.pointers == [lvl4,genesis]
  d=PoPoW()
  d.generate_from_prev(b, b"\xfa"*32)
  assert d.pointers == [b"\xfa"*32, lvl0, lvl2, lvl3, genesis]
  assert d.serialize() == b"\x05" + b"\xfa"*32 + lvl0 + lvl2 + lvl3 + genesis
  e=PoPoW()
  assert e.deserialize_raw(d.serialize()) == b""
  assert e.pointers == [b"\xfa"*32, lvl0, lvl2, lvl3, genesis]
  assert e.check_self_consistency()
  g=PoPoW()
  g.pointers = [lvl3, lvl2, genesis]
  assert not g.check_self_consistency()

def test_votedata():
  #Should be separated to a few test functions
  for (forks_vector, miner_subsidy_vote) in [(b"\x00"*4, b"\x00"), (b"\xff"*4, b"\xff"), (os.urandom(4), os.urandom(1))]:
    a=VoteData(forks_vector, miner_subsidy_vote)
    ser_a=a.serialize()
    b=VoteData()
    ser=b.deserialize_raw(ser_a+b"\x00")
    assert ser==b"\x00"
    assert b.forks_vector==a.forks_vector, "Wrong serialization-deserialization of forks_vector %s"%a.forks_vector
    assert b.miner_subsidy_vote==a.miner_subsidy_vote, "Wrong serialization-deserialization of miner_subsidy_vote %s"%a.miner_subsidy_vote



def test_headers():
  #serialize-deserialize
  h0 = Header(3    , 0, [b"\x01"*65,b"\x02"*32,b"\x03"*65], PoPoW([b"\x01"*32,b"\x02"*32]), VoteData(), 1513777327, 2**256-1, 1, b"\x00"*15+b"\x0d")
  h1=Header()
  h1.deserialize(h0.serialize())
  assert h1.serialize()==h0.serialize()
  assert h1==h0

def test_context_header():
  #serialize-deserialize
  h0 = Header(3    , 0, [b"\x01"*65,b"\x02"*32,b"\x03"*65], PoPoW([]), VoteData(), 1513777327, 2**256-1, 1, b"\x00"*15+b"\x0d")
  ch0=ContextHeader(h0)
  ch0.descendants = set([b"\x12"*32])
  ch0.connected_to_genesis = True
  ch0.invalid = True
  ch0.reason = "Haha"
  ch1=ContextHeader()  
  ch1.deserialize(ch0.serialize_with_context())
  assert ch1.serialize()==ch0.serialize()

