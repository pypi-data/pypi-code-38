from pathlib import Path

import pytest

from oll_sc.api import (sc_export_pub_key_pem, sc_export_x509_pem,
                        sc_is_present, sc_session, sc_sign_rsa,
                        sc_sign_rsa_pkcs_pss_sha256)
from oll_sc.exceptions import (SmartCardFindKeyObjectError,
                               SmartCardNotPresentError, SmartCardSigningError,
                               SmartCardWrongPinError)

from .pkcs11 import PKCS11
from .settings import (VALID_KEY_ID, VALID_MECH, VALID_PIN, WRONG_KEY_ID,
                       WRONG_MECH, WRONG_PIN)


def test_sc_export_pub_key_valid_key_id_should_return_pem(pkcs11):
  with open(str(Path(__file__).parent / 'keys/public_key.pem'), 'rb') as pem:
    pub_key_pem = sc_export_pub_key_pem(VALID_KEY_ID, VALID_PIN, pkcs11=pkcs11)
    assert pub_key_pem == pem.read()


def test_sc_export_pub_key_wrong_key_id_should_raise_error(pkcs11):
  with pytest.raises(SmartCardFindKeyObjectError):
    sc_export_pub_key_pem(WRONG_KEY_ID, VALID_PIN, pkcs11=pkcs11)


def test_sc_export_x509_valid_key_id_should_return_cert(pkcs11):
  with open(str(Path(__file__).parent / 'keys/x509_cert.pem'), 'rb') as pem:
    x509_cert = sc_export_x509_pem(VALID_KEY_ID, VALID_PIN, pkcs11=pkcs11)
    assert x509_cert == pem.read()


def test_sc_export_x509_valid_key_id_should_should_raise_error(pkcs11):
  with pytest.raises(SmartCardFindKeyObjectError):
    sc_export_x509_pem(WRONG_KEY_ID, VALID_PIN, pkcs11=pkcs11)


def test_sc_is_present_should_return_true(pkcs11):
  assert sc_is_present(pkcs11=pkcs11)


@pytest.mark.skip_smartcard
@pytest.mark.parametrize('pkcs11', [dict(sc_inserted=False)], indirect=True)
def test_sc_is_present_should_return_false(pkcs11):
  assert not sc_is_present(pkcs11=pkcs11)


def test_sc_session_with_valid_pin_should_return_session_obj(pkcs11):
  with sc_session(VALID_PIN, pkcs11=pkcs11) as session:
    assert session

    if isinstance(pkcs11, PKCS11):
      assert session.logged_in
      assert not session.session_closed

  if isinstance(pkcs11, PKCS11):
    assert session.session_closed


@pytest.mark.skip_smartcard
@pytest.mark.parametrize('pkcs11', [dict(sc_inserted=False)], indirect=True)
def test_sc_session_without_sc_inserted_should_raise_error(pkcs11):
  with pytest.raises(SmartCardNotPresentError):
    with sc_session(VALID_PIN, pkcs11=pkcs11):
      pass


def test_sc_session_wrong_pin_should_raise_error(pkcs11):
  with pytest.raises(SmartCardWrongPinError):
    with sc_session(WRONG_PIN, pkcs11=pkcs11):
      pass


def test_sc_sign_rsa_wrong_key_id_should_raise_error(pkcs11):
  with pytest.raises(SmartCardFindKeyObjectError):
    sc_sign_rsa('test', VALID_MECH, WRONG_KEY_ID, VALID_PIN, pkcs11=pkcs11)


def test_sc_sign_rsa_wrong_mechanism_should_raise_error(pkcs11):
  with pytest.raises(SmartCardSigningError):
    sc_sign_rsa('test', WRONG_MECH, VALID_KEY_ID, VALID_PIN, pkcs11=pkcs11)


def test_sc_sign_rsa_pkcs_pss_sha256_string_data(pkcs11):
  signature = sc_sign_rsa_pkcs_pss_sha256('test', VALID_KEY_ID, VALID_PIN, pkcs11=pkcs11)
  assert signature
  assert isinstance(signature, bytes)


def test_sc_sign_rsa_pkcs_pss_sha256_bytes_data(pkcs11):
  signature = sc_sign_rsa_pkcs_pss_sha256(b'test', VALID_KEY_ID, VALID_PIN, pkcs11=pkcs11)
  assert signature
  assert isinstance(signature, bytes)
