import base64
import json

from py_nsbcli.config import ENC
from py_nsbcli.system_merkle_proof.merkle_proof import MerkleProof
from py_nsbcli.modules.contract import Contract


class SystemMerkleProof(Contract):
    def __init__(self, bind_cli):
        super().__init__(bind_cli)

    def validate_merkle_proof(self, wlt, merkle_proof: MerkleProof):
        data_add_action = {
            "function_name": "validateMerkleProof",
            "args": base64.b64encode(merkle_proof.json().encode(ENC)).decode()
        }

        return self.exec_system_contract_method(
            wlt,
            b"systemCall\x19system.merkleproof\x18",
            json.dumps(data_add_action).encode(ENC),
            0
        )

    def get_merkle_proof(
        self, wlt, isc_address: bytes or str, tid: int, m_type: int, bid: int, root_hash: bytes, key: bytes
    ):
        if isinstance(isc_address, str):
            isc_address = bytes.fromhex(isc_address)
        data_add_action = {
            "function_name": "getMerkleProof",
            "args": base64.b64encode(json.dumps({
                "1": base64.b64encode(isc_address).decode(),
                "2": tid,
                "3": m_type,
                "4": bid,
                "5": root_hash,
                "6": key,
            }).encode(ENC)).decode()
        }

        return self.exec_system_contract_method(
            wlt,
            b"systemCall\x19system.merkleproof\x18",
            json.dumps(data_add_action).encode(ENC),
            0
        )
