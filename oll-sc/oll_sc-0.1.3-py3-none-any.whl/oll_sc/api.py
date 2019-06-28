import logging
from contextlib import contextmanager

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from PyKCS11 import (CKA_ALWAYS_AUTHENTICATE, CKA_CERTIFICATE_TYPE, CKA_CLASS,
                     CKA_ID, CKA_VALUE, CKC_X_509, CKF_RW_SESSION,
                     CKF_SERIAL_SESSION, CKG_MGF1_SHA256, CKM_SHA256,
                     CKM_SHA256_RSA_PKCS_PSS, CKO_CERTIFICATE, CKO_PRIVATE_KEY,
                     CKO_PUBLIC_KEY, CKU_CONTEXT_SPECIFIC, PyKCS11Error,
                     RSA_PSS_Mechanism)

from . import init_pkcs11
from .exceptions import (SmartCardFindKeyObjectError, SmartCardNotPresentError,
                         SmartCardSigningError, SmartCardWrongPinError)

logger = logging.getLogger(__name__)


@init_pkcs11
def sc_export_pub_key_pem(key_id, pin, pkcs11=None):
  """Export public key for provided key id from smart card.

  Args:
    - key_id(tuple): Key ID as tuple (e.g. (1,))
    - pin(str): Pin for session login
    - pkcs11(PyKCS11): Automatically initialied; do not pass this argument

  Returns:
    Public key in PEM format (bytes)

  Raises:
    - SmartCardNotPresentError: If smart card is not inserted
    - SmartCardWrongPinError: If pin is incorrect
    - SmartCardFindKeyObjectError: If public key for given key id does not exist
  """
  with sc_session(pin, pkcs11=pkcs11) as session:
    try:
      pub_key = session.findObjects([(CKA_ID, key_id), (CKA_CLASS, CKO_PUBLIC_KEY)])[0]
      pub_key_value = session.getAttributeValue(pub_key, [CKA_VALUE])[0]

      pub_key_der = serialization.load_der_public_key(bytes(pub_key_value), default_backend())
      # Convert public key DER to PEM format
      pub_key_pem = pub_key_der.public_bytes(
          serialization.Encoding.PEM,
          serialization.PublicFormat.SubjectPublicKeyInfo,
      )

      logger.debug('Public key for key id: %s is \n%s', key_id, pub_key_pem.decode())
      return pub_key_pem
    except (IndexError, TypeError, ValueError):
      raise SmartCardFindKeyObjectError(key_id)


@init_pkcs11
def sc_export_x509_pem(key_id, pin, pkcs11=None):
  """Export x509 certificate for provided key id from smart card.

  Args:
    - key_id(tuple): Key ID as tuple (e.g. (1,))
    - pin(str): Pin for session login
    - pkcs11(PyKCS11): Automatically initialied; do not pass this argument

  Returns:
    x509 certificate in PEM format (bytes)

  Raises:
    - SmartCardNotPresentError: If smart card is not inserted
    - SmartCardWrongPinError: If pin is incorrect
    - SmartCardFindKeyObjectError: If x509 certificate for given key id does not exist
  """
  with sc_session(pin, pkcs11=pkcs11) as session:
    try:
      x509_cert = session.findObjects([(CKA_ID, key_id),
                                       (CKA_CLASS, CKO_CERTIFICATE),
                                       (CKA_CERTIFICATE_TYPE, CKC_X_509)])[0]
      x509_cert_value = session.getAttributeValue(x509_cert, [CKA_VALUE])[0]
      x509_cert_value_der = x509.load_der_x509_certificate(bytes(x509_cert_value),
                                                           default_backend())
      # Convert x509 certificate DER to PEM format
      x509_cert_value_pem = x509_cert_value_der.public_bytes(serialization.Encoding.PEM)

      logger.debug('X509 certificate for key id: %s is \n%s', key_id, x509_cert_value_pem.decode())
      return x509_cert_value_pem
    except (IndexError, TypeError, ValueError):
      raise SmartCardFindKeyObjectError(key_id)


