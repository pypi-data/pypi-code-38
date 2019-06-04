from ctypes import cdll, c_char, c_char_p, c_int, create_string_buffer, Structure, POINTER, pointer
from os import path
import platform
import sys
import os
import json
import pkg_resources

class LibfpException(Exception):
    pass

def get_library_path(library_filename):
    return pkg_resources.resource_filename('pylibfp', path.join('lib', library_filename))

_ISPY2 = sys.version_info[0] == 2
_ISPY3 = sys.version_info[0] == 3

_ARCH, _PLAT = platform.architecture()
if _PLAT.upper().startswith("WINDOWS"):
    if _ARCH.startswith("32"):
        _libfp = cdll.LoadLibrary(get_library_path("libfpw32.dll"))
    else:
        _libfp = cdll.LoadLibrary(get_library_path("libfpw64.dll"))
elif platform.system().upper() == "DARWIN":
    _libfp = cdll.LoadLibrary(get_library_path("libfpd64.so"))
else:
    _libfp = cdll.LoadLibrary(get_library_path("libfpl64.so"))


class ResultStruct(Structure):
  _fields_ = [("err", c_int), ("data", c_char_p)]


_libfp.fingerprint.argtypes = [POINTER(c_char), c_int, c_int]
_libfp.fingerprint.restype = POINTER(ResultStruct)

_libfp.fingerprint_chunk.argtypes = [POINTER(c_char), c_int]
_libfp.fingerprint_chunk.restype = c_char_p

_libfp.fingerprint_email_terbiumtwox.argtypes = [POINTER(c_char)]
_libfp.fingerprint_email_terbiumtwox.restype = c_char_p

_libfp.fingerprint_email_fromsha1.argtypes = [POINTER(c_char)]
_libfp.fingerprint_email_fromsha1.restype = c_char_p

_libfp.fingerprint_email_sha1.argtypes = [POINTER(c_char)]
_libfp.fingerprint_email_sha1.restype = c_char_p

_libfp.clean_string.argtypes = [POINTER(c_char), c_int]
_libfp.clean_string.restype = c_char_p

_libfp.assets_from_name.argtypes = [POINTER(c_char), POINTER(c_char),
    POINTER(c_char), POINTER(c_char), POINTER(c_char)]
_libfp.assets_from_name.restype = c_char_p

_libfp.assets_from_address.argtypes = [POINTER(c_char), POINTER(c_char),
    POINTER(c_char)]
_libfp.assets_from_address.restype = c_char_p

_libfp.assets_from_city_state_zip.argtypes = [POINTER(c_char), POINTER(c_char),
    POINTER(c_char), POINTER(c_char), POINTER(c_char)]
_libfp.assets_from_city_state_zip.restype = c_char_p

_libfp.assets_from_email_address.argtypes = [POINTER(c_char), POINTER(c_char),
    POINTER(c_char)]
_libfp.assets_from_email_address.restype = c_char_p

_libfp.assets_from_ssn.argtypes = [POINTER(c_char), POINTER(c_char),
    POINTER(c_char)]
_libfp.assets_from_ssn.restype = c_char_p

_libfp.assets_from_phone_number.argtypes = [POINTER(c_char), POINTER(c_char),
    POINTER(c_char)]
_libfp.assets_from_phone_number.restype = c_char_p

_libfp.assets_from_credit_card.argtypes = [POINTER(c_char), POINTER(c_char), POINTER(c_char)]
_libfp.assets_from_credit_card.restype = c_char_p

_libfp.assets_from_iban.argtypes = [POINTER(c_char), POINTER(c_char), POINTER(c_char)]
_libfp.assets_from_iban.restype = c_char_p

MODE_TEXT = 0
MODE_CODE = 1
MODE_DIGITS = 2

ML_HASH_LENGTH = 32

OPTIONS_BOOLEAN = 1
OPTIONS_RAW = 2
OPTIONS_TILED = 4
OPTIONS_STORABLENGRAMS = 8
OPTIONS_PARSEONLY = 16

ERROR_PADDING = 1
ERROR_PADDING_MSG = "Unable to fingerprint chunk: {}"


def _ensure_bytes(v):
    if _ISPY3 and hasattr(v, "encode"):
        return v.encode("utf-8")
    if _ISPY2 and type(v) is not str:
        try:
            return v.encode("utf-8")
        except AttributeError:
            return v
    else:
        return v


def _ensure_unicode(v):
    if _ISPY3 and hasattr(v, "decode"):
        return v.decode("utf-8")
    if _ISPY2 and type(v) is str:
        return v.decode("utf-8")
    else:
        return v


def _decode_raw(s):
    c = ML_HASH_LENGTH * 2
    return [_ensure_unicode(s[i:i+c]) for i in range(0, len(s), c)]


