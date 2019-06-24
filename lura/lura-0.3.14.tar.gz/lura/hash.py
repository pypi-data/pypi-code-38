import hashlib

def hashs(buf, alg='sha512'):
  'Hash a buffer using hashlib.'

  algs = hashlib.algorithms_guaranteed
  if not alg in algs:
    raise ValueError(f'Algorithm {alg} not in {algs}')
  o = getattr(hashlib, alg)()
  if isinstance(buf, str):
    buf = buf.encode("ascii")
  o.update(buf)
  return str(o.hexdigest())

def hashf(path, alg='sha512'):
  'Hash a file using hashlib.'

  algs = hashlib.algorithms_guaranteed
  if not alg in algs:
    raise ValueError(f'Algorithm {alg} not in {algs}')
  o = getattr(hashlib, alg)()
  with open(path, 'rb') as fd:
    while True:
      buf = fd.read(hashf.buflen)
      if len(buf) == 0:
        break
      o.update(buf)
  return str(o.hexdigest())

hashf.buflen = 256 * 1024

def checkhash(path, alg, hash):
  '''
  Calculate the hash for a file at ``path`` using algorithm ``alg`` and
  compare it to a known hash ``sum``. If the hashes do not match, then
  ``checkhash.error`` is raised.
  '''

  hash2 = hashf(path, alg)
  if hash != hash2:
    raise checkhash.error(path, alg, hash, hash2)

class HashError(Exception):

  def __init__(self, path, alg, expected, received):
    msg = f'{path}: expected {alg} {expected}, got {received}'
    super().__init__(msg)
    self.path = path
    self.alg = alg
    self.expected = expected
    self.received = received

checkhash.error = HashError
