# Compatibily code in case that pyOpenSSL is not installed.

import functools, tempfile
from subprocess import Popen, PIPE, STDOUT

_tmpfile = functools.partial(tempfile.NamedTemporaryFile, prefix=__name__+'-')

class Error(Exception): pass

FILETYPE_PEM = 1

def load_privatekey(type, buffer):
  r = _tmpfile()
  r.write(buffer.encode())
  r.flush()
  return r

def load_certificate(type, buffer):
  # extract public key since we only use it to verify signatures
  r = _tmpfile()
  p = Popen(("openssl", "x509", "-pubkey", "-noout"),
            stdin=PIPE, stdout=r, stderr=PIPE)
  err = p.communicate(buffer.encode())[1]
  if p.poll():
    raise Error(err)
  return r

def sign(pkey, data, digest):
  p = Popen(("openssl", digest, "-sign", pkey.name),
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
  out, err = p.communicate(data)
  if p.poll():
    raise Error(err)
  return out

def verify(cert, signature, data, digest):
  with _tmpfile() as f:
    f.write(signature)
    f.flush()
    p = Popen(("openssl", digest, "-verify", cert.name, "-signature", f.name),
              stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    err = p.communicate(data)[0]
  if p.poll():
    raise Error(err)