def fingerprint(content, mode=MODE_TEXT, boolean=False, raw=False, flags=0):
    result = None
    opts = 0
    if boolean and raw:
        raise ValueError("boolean and raw cannot both be true")
    if boolean:
        opts = opts | OPTIONS_BOOLEAN
        opts = opts | OPTIONS_TILED
    if raw:
        opts = opts | OPTIONS_RAW
    else:
        opts = opts | OPTIONS_STORABLENGRAMS
    opts = opts | flags
    result = _libfp.fingerprint(create_string_buffer(_ensure_bytes(content)), mode, opts)
    if result.contents.err == ERROR_PADDING:
        raise LibfpException(ERROR_PADDING_MSG.format(result.contents.data))
    if raw:
        return _decode_raw(result.contents.data)
    return _ensure_unicode(result.contents.data)


def fingerprint_chunk(content, flags=0):
    result = _libfp.fingerprint_chunk(create_string_buffer(_ensure_bytes(content)), flags)
    return _ensure_unicode(result)


def fingerprint_email_terbiumtwox(content):
    result = _libfp.fingerprint_email_terbiumtwox(create_string_buffer(_ensure_bytes(content)))
    return _ensure_unicode(result)


def fingerprint_email_fromsha1(content):
    result = _libfp.fingerprint_email_fromsha1(create_string_buffer(_ensure_bytes(content)))
    return _ensure_unicode(result)


def fingerprint_email_sha1(content):
    result = _libfp.fingerprint_email_sha1(create_string_buffer(_ensure_bytes(content)))
    return _ensure_unicode(result)


def clean_string(content, mode=MODE_TEXT):
    v = _ensure_bytes(content)
    return _ensure_unicode(_libfp.clean_string(v, mode))

def fingerprints_pii_name_variants(first_name, middle_name, last_name):
    first_name = _ensure_bytes(first_name)
    if middle_name is not None:
        middle_name = _ensure_bytes(middle_name)
    last_name = _ensure_bytes(last_name)
    assets_json = _ensure_unicode(_libfp.assets_from_name(
            b"temporary", b"0", first_name, middle_name, last_name))
    assets = json.loads(assets_json)
    return [[_ensure_unicode(fp) for fp in asset["fingerprints"]]
            for asset in assets]

def fingerprints_pii_address_variants(street_address):
    street_address = _ensure_bytes(street_address)
    assets_json = _ensure_unicode(_libfp.assets_from_address(
            b"temporary", b"0", street_address))
    assets = json.loads(assets_json)
    return [[_ensure_unicode(fp) for fp in asset["fingerprints"]]
            for asset in assets]

def fingerprints_pii_city_state_zip_variants(city, state, zipcode):
    city = _ensure_bytes(city)
    state = _ensure_bytes(state)
    zipcode = _ensure_bytes(zipcode)

    # MdY: This is required to make state optional, not sure why.
    state = b'' if state is None else state

    assets_json = _ensure_unicode(_libfp.assets_from_city_state_zip(
            b"temporary", b"0", city, state, zipcode))
    assets = json.loads(assets_json)
    return [[_ensure_unicode(fp) for fp in asset["fingerprints"]]
            for asset in assets]

def fingerprints_pii_email_address(email):
    email = _ensure_bytes(email)
    assets_json = _ensure_unicode(_libfp.assets_from_email_address(
            b"temporary", b"0", email))
    assets = json.loads(assets_json)
    return [
        [_ensure_unicode(fp) for fp in asset["fingerprints"]] for asset in assets
    ]

def fingerprints_pii_ssn(ssn):
    ssn = _ensure_bytes(ssn)
    assets_json = _ensure_unicode(_libfp.assets_from_ssn(
            b"temporary", b"0", ssn))
    assets = json.loads(assets_json)
    assert(len(assets) == 1)
    return [_ensure_unicode(fp) for fp in assets[0]["fingerprints"]]

def fingerprints_pii_phone_number(phone_number):
    phone_number = _ensure_bytes(phone_number)
    assets_json = _ensure_unicode(_libfp.assets_from_phone_number(
            b"temporary", b"0", phone_number))
    assets = json.loads(assets_json)
    assert(len(assets) == 1)
    return [_ensure_unicode(fp) for fp in assets[0]["fingerprints"]]

def fingerprints_pii_credit_card(credit_card):
    credit_card = _ensure_bytes(credit_card)
    assets_json = _ensure_unicode(_libfp.assets_from_credit_card(b"temporary", b"0", credit_card))
    assets = json.loads(assets_json)
    assert(len(assets) == 1)
    return [_ensure_unicode(fp) for fp in assets[0]["fingerprints"]]

def fingerprints_pii_iban(iban):
    iban = _ensure_bytes(iban)
    assets_json = _ensure_unicode(_libfp.assets_from_iban(b"temporary", b"0", iban))
    assets = json.loads(assets_json)

    return [[_ensure_unicode(fp) for fp in asset["fingerprints"]]
            for asset in assets]