@init_pkcs11
def sc_is_present(pkcs11=None):
  """Check if smart card is inserted.

  Args:
    - pkcs11(PyKCS11): Automatically initialied; do not pass this argument

  Returns:
    True if smart card is inserted otherwise False (bool)
  """
  return bool(pkcs11.getSlotList(tokenPresent=True))


@contextmanager
@init_pkcs11
def sc_session(pin, pkcs11=None):
  """Open token session needed for signing, encryption, etc.

  Args:
    - pin(str): Pin for session login
    - pkcs11(PyKCS11): Automatically initialied; do not pass this argument

  Returns:
    Session object (pykcs11.Session)

  Raises:
    - SmartCardNotPresentError: If smart card is not inserted
    - SmartCardWrongPinError: If pin is incorrect
  """
  if not sc_is_present(pkcs11=pkcs11):
    raise SmartCardNotPresentError('Please insert your smart card.')

  try:
    slot = pkcs11.getSlotList(tokenPresent=True)[0]

    session = pkcs11.openSession(slot, CKF_SERIAL_SESSION | CKF_RW_SESSION)
    logger.debug('Session opened for slot %s', slot)

    session.login(pin)
    yield session
    session.logout()

    logger.debug('Successfully logged out of session.')
  except PyKCS11Error:
    raise SmartCardWrongPinError('PIN is not valid.')
  finally:
    session.closeSession()
    logger.debug('Successfully closed the session.')


@init_pkcs11
def sc_sign_rsa(data, mechanism, key_id, pin, pkcs11=None):
  """Create and return signature using provided rsa mechanism.

  Args:
    - data(str | bytes): Data to be digested and signed
    - mechanism(PyKCS11 mechanism): Consult PyKCS11 for more info
    - key_id(tuple): Key ID as tuple (e.g. (1,))
    - pin(str): Pin for session login
    - pkcs11(PyKCS11): Automatically initialied; do not pass this argument

  Returns:
    Signature based on provided arguments (bytes)

  Raises:
    - SmartCardNotPresentError: If smart card is not inserted
    - SmartCardWrongPinError: If pin is incorrect
    - SmartCardFindKeyObjectError: If private key for given key id does not exist
    - SmartCardSigningError: If error happened during signing data
  """
  if isinstance(data, str):
    data = data.encode()

  logger.debug('About to sign data %s with mechanism %s', data, mechanism)

  with sc_session(pin, pkcs11=pkcs11) as session:
    try:
      priv_key = session.findObjects([(CKA_ID, key_id), (CKA_CLASS, CKO_PRIVATE_KEY)])[0]

      # If CKA_ALWAYS_AUTHENTICATE is True, login with CKU_CONTEXT_SPECIFIC
      always_auth = session.getAttributeValue(priv_key, [CKA_ALWAYS_AUTHENTICATE])[0]
      if always_auth:
        session.login(pin, CKU_CONTEXT_SPECIFIC)

      return session.sign(priv_key, data, mechanism)
    except (IndexError, TypeError):
      raise SmartCardFindKeyObjectError(key_id)
    except PyKCS11Error:
      raise SmartCardSigningError(data)


@init_pkcs11
def sc_sign_rsa_pkcs_pss_sha256(data, key_id, pin, pkcs11=None):
  """Sign data using SHA256_RSA_PKCS_PSS mechanism.

  Args:
    - data(str | bytes): Data to be digested and signed
    - key_id(tuple): Key ID as tuple (e.g. (1,))
    - pin(str): Pin for session login
    - pkcs11(PyKCS11): Automatically initialied; do not pass this argument

  Returns:
    Signature based on RSASSA-PSS signing algorithm on SHA256 digested data (bytes)

  Raises:
    - SmartCardNotPresentError: If smart card is not inserted
    - SmartCardWrongPinError: If pin is incorrect
    - SmartCardFindKeyObjectError: If private key for given key id does not exist
    - SmartCardSigningError: If error happened during signing data
  """
  mechanism = RSA_PSS_Mechanism(CKM_SHA256_RSA_PKCS_PSS, CKM_SHA256, CKG_MGF1_SHA256, 32)
  return bytes(sc_sign_rsa(data, mechanism, key_id, pin, pkcs11=pkcs11))
