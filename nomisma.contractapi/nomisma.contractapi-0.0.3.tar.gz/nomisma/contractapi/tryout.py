from concurrent.futures import Future
from typing import Tuple

from nomisma.contractapi import UnsentTransaction
from nomisma.contractapi import ContractMetaData
from nomisma.contractapi.util import from_abi


class BankRegistry:
    def __init__(self, web3, asyncexec, address, caller_account=None):
        abi = from_abi('BankRegistry.json')['abi']
        self.meta_ = ContractMetaData(web3, asyncexec, address, abi, caller_account)
        self.w3_contract = web3.eth.contract(abi=abi, address=address)

    def minEquityBalance(self) -> Future:
        f = self.w3_contract.functions.minEquityBalance()
        return self.meta_.asyncexec.submit(f.call)

    def setMinEquityBalance(self, new_min) -> UnsentTransaction[None]:
        return UnsentTransaction(self.meta_, self.w3_contract.functions.setMinEquityBalance(new_min))

    def tuple_type(self) -> UnsentTransaction[Tuple[bool, str]]:
        return UnsentTransaction(self.meta_, None)
