from base64 import b64encode, b64decode
import binascii
from coolsignup.conf import conf
import json
from naval import Do, Assert, Apply
from postpone import LazyString as _
from tornado.web import create_signed_value, decode_signed_value
import zlib


def create_signed_string(strg):
    return b64encode(
        zlib.compress(create_signed_value(
            conf.get("secretKey"),
            "data",
            strg
        )),
        altchars = b'_-'
    ).decode('utf-8')

def decode_signed_string(strg, max_age_days):
    try:
        result = decode_signed_value(
            conf.get("secretKey"),
            "data",
            zlib.decompress(b64decode(strg, altchars = b'_-')),
            max_age_days = max_age_days
        )
    except (binascii.Error, zlib.error) as exc:
        return None
    if result is None:
        return None
    else:
        return result.decode('utf-8')

def create_signed_document(dct):
    return create_signed_string(json.dumps(dct))

def decode_signed_document(signed_doc, max_age_days):
    decoded_string = decode_signed_string(signed_doc, max_age_days)
    if decoded_string is None:
        return None
    return json.loads(decoded_string)

def DecodeSignedDocument(max_age_days, error_message = None):
    return Do(
        Apply(lambda message: decode_signed_document(message, max_age_days)),
        Assert(lambda result: result is not None),
        error_message = error_message or _("Invalid or expired code")
    )

def DecodeSignedString(max_age_days, error_message = None):
    return Do(
        Apply(lambda message: decode_signed_string(message, max_age_days)),
        Assert(lambda result: result is not None),
        error_message = error_message or _("Invalid or expired code")
    )
