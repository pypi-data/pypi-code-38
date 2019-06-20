# Fake pkcs11 classes for simulation
import pickle
from pathlib import Path

from PyKCS11 import (CKA_ALWAYS_AUTHENTICATE, CKO_CERTIFICATE, CKO_PRIVATE_KEY,
                     CKO_PUBLIC_KEY, PyKCS11Error)

from .settings import VALID_KEY_ID, VALID_MECH, VALID_PIN


def _is_valid_mechanism(mechanism):
  return mechanism._mech.mechanism == VALID_MECH._mech.mechanism and \
      mechanism._param.hashAlg == VALID_MECH._param.hashAlg and \
      mechanism._param.mgf == VALID_MECH._param.mgf and \
      mechanism._param.sLen == VALID_MECH._param.sLen


class _Session:
  """Fake pkcs11 session implementation used to test API.
  For more info:
    https://github.com/LudovicRousseau/PyKCS11/blob/master/PyKCS11/__init__.py#L851
  """

  def __init__(self, able_to_login=True):
    self._able_to_login = able_to_login
    self.logged_in = False
    self.session_closed = False

  def closeSession(self):
    self.session_closed = True

  def findObjects(self, *args):
    # If key id is wrong, return empty list
    if args[0][0][1] != VALID_KEY_ID:
      return []

    return {
        # Certificate
        CKO_CERTIFICATE: ['cert'],
        CKO_PUBLIC_KEY: ['pub_key'],
        CKO_PRIVATE_KEY: ['priv_key']
    }.get(args[0][1][1], [])

  def getAttributeValue(self, obj, *args):
    if obj == 'pub_key':
      with open(str(Path(__file__).parent / 'keys/public_key.cer'), 'rb') as der:
        return [pickle.loads(der.read())]
    elif obj == 'cert':
      with open(str(Path(__file__).parent / 'keys/x509_cert.cer'), 'rb') as der:
        return [pickle.loads(der.read())]
    elif obj == 'priv_key' and args[0][0] == CKA_ALWAYS_AUTHENTICATE:
      return [True]

    else:
      return []

  def login(self, pin, user_type=None):
    if not self._able_to_login or pin != VALID_PIN:
      raise PyKCS11Error('Could not login.')
    self.logged_in = True

  def logout(self):
    if not self.logged_in:
      raise PyKCS11Error('Could not logout.')
    self.logged_in = False

  def sign(self, pk, data, mechanism):
    if not _is_valid_mechanism(mechanism):
      raise PyKCS11Error('Mechanism is not valid.')
    if not isinstance(data, bytes):
      raise TypeError()

    return b'signature'


class PKCS11:
  """Fake pkcs11 lib implementation used to test API.
  For more info:
    https://github.com/LudovicRousseau/PyKCS11/blob/master/PyKCS11/__init__.py#L453
  """

  def __init__(self, sc_inserted=True, able_to_open_session=True,
               _able_to_login=True):
    self._able_to_login = _able_to_login
    self._able_to_open_session = able_to_open_session
    self._sc_inserted = sc_inserted

  def getSlotList(self, tokenPresent=False):
    if self._sc_inserted:
      return [0]
    else:
      return []

  def openSession(self, slot, flags=0):
    if not self._able_to_open_session:
      raise PyKCS11Error('Could not open a session.')

    return _Session(self._able_to_login)
