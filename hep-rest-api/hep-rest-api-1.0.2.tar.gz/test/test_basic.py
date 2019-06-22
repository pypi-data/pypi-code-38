import sys
import uuid
import os
# set the path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, ""))

import hep_rest_api
from hep_rest_api.scenarios.auth import AuthHelper
from hep_rest_api.scenarios.pay import PayHelper
from hep_rest_api.scenarios.proof import ProofHelper
from hep_rest_api.scenarios.proof import OrderProof


PRIVATE_KEY_PATH = "/Users/erhu/pony/priv"
HEP_KEY = "71ffeae1a9a2402c944d84c54f8ffddc"
HEP_SECRET = "2d66e7f3dd4445dbb6791b56fadcd2dc"
HEP_PROTOCOL = "HEP"
HEP_PROTOCOL_VERSION = "1.0"
HEP_HOST = "http://hep.newtonproject.dev.diynova.com"
HEP_ID = "75098291f88343b9836118546f375a9f"
TEST_NEWID = "NEWID1acGJchbdZy74f3dTQxfZd6kkztfxzUgLtUyTvUtU21U4RaS72XY"
base_parameters = {
    'dapp_key': HEP_KEY,
    'protocol': HEP_PROTOCOL,
    'version': HEP_PROTOCOL_VERSION,
    'os': sys.platform,
    'language': 'en'
}
chain_id = 1002
key_path = PRIVATE_KEY_PATH
configuration = hep_rest_api.api_client.Configuration()
configuration.host = HEP_HOST
api_client = hep_rest_api.RestApi(hep_rest_api.ApiClient(configuration))
payment_data = {"dapp_id": "75098291f88343b9836118546f375a9f", "nonce": "92ac0a98ba1742c48eb8e91100077817", "sign_type": "secp256r1", "signature": "0xee47bd99d1807b7a14bb36c9e9fe641753f13e3c5d77610121edd3e125ddf78d22a56c98de8012d185b6de0da27aaef4101d3fe4beb5cf3038bc134d73012f48", "ts": "1561121020", "txid": "0xd7ab1ddcad52efd96298610030c985083cb6639b3f0f07c86f51ea7845a61237", "uuid": "b8e89a114b104a8d83e0266bbc5a55a1"}
login_data = {"action": "hep.auth.login", "scope": 1, "expired": 1561129670, "memo": "default", "uuid": "682749f075b74702b8c41c9a75862b0a", "dapp_id": "75098291f88343b9836118546f375a9f", "dapp_key": "71ffeae1a9a2402c944d84c54f8ffddc", "protocol":"HEP", "version": "1.0", "os": "darwin", "language": "en", "ts": 1561129370, "nonce": "ae892ffdf7ee430a992f29b5760d4e69", "dapp_signature": "046fbe22f261c5e5b62b37679b8f5a99", "dapp_signature_method": "HMAC-MD5", "signature": "0xf33c0e088f1cb64a8d0845a62333500d73b227c242e36dcf902da4243e515472dd2de175443b2918c52fbd6abbcbbace98a8e75540a93e3d29628096437f09e7", "sign_type": "secp256r1"}
login_profile = {"address": "NEW17xYWcvn5cp7rgYubVeenHZLGDJ5JtJapUPm", "avatar": "", "cellphone": "18888888881", "country_code": "86", "invite_code": "XLFFKD", "name":"不上班", "newid": "NEWID1acGJchbdZy74f3dTQxfZd6kkztfxzUgLtUyTvUtU21U4RaS72XY", "sign_type": "secp256r1", "signature": "0x8132dc49de81e4a1b85aaaa142fce6502f1093d495004240c2fee7bbf39e7ddb5c4565537ebb9b50312b6c34d267724f6567aa473dc85c9b268efc8f46f2235d", "uuid": "c11494156640416393a8d7c9926ffa87"}

def _get_api_client():
    configuration = hep_rest_api.api_client.Configuration()
    configuration.host = HEP_HOST
    api_instance = hep_rest_api.RestApi(hep_rest_api.ApiClient(configuration))
    return api_instance


def test_auth_login():
    api_client = _get_api_client()
    auth_helper = AuthHelper(api_client, base_parameters, HEP_ID, HEP_SECRET, key_path, chain_id=chain_id)
    auth_resposne = auth_helper.generate_auth_request(uuid=uuid.uuid4().hex)
    qr_str = auth_helper.generate_qrcode_string(auth_resposne.auth_hash)
    print(qr_str)
    is_valid = auth_helper.validate_auth_callback(login_profile)
    print(is_valid)


def test_auth_pay():
    api_client = _get_api_client()
    pay_helper = PayHelper(api_client, base_parameters, HEP_ID, HEP_SECRET, key_path, chain_id=chain_id)
    pay_response = pay_helper.generate_pay_request(uuid.uuid4().hex, "NEW", 12, "description", "NEWID1acGJchbdZy74f3dTQxfZd6kkztfxzUgLtUyTvUtU21U4RaS72XY", "NEWID1acGJchbdZy74f3dTQxfZd6kkztfxzUgLtUyTvUtU21U4RaS72XY", "NEWID1acGJchbdZy74f3dTQxfZd6kkztfxzUgLtUyTvUtU21U4RaS72XY", uuid=uuid.uuid4().hex)
    print(pay_response.pay_hash)
    pay_qr_str = pay_helper.generate_qrcode_string(pay_response.pay_hash)
    print(pay_qr_str)
    is_valid = pay_helper.validate_pay_callback(payment_data)
    print(is_valid)
    pay_data = {'api_version': '1', 'dapp_key': '71ffeae1a9a2402c944d84c54f8ffddc', 'protocol': 'HEP', 'version': '1.0', 'os': 'darwin', 'language': 'en', 'ts': 1561189219, 'nonce': '7fd6675608ba49d48c4e5c2f7e87bd8f', 'dapp_signature': 'beccf75e3f0aad44e25e8a50c37f7476', 'dapp_signature_method': 'HMAC-MD5', 'txid': '0xd7ab1ddcad52efd96298610030c985083cb6639b3f0f07c86f51ea7845a61237'}
    response = pay_helper.get_confirmed_transaction(pay_data['txid'])
    print(response)


def test_auth_proof():
    api_client = _get_api_client()
    order_content = OrderProof(uuid.uuid4().hex, "NEW", "20", TEST_NEWID, TEST_NEWID,TEST_NEWID, description="haha", chain_txid="0x91a662d227a62d30746e67fdc2ce7903ff63b29b5f3861b8bb2b50f64561cfaa")
    order_content.add_order_item(2, 1, 10, "NEW", "testnet", uuid.uuid4().hex, "product")
    proof_helper = ProofHelper(api_client, base_parameters, HEP_ID, HEP_SECRET, key_path, chain_id=chain_id)
    oracles = proof_helper.get_default_trust_oracle()
    print(oracles)
    proof_resposne = proof_helper.generate_proof_request(order_content.to_dict(), uuid=uuid.uuid4().hex)
    proof_str = proof_helper.generate_qrcode_string(proof_resposne.proof_hash)
    print(proof_str)
    proof_hashes = [
        proof_resposne.proof_hash
    ]
    response = proof_helper.get_status_of_proofs(proof_hashes)
    print(response)


if __name__ == '__main__':
    print("test--login--")
    test_auth_login()
    print("test---pay---")
    test_auth_pay()
    print("test---proof---")
    test_auth_proof()
