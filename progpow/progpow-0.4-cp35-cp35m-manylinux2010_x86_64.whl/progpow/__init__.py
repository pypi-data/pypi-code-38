from ._libprogpow0_9_2 import ffi as ffi0_9_2, lib as lib0_9_2
from ._libprogpow0_9_3 import ffi as ffi0_9_3, lib as lib0_9_3
from collections import OrderedDict
import warnings
versions = {
            '0.9.2' : {'ffi':ffi0_9_2, 'lib':lib0_9_2},
            '0.9.3' : {'ffi':ffi0_9_3, 'lib':lib0_9_3},
           }

class ProgPowHandler:
  def __init__(self, max_contexts_num=1, version=None):
    if not version:
      warnings.warn("Default progpow versioning is deprecated. Version should be set explicitly", DeprecationWarning)
      version='0.9.2'
    self.version = version
    self.ffi, self.lib = versions[self.version]['ffi'], versions[self.version]['lib']
    self.max_contexts_num = max_contexts_num
    self.contexts=OrderedDict()

  def bytes_to_hash256(self, bts):
    hash256 = self.ffi.new("hash256*")
    for i in range(32):
      hash256.bytes[i]=bts[i]
    return hash256

  def get_epoch_num(self, block_num):
    return block_num//self.lib.ETHASH_EPOCH_LENGTH

  def _create_context(self, epoch_num):
    ctx = self.lib.ethash_create_epoch_context(epoch_num)
    self.contexts[epoch_num]=ctx

  def _destroy_oldest_context(self):
    epoch_num, ctx = self.contexts.popitem(0)
    self.lib.ethash_destroy_epoch_context(ctx)
 
  def _check_context(self, epoch_num):
    if epoch_num in self.contexts:
      return
    self._create_context(epoch_num)
    while len(self.contexts)>self.max_contexts_num:
      self._destroy_oldest_context()

  def hash_result(self, header_height, header_hash, nonce):
    hh = self.bytes_to_hash256(header_hash)
    result = self.ffi.new("result*")
    epoch_num = self.get_epoch_num(header_height)
    self._check_context(epoch_num)
    self.lib.progpow_hash(result, self.contexts[epoch_num], header_height, hh,  nonce) 
    return bytes(result.mix_hash.bytes), bytes(result.final_hash.bytes)

  def hash(self, header_height, header_hash, nonce):
    return self.hash_result(header_height, header_hash, nonce)[1]
    
  def light_search(self, header_height, header_hash, target, start_nonce = 0, iterations=0, step = 2**10):
    hh = self.bytes_to_hash256(header_hash)
    boundary = self.bytes_to_hash256(target)
    search_result = self.ffi.new("search_result*")
    epoch_num = self.get_epoch_num(header_height)
    self._check_context(epoch_num)
    nonce = start_nonce
    max_nonce = start_nonce+iterations
    while nonce<max_nonce:
      next_iter = step if nonce+step<max_nonce else max_nonce-nonce
      self.lib.progpow_search_light(search_result, self.contexts[epoch_num], header_height, hh, boundary, start_nonce, next_iter)
      nonce+=next_iter
      if search_result.solution_found:
        break
    if search_result.solution_found:
      return {'solution_found':True, 'nonce':search_result.nonce, 'final_hash':bytes(search_result.final_hash.bytes)}
    else:
      return {'solution_found':False}

  def give_seed(self, header_height):
    seed = self.ffi.new("hash256*")
    self.lib.ethash_initialise_epoch_seed(seed, self.get_epoch_num(header_height))
    return bytes(seed.bytes)

  def get_epoch_by_seed(self, seed):
    seed_hash = self.bytes_to_hash256(seed)
    return self.lib.find_epoch_number_by_seed(seed_hash)

  def __del__(self):
    while len(self.contexts):
      self._destroy_oldest_context()
