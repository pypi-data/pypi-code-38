from decimal import *
from typing import Tuple
from nomisma.contractapi.asyncexec import UnsentTransaction, Promise
from nomisma.contractapi.meta import ContractMetaData
from nomisma.contractapi.util import from_abi


# This is code generated. Do not modify! Add methods and overrides to the subclass.
class BankRegistryAbstract:
    def __init__(self, web3, asyncexec, address, signer=None):
        abi = from_abi('BankRegistry.json')['abi']
        self.meta_ = ContractMetaData(web3, asyncexec, address, abi, signer)
        self.w3_contract = web3.eth.contract(abi=abi, address=address)

    def resolver(self) -> Promise:
        f = self.w3_contract.functions.resolver()
        return self.meta_.asyncexec.submit(f.call)

    def check_role(self,
                   addr_address,
                   role_name: str) -> Promise[None]:
        """
        Solidity signature: checkRole(address,string)
        reverts if addr does not have role

        :param addr_address: (address) : address
        :param role_name: (str) : the name of the role // reverts
        :return: a Promise for [None] that is executed asynchronously
        """
        f = self.w3_contract.functions.checkRole(addr_address, role_name)
        return self.meta_.asyncexec.submit(f.call)

    def is_valid_contract(self,
                          _contract_address) -> Promise[bool]:
        f = self.w3_contract.functions.isValidContract(_contract_address)
        return self.meta_.asyncexec.submit(f.call)

    def min_equity_balance(self) -> Promise[int]:
        f = self.w3_contract.functions.minEquityBalance()
        return self.meta_.asyncexec.submit(f.call)

    def has_role(self,
                 addr_address,
                 role_name: str) -> Promise[bool]:
        """
        Solidity signature: hasRole(address,string)
        determine if addr has role

        :param addr_address: (address) : address
        :param role_name: (str) : the name of the role
        :return: a Promise for [bool] that is executed asynchronously
        """
        f = self.w3_contract.functions.hasRole(addr_address, role_name)
        return self.meta_.asyncexec.submit(f.call)

    def token_manager(self) -> Promise:
        f = self.w3_contract.functions.tokenManager()
        return self.meta_.asyncexec.submit(f.call)

    def contracts_length(self) -> Promise[int]:
        f = self.w3_contract.functions.contractsLength()
        return self.meta_.asyncexec.submit(f.call)

    def system_governance(self) -> Promise:
        f = self.w3_contract.functions.systemGovernance()
        return self.meta_.asyncexec.submit(f.call)

    def commission_beneficiary(self) -> Promise:
        f = self.w3_contract.functions.commissionBeneficiary()
        return self.meta_.asyncexec.submit(f.call)

    def contracts(self,
                  idx: int) -> Promise:
        f = self.w3_contract.functions.contracts(idx)
        return self.meta_.asyncexec.submit(f.call)

    def date_keeper(self) -> Promise:
        f = self.w3_contract.functions.dateKeeper()
        return self.meta_.asyncexec.submit(f.call)

    def event_emitter(self) -> Promise:
        f = self.w3_contract.functions.eventEmitter()
        return self.meta_.asyncexec.submit(f.call)

    def exchange_connector(self) -> Promise:
        f = self.w3_contract.functions.exchangeConnector()
        return self.meta_.asyncexec.submit(f.call)

    def rate_precision_multiplier(self) -> Promise[int]:
        f = self.w3_contract.functions.RATE_PRECISION_MULTIPLIER()
        return self.meta_.asyncexec.submit(f.call)

    def commission_percentage(self) -> Promise[int]:
        f = self.w3_contract.functions.commissionPercentage()
        return self.meta_.asyncexec.submit(f.call)

    def governance_role_name(self) -> Promise[str]:
        f = self.w3_contract.functions.GOVERNANCE_ROLE_NAME()
        return self.meta_.asyncexec.submit(f.call)

    def get_event_emitter(self) -> Promise:
        """
        Solidity signature: getEventEmitter()
        Returns address of an existing BankEventEmitter.

        :return: a Promise for [address] that is executed asynchronously
        """
        f = self.w3_contract.functions.getEventEmitter()
        return self.meta_.asyncexec.submit(f.call)

    def get_matrices_for_banks(self,
                               banks_address_list) -> Promise:
        f = self.w3_contract.functions.getMatricesForBanks(banks_address_list)
        return self.meta_.asyncexec.submit(f.call)

    def set_event_emitter(self,
                          _event_emitter_address) -> UnsentTransaction[None]:
        """
        Solidity signature: setEventEmitter(address)
        Registers `EventEmitter` contract by assigning it's address to the `eventEmitter` variable. Only `governor` can call this function.

        :param _event_emitter_address: (address) : - address of a `EventEmitter` contract to be set.
        :return: an UnsentTransaction for [None]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.setEventEmitter(_event_emitter_address))

    def set_resolver(self,
                     _resolver_address) -> UnsentTransaction[None]:
        return UnsentTransaction(self.meta_, self.w3_contract.functions.setResolver(_resolver_address))

    def set_token_manager(self,
                          _token_manager_address) -> UnsentTransaction[None]:
        """
        Solidity signature: setTokenManager(address)
        Registers `TokenManager` contract by assigning it's address to the `tokenManager` variable. Only `governor` can call this function.

        :param _token_manager_address: (address) : - address of a `TokenManager` contract to be set.
        :return: an UnsentTransaction for [None]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.setTokenManager(_token_manager_address))

    def set_exchange_connector(self,
                               _exchange_connector_address) -> UnsentTransaction[None]:
        """
        Solidity signature: setExchangeConnector(address)
        Registers `ExchangeConnector` contract by assigning it's address to the `exchangeConnector` variable. Only `governor` can call this function.

        :param _exchange_connector_address: (address) : - address of an `ExchangeConnector` contract to be set.
        :return: an UnsentTransaction for [None]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.setExchangeConnector(_exchange_connector_address))

    def set_min_equity_balance(self,
                               _min_equity_balance: int) -> UnsentTransaction[None]:
        """
        Solidity signature: setMinEquityBalance(uint256)
        Sets new minEquityBalance Only `owner` can call this function.

        :param _min_equity_balance: (int) : - new minimum equity balance in Ether.
        :return: an UnsentTransaction for [None]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.setMinEquityBalance(_min_equity_balance))

    def set_date_keeper(self,
                        _date_keeper_address) -> UnsentTransaction[None]:
        """
        Solidity signature: setDateKeeper(address)
        Registers `DateKeeper` contract by assigning it's address to the `dateKeeper` variable. Only `owner` can call this function.

        :param _date_keeper_address: (address) : - address of a `DateKeeper` contract to be set.
        :return: an UnsentTransaction for [None]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.setDateKeeper(_date_keeper_address))

    def set_commission_beneficiary(self,
                                   beneficiary_address) -> UnsentTransaction[None]:
        return UnsentTransaction(self.meta_, self.w3_contract.functions.setCommissionBeneficiary(beneficiary_address))

    def set_commission_percentage(self,
                                  _commission_percentage: int) -> UnsentTransaction[None]:
        return UnsentTransaction(self.meta_, self.w3_contract.functions.setCommissionPercentage(_commission_percentage))

    def deploy_bank(self,
                    to_pay_ether: Decimal,
                    date_args_uint256_array_4,
                    deploy_num_args_uint256_array_4,
                    _loan_token_address,
                    data_bytes) -> UnsentTransaction:
        """
        Solidity signature: deployBank(uint256[4],uint256[4],address,bytes)
        deployBank - deploys new bank contract

        :param to_pay_ether: (Decimal) : amount (in ether) to transfer from the calling account
        :param date_args_uint256_array_4: (uint256[4]) : - 0 - expirationDate - date when bank expire. 1 - lddInvestEquity - timestamp 2 - lddInvestDebt - timestamp 3 - lddBorrow - timestamp
        :param deploy_num_args_uint256_array_4: (uint256[4]) : - 0 - _minimumReserveRatio - percentage amount multiplied by RATE_PRECISION_MULTIPLIER which corresponds to minimum equity that should always remain in the bank as a percentage of total debt and equity investments made in this bank. 1 - commission - amount of commission relative to _srcAmount provided to comply minEquity rule. 2 - _debtInterest - percentage interest on debt investments 3 - _srcAmount - amount of equity user is willing to deploy within the context of transaction to deployBank. The value is provided in loanToken terms.
        :param _loan_token_address: (address) : - address of bank funding currency
        :param data_bytes: (bytes) : - bytes that represent collateral matrix for the bank.
        :return: an UnsentTransaction for [address]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.deployBank(date_args_uint256_array_4, deploy_num_args_uint256_array_4, _loan_token_address, data_bytes), to_pay_ether)
