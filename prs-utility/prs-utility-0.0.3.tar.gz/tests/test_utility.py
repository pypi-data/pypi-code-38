import json
import pytest

from prs_utility.util import (
    remove_prefix_0x, dump_buf, quote_qs, get_sorted_qs
)
from prs_utility.core import get_private_key
from prs_utility import (
    keccak256,
    recover_private_key,
    private_key_to_address,
    create_key_pair,
    sign_hash,
    sign_text,
    sign_block_data,
    sig_to_address,
    sig_to_address_from_block,
)
from prs_utility import hex_to_buf


KEYSTORE = {
    "address": "758ea2601697fbd3ba6eb6774ed70b6c4cdb0ef9",
    "crypto": {
        "cipher": "aes-128-ctr",
        "ciphertext": "92af6f6710eba271eae5ac7fec72c70d9f49215e7880a0c45d4c53e56bd7ea59",
        "cipherparams": {
            "iv": "13ddf95d970e924c97e4dcd29ba96520"
        },
        "mac": "b9d81d78f067334ee922fb2863e32c14cbc46e479eeb0acc11fb31e39256004e",
        "kdf": "pbkdf2",
        "kdfparams": {
            "c": 262144,
            "dklen": 32,
            "prf": "hmac-sha256",
            "salt": "79f90bb603491573e40a79fe356b88d0c7869852e43c2bbaabed44578a82bbfa"
        }
    },
    "id": "93028e51-a2a4-4514-bc1a-94b089445f35",
    "version": 3
}
PASSWORD = '123123'
PRIVATE_KEY = '6e204c62726a19fe3f43c4ca9739b7ffa37e4a3226f824f3e24e00a5890addc6'
ADDRESS = '758ea2601697fbd3ba6eb6774ed70b6c4cdb0ef9'


@pytest.mark.parametrize('s', ['0x123456', '0X123456', '123456'])
def test_remove_prefix_0x(s):
    remove_prefix_0x(s) == '123456'


@pytest.mark.parametrize(
    's, expected',
    [
        ('/', '%2F'),
        (' ', '%20'),
        ('+', '%2B'),
        ('http://a.com', 'http%3A%2F%2Fa.com'),
    ]
)
def test_quote_qs(s, expected):
    assert quote_qs(s) == expected


@pytest.mark.parametrize(
    'data, expected',
    [
        ({'a': 'A', 'b': True, 'c': False}, 'a=A&b=true&c=false'),
        ({'c': 'A', 'b': True, 'a': False}, 'a=false&b=true&c=A'),
        ({'c': 'a', 'b': 'b', 'a': 'c'}, 'a=c&b=b&c=a'),
    ]
)
def test_get_sorted_qs(data, expected):
    assert get_sorted_qs(data) == expected


def test_get_private_key():
    # from hex str
    pk = get_private_key(PRIVATE_KEY)
    assert dump_buf(pk.to_bytes(), dump=True) == PRIVATE_KEY

    pk_hex_str = remove_prefix_0x(pk.to_hex())
    pk2 = get_private_key(pk_hex_str)
    assert dump_buf(pk2.to_bytes(), dump=True) == PRIVATE_KEY

    pk3 = get_private_key(pk2)
    assert dump_buf(pk3.to_bytes(), dump=True) == PRIVATE_KEY

    # from eth_keys.datatypes.PrivateKey
    assert pk3 == get_private_key(pk3)

    # from bytes
    pk4 = get_private_key(hex_to_buf(PRIVATE_KEY))
    assert dump_buf(pk4.to_bytes(), dump=True) == PRIVATE_KEY

    # others raise ValueError
    with pytest.raises(ValueError):
        assert get_private_key(49811479637078589373593593025073956895140807052997722971398738500270349278662)


@pytest.mark.parametrize('dump', [True, False])
def test_recover_private_key(dump):
    keystore = json.dumps(KEYSTORE)
    private_key = recover_private_key(keystore, PASSWORD, dump)
    if dump:
        assert isinstance(private_key, str)
        assert private_key == PRIVATE_KEY
    else:
        assert isinstance(private_key, bytes)
        assert private_key == hex_to_buf(PRIVATE_KEY)


def test_private_key_to_address():
    address = private_key_to_address(PRIVATE_KEY)
    assert address == ADDRESS


def test_keccak256():
    message = 'hello prs'
    _hash = keccak256(message)
    _HASH = '647df39ad889e83cc0b9b65375672d1bfe282565c564d3d553a435bf80e67d92'
    assert _hash == _HASH


@pytest.mark.parametrize('dump', [True, False])
def test_create_key_pair(dump):
    pair = create_key_pair(dump)
    for item in {'privateKey', 'publicKey', 'address'}:
        assert item in pair
        v = pair[item]
        if item == 'address':
            assert isinstance(v, str)
            assert v[:2].lower() != '0x'
            continue

        if dump:
            assert isinstance(v, str)
            assert v[:2].lower() != '0x'
        else:
            assert isinstance(v, bytes)


@pytest.mark.parametrize(
    '_hash, expected',
    [
        (
            '565b63ac79b7d35a05322975340ae243e35ce084ae285c719fa6b203916f2845',
            'c47b72a8c7fa6407027deba86d3466f19c3546970214e8aa0b58094d4de4043a1c1c4893098d83b692528b678837d218230a8d0d5aaff4d4b42d50b255cd774e00'
        ),
        (
            'ab2fda04d97bba54f4d45e5b86ff62c5b720c8adbac277ee5920bf916b735f28',
            '9cb66fa967e970129569e8b164785edf183e76a4d3cdffecf1f918a1fa7835ce01ab4c2ee72e8aa1a5fae32c5920b0e01a97f104a490b4afca57c0fde664ab1300'
        ),
        (
            'e196055fda057d4abcab0a1b1b0ed54d5a33d23ad348e903bbaacf6c95d8404e',
            'dd9a6dc3352bd1c864a2c626acd075f8b7c48be30bdc9c9d4d316c7b02bf038f2fb1f6c9e1b7868c75e10abb76cf2eceab1eca1002897ccc6b59a33d0512af1701'
        )
    ]
)
def test_sign_hash(_hash, expected):
    private_key = '6e204c62726a19fe3f43c4ca9739b7ffa37e4a3226f824f3e24e00a5890addc6'
    sign = sign_hash(_hash, private_key)
    assert sign['signature'] == expected


def test_sign_text():
    key_pair = create_key_pair()
    private_key = key_pair['privateKey']
    address = key_pair['address']
    message = 'hello, world'
    sig = sign_text(message, private_key)
    _hash, signature = sig['hash'], sig['signature']
    recover_addr = sig_to_address(_hash, signature)
    assert address == recover_addr


def test_sign_block_data():
    key_pair = create_key_pair()
    private_key = key_pair['privateKey']
    address = key_pair['address']
    data = {'a': 111, 'b': 222}
    sig = sign_block_data(data, private_key)
    _hash, signature = sig['hash'], sig['signature']
    recover_addr = sig_to_address(_hash, signature)
    assert address == recover_addr


def test_sig_to_address_from_block():
    key_pair = create_key_pair()
    private_key = key_pair['privateKey']
    address = key_pair['address']
    data = {'a': 111, 'b': 222}
    sig = sign_block_data(data, private_key)
    signature = sig['signature']
    recover_addr = sig_to_address_from_block(data, signature)
    assert address == recover_addr
