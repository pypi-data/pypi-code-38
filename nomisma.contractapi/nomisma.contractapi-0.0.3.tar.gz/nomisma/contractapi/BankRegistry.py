from decimal import Decimal

from datetime import date, datetime

from nomisma.contractapi.BankRegistryAbstract import BankRegistryAbstract
from typing import Dict, List, Tuple

from nomisma.contractapi.util import date_to_eth_time, datetime_to_eth_time, rate_to_int


def to_bytes(v: int, length: int) -> bytes:
    return v.to_bytes(length, byteorder='big')


def encode_matrix(ltv_and_interest_rates: Dict[str, Tuple[List[Decimal], List[Decimal]]]) -> bytearray:
    result = bytearray()
    result.extend(to_bytes(len(ltv_and_interest_rates), 32))  # outer length
    for addr, (ltv_rates, interest_rates) in ltv_and_interest_rates:
        if len(addr) != 42:
            raise ValueError('address is not the right length in hex format!')
        if len(ltv_rates) != len(interest_rates):
            raise ValueError('ltv and interest rates must be the same length!')
        result.extend(bytearray.fromhex(addr[2:]))
        result.extend(bytearray(to_bytes(len(ltv_rates), 12)))  # address + len encode to 32 bytes, aka uint256
        for i in range(0, len(ltv_rates)):
            result.extend(to_bytes(rate_to_int(ltv_rates[i]), 16))
            result.extend(to_bytes(rate_to_int(interest_rates[i]), 16))
    return result

class BankRegistry(BankRegistryAbstract):
    def __init__(self, web3, asyncexec, address, caller_account=None):
        super().__init__(web3, asyncexec, address, caller_account)

    def create_bank(self,
                    to_pay_ether: Decimal,
                    expiration_date: date,
                    ldd_invest_equity: datetime,
                    ldd_invest_debt: datetime,
                    ldd_borrow: datetime,
                    minimum_reserve_ratio: Decimal,
                    commission: int,
                    debt_interest: Decimal,
                    src_amount: int,
                    loan_token_address,
                    ltv_and_interest_rates: Dict[str, Tuple[List[Decimal], List[Decimal]]]):
        """
        creates a new Bank by deploying a Bank contract with the given parameters

        :param to_pay_ether: (Decimal) : amount (in ether) to transfer from the calling account
        :param expiration_date: date: date when bank expire.
        :param ldd_invest_equity: datetime
        :param ldd_invest_debt: datetime
        :param ldd_borrow: datetime
        :param minimum_reserve_ratio: percentage amount which corresponds to minimum equity that should always remain
            in the bank as a percentage of total debt and equity investments made in this bank.
        :param commission: amount of commission relative to _srcAmount provided to comply minEquity rule.
        :param debt_interest: percentage interest on debt investments
        :param src_amount: int: amount of equity user is willing to deploy within the context of transaction to
            deployBank. The value is provided in loanToken terms.
        :param loan_token_address: address of bank funding currency
        :param ltv_and_interest_rates: Dict[str, Tuple[List[Decimal], List[Decimal]]]: a dictionary with token address
            as the key. The value is a tuple of arrays that correspond to the ltv and interest rates form that account.
        :return: an UnsentTransaction for [address] address of the deployed bank
        """
        return self.deploy_bank(to_pay_ether,
                                [date_to_eth_time(expiration_date),
                                 datetime_to_eth_time(ldd_invest_equity),
                                 datetime_to_eth_time(ldd_invest_debt),
                                 datetime_to_eth_time(ldd_borrow)],
                                [rate_to_int(minimum_reserve_ratio),
                                 commission,
                                 rate_to_int(debt_interest),
                                 src_amount],
                                loan_token_address,
                                encode_matrix(ltv_and_interest_rates))