import threading
from typing import Dict

from eth_account.signers.local import LocalAccount
from web3 import Web3


class LocalAccountSigner:
    def __init__(self, w3: Web3, account: LocalAccount) -> None:
        super().__init__()
        self.account = account
        self.w3 = w3
        self.nonce = -1
        self.nonce_lock = threading.Lock()

    def sign(self, transaction: Dict) -> bytes:
        self.nonce_lock.acquire()
        local_nonce = -1
        try:
            if self.nonce == -1:
                self.nonce = self.w3.eth.getTransactionCount(self.account.address)
            else:
                self.nonce = self.nonce + 1
        finally:
            local_nonce = self.nonce
            self.nonce_lock.release()
        transaction['nonce'] = local_nonce
        signed = self.account.sign_transaction(transaction)
        return signed.rawTransaction


class LocalSignerFactory:
    def __init__(self) -> None:
        super().__init__()
        self.lock = threading.Lock()
        self.address_to_signer = {}

    def signer(self, w3: Web3, account: LocalAccount) -> LocalAccountSigner:
        self.lock.acquire()
        try:
            if account.address in self.address_to_signer:
                return self.address_to_signer[account.address]
            else:
                las = LocalAccountSigner(w3, account)
                self.address_to_signer[account.address] = las
                return las
        finally:
            self.lock.release()


SingletonLocalSingerFactory = LocalSignerFactory()
