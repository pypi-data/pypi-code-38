from datetime import date
import time
from decimal import Decimal

from eth_account import Account
from eth_account.signers.local import LocalAccount

import nomisma.contractapi.testutil.TruffleContract
import nomisma.contractapi.util
import web3._utils.abi
from web3 import Web3

from nomisma.contractapi.BankRegistryAbstract import BankRegistryAbstract
from nomisma.contractapi.asyncexec import AsyncExec
from nomisma.contractapi.signer import LocalAccountSigner, SingletonLocalSingerFactory
from nomisma.contractapi.testutil.FullERC20MockAbstract import FullERC20MockAbstract

delegate_contracts = ['BankInvest.json', 'BankStateGetters.json', 'BankRedeem.json',
                      'BankInitialise.json', 'BankBorrow.json', 'TokenManager.json']

DAY_IN_SECONDS = 24 * 3600

RATE_PRECISION_MULTIPLIER = 10 ** 4

ETHER_TO_WAY_FACTOR = Decimal(1e18)


def from_abi(web3, name):
    return ContractForTest(web3, nomisma.contractapi.testutil.TruffleContract.from_abi(name))


def from_mock_abi(web3, name):
    return ContractForTest(web3, nomisma.contractapi.testutil.TruffleContract.from_mock_abi(name))


class CapitalStructureTestResource:
    def __init__(self,
                 web3=None,
                 deployment_account: LocalAccount=None,
                 governor_account: LocalAccount=None,
                 commission_beneficiary_address=None,
                 date_keeper_data=None,
                 min_equity_balance=1,
                 commission_percentage=0.1):
        if web3 is None:
            self.web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        else:
            self.web3 = web3
        self.asyncexec = AsyncExec(10, poll_interval=0.1)
        if deployment_account is None:
            self.deployment_account = local_test_accounts[0]
        else:
            self.deployment_account = deployment_account
        if governor_account is None:
            self.governor_account = local_test_accounts[1]
        else:
            self.governor_account = governor_account
        self.deployment_signer = SingletonLocalSingerFactory.signer(self.web3, self.deployment_account)
        self.governor_signer = SingletonLocalSingerFactory.signer(self.web3, self.governor_account)
        if commission_beneficiary_address is None:
            self.commission_beneficiary_address = local_test_accounts[2].address
        else:
            self.commission_beneficiary_address = commission_beneficiary_address
        if date_keeper_data is None:
            self.date_keeper_data = DateKeeperData()
        else:
            self.date_keeper_data = date_keeper_data
        self.min_equity_balance=min_equity_balance
        self.commission_percentage=int(commission_percentage/100*RATE_PRECISION_MULTIPLIER)
        self.bank_registry = None

    def tearDown(self):
        self.asyncexec.shutdown()

    def fund_test_accounts(self, funding_account: LocalAccount, ether_amount: Decimal):
        signer = SingletonLocalSingerFactory.signer(self.web3, funding_account)
        for acct in local_test_accounts:
            tx_dict1 = dict(
                gasPrice=self.web3.eth.gasPrice,
                gas=100000,
                to=acct.address,
                value=int(ether_amount * ETHER_TO_WAY_FACTOR)
            )
            tx_hash1 = self.web3.eth.sendRawTransaction(signer.sign(tx_dict1))
            self.web3.eth.waitForTransactionReceipt(tx_hash1)


    def deploy_delegate_contracts(self):
        delegates = []
        self.contract_address_map = {}
        for json_contract in delegate_contracts:
            contract_for_test = from_abi(self.web3, json_contract)
            contract_for_test.deploy_nowait(self.deployment_signer)
            delegates.append(contract_for_test)
        for i in range(len(delegate_contracts)):
            self.contract_address_map[delegate_contracts[i]] = delegates[i].get_address()

    def populate_resolver(self, resolver, name):
        truffle_to_add = from_abi(self.web3, name).truffle_contract
        destination = self.contract_address_map[name]
        w3_contract = self.web3.eth.contract(
            abi=truffle_to_add.abi())
        sig_hashes = []
        addresses = []
        tx_hashes = []
        for f in w3_contract.all_functions():
            signature = web3._utils.abi.abi_to_signature(f.abi)
            signature_hash = Web3.keccak(text=signature)
            sig_hashes.append(signature_hash)
            addresses.append(destination)
            if len(sig_hashes) == 2:
                tx_hash = self.send_tx(resolver.callable().functions.bulkRegister(sig_hashes, addresses),
                                       self.governor_signer)
                tx_hashes.append(tx_hash)
                sig_hashes.clear()
                addresses.clear()
        if len(sig_hashes) > 0:
            tx_hash = self.send_tx(resolver.callable().functions.bulkRegister(sig_hashes, addresses),
                                   self.governor_signer)
            tx_hashes.append(tx_hash)
        for tx_hash in tx_hashes:
            self.web3.eth.waitForTransactionReceipt(tx_hash)

    def send_tx(self, func, signer):
        gas = 5699999 # func.estimateGas() * 4
        tx_dict = func.buildTransaction({'gas': gas})
        return self.web3.eth.sendRawTransaction(signer.sign(tx_dict))

    def deploy_bank_registry(self):
        token_manager_resolver = from_abi(self.web3, 'Resolver.json')
        token_manager_resolver.deploy_nowait(self.deployment_signer, self.governor_account.address)

        self.populate_resolver(token_manager_resolver, 'TokenManager.json')

        token_manager_router = from_abi(self.web3, 'TokenManagerRouter.json')
        token_manager_router.deploy_nowait(self.deployment_signer, self.governor_account.address,
                                           token_manager_resolver.get_address())

        exchange_mock = from_mock_abi(self.web3, 'ExchangeConnectorMock.json')
        exchange_mock.deploy_nowait(self.deployment_signer, self.governor_account.address, token_manager_router.get_address())

        ddd = self.date_keeper_data
        bank_date_keeper = from_abi(self.web3, 'BankDateKeeper.json')
        bank_date_keeper.deploy_nowait(self.deployment_signer, self.governor_account.address, ddd.weekly_config(),
                                       ddd.bank_dates(), ddd.bank_dates_interval_starts(),
                                       ddd.bank_dates_interval_ends())

        bank_resolver = from_abi(self.web3, 'Resolver.json')
        bank_resolver.deploy_nowait(self.deployment_signer, self.governor_account.address)

        self.populate_resolver(bank_resolver, 'BankBorrow.json')
        self.populate_resolver(bank_resolver, 'BankInvest.json')
        self.populate_resolver(bank_resolver, 'BankRedeem.json')
        self.populate_resolver(bank_resolver, 'BankInitialise.json')
        self.populate_resolver(bank_resolver, 'BankStateGetters.json')

        self.token_validator = from_abi(self.web3, 'TokenValidator.json')
        self.token_validator.deploy_nowait(self.deployment_signer, self.governor_account.address)

        self.bank_registry = from_abi(self.web3, 'BankRegistry.json')
        self.bank_registry.deploy_nowait(self.deployment_signer, self.min_equity_balance, self.commission_percentage,
                                    exchange_mock.get_address(), token_manager_router.get_address(),
                                    bank_date_keeper.get_address(), self.governor_account.address,
                                    bank_resolver.get_address(), self.token_validator.get_address(),
                                    self.commission_beneficiary_address)

        bank_event_emitter = from_abi(self.web3, 'BankEventEmitter.json')
        bank_event_emitter.deploy_nowait(self.deployment_signer, self.bank_registry.get_address())

        tx_hash = self.send_tx(self.bank_registry.callable().functions.setEventEmitter(bank_event_emitter.get_address()),
                               self.governor_signer)
        self.web3.eth.waitForTransactionReceipt(tx_hash)

    def bank_registry_instance(self, signer_account=None):
        signer = None
        if signer_account is not None:
            signer = SingletonLocalSingerFactory.signer(self.web3, signer_account)
        return BankRegistryAbstract(self.web3, self.asyncexec, self.bank_registry.get_address(), signer)

    def create_new_erc20_token(self, owner_signer: LocalAccountSigner, name: str, symbol: str, decimals: int, amount_to_mint: int)\
            -> FullERC20MockAbstract:
        erc20_contract = from_mock_abi(self.web3, 'FullERC20Mock.json')
        erc20_contract.deploy_nowait(owner_signer, name, symbol, decimals, amount_to_mint)
        tx_hash = self.send_tx(self.token_validator.callable().functions.addTokensToWhitelist([erc20_contract.get_address()]),
                               self.governor_signer)
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        return FullERC20MockAbstract(self.web3, self.asyncexec, erc20_contract.get_address(), owner_signer)

    def test_signer(self, index:int) -> LocalAccountSigner:
        return SingletonLocalSingerFactory.signer(self.web3, local_test_accounts[index])

class ContractForTest:
    def __init__(self, web3, truffle_contract):
        self.truffle_contract = truffle_contract
        self.w3 = web3
        self.tx_receipt = None
        self.tx_hash = None
        self.instance_contract = None

    def deploy_nowait(self, deploy_signer: LocalAccountSigner, *constructor_args):
        w3_contract = self.w3.eth.contract(
            abi=self.truffle_contract.abi(),
            bytecode=self.truffle_contract.bytecode())
        constructor = w3_contract.constructor(*constructor_args)
        gas = constructor.estimateGas()
        # if gas > 3000000:
        #     gas = 3000000
        tx_dict = constructor.buildTransaction({'gas': gas})
        raw_tx = deploy_signer.sign(tx_dict)
        self.tx_hash = self.w3.eth.sendRawTransaction(raw_tx)

    def get_address(self):
        if self.tx_receipt is None:
            self.tx_receipt = self.w3.eth.waitForTransactionReceipt(self.tx_hash)
        return self.tx_receipt['contractAddress']

    def callable(self):
        if self.instance_contract is None:
            self.instance_contract = self.w3.eth.contract(abi=self.truffle_contract.abi(), address=self.get_address())
        return self.instance_contract


class DateKeeperData:
    fixed_maturity_week_day = 5
    fixed_q_maturity_week = 3

    def __init__(self, initial_timestamp=None, weeks_in_future_enabled=4,
                 ldd_interval_start=DAY_IN_SECONDS, ldd_interval_end=DAY_IN_SECONDS * 2,
                 min_interval_since_bank_deployment_ts=604800):
        if initial_timestamp is None:
            self.initial_timestamp = nomisma.contractapi.util.str_to_eth_time('Jan 1, 2019 @ 00:00:00 UTC')
        else:
            self.initial_timestamp = initial_timestamp
        self.weeks_in_future_enabled = weeks_in_future_enabled
        self.ldd_interval_start = ldd_interval_start
        self.ldd_interval_end = ldd_interval_end
        self.min_interval_since_bank_deployment_ts = min_interval_since_bank_deployment_ts

    def weekly_config(self):
        return [self.initial_timestamp, self.weeks_in_future_enabled, self.ldd_interval_start,
                self.ldd_interval_end, self.min_interval_since_bank_deployment_ts]

    def third_friday(self, year, month):
        return date(year, month,
                    self.fixed_maturity_week_day + self.fixed_q_maturity_week * 7)  # this isn't a friday!??

    def bank_dates(self):
        # march, june, september, december
        fixed_q_maturity_months = [3, 6, 9, 12]
        # third week of the month

        today = date.today()
        fixed_dates = []
        for month in fixed_q_maturity_months:
            year = today.year
            if today.month + 3 >= month:
                year += 1
            fixed_dates.append(int(time.mktime(self.third_friday(year, month).timetuple()) + 8 * 3600))

        fixed_dates.sort()
        return fixed_dates

    def bank_dates_interval_starts(self):
        return [DAY_IN_SECONDS, DAY_IN_SECONDS, DAY_IN_SECONDS, DAY_IN_SECONDS]

    def bank_dates_interval_ends(self):
        return [DAY_IN_SECONDS * 3, DAY_IN_SECONDS * 3, DAY_IN_SECONDS * 3, DAY_IN_SECONDS * 3]

local_test_accounts = []
local_test_accounts.append(Account.from_key("0xb174a963ccf49e9e84dbf91568624e8254f0e0351ffd9cca69c43ae937efd132"))
local_test_accounts.append(Account.from_key("0xddeff2733e6142c873df7bede7db29055471ebeae7090ef618996a51daa4cd8c"))
local_test_accounts.append(Account.from_key("0x9abc12c2cbdd4673e69bb5ac2e3995646cb89945f9b835fd6cc7e53743b60373"))
local_test_accounts.append(Account.from_key("0xc7a3efd1427b1beb08adaa9b537395b134168f15921d6c9f4eaefba01fc9a332"))
local_test_accounts.append(Account.from_key("0xaa04f62c15f5dadbf6f53835a95f981a466ef8a600dc6c6a992ef4b4b8d42b3b"))
local_test_accounts.append(Account.from_key("0x167adfc076e9610a89aebbf837479051f2349644a85e0a050dd1095cc1d3f926"))
local_test_accounts.append(Account.from_key("0xe5132f71ad0a22d4f37970b6758cd39b1a55f03496698be5243df62810cbce4c"))
local_test_accounts.append(Account.from_key("0x750cb95a3702c3d659b79185e25057a41ebc6f6a4aedf401854da7173714e39e"))
local_test_accounts.append(Account.from_key("0x8a19cffa8176f4d16c3a738a5f3d986d563d83a274ee325cd6fb84909149e605"))
local_test_accounts.append(Account.from_key("0xde760f1be3de32d19d3473cc8ce34a0f4f13e64ffb9b9a76f33efd4b7bfc2daa"))
local_test_accounts.append(Account.from_key("0x5e9b2f25294ef0f292f51ac7a3b678307349f619c443a9b5df55121b525e41aa"))
local_test_accounts.append(Account.from_key("0x81eff67d09a3b2a2c6cf029e3ea31cd3828c2d92ad6aec637fa06af839779a1e"))
local_test_accounts.append(Account.from_key("0xbb55a91411b1208a304e1a8e5c58dc64cdfb79e7fbab0e3f7228229926dfc3bc"))
local_test_accounts.append(Account.from_key("0x1ff18be82e17f852ce4faab60b6997aaed0991dd99130d54b9316b650323490b"))
local_test_accounts.append(Account.from_key("0x73fd232e4678b78041405f5d3400f3f7fd9ee88547f7e16bbd34d04206c747d8"))
local_test_accounts.append(Account.from_key("0xb5b63e2923d00546b1f966433a1d2daa727bea7f3b310ad384c63ac06d69b575"))
local_test_accounts.append(Account.from_key("0x9db466bf6aaca64a09661e0f4635c69d41c923fecf1f856e5f783f7004c46495"))
local_test_accounts.append(Account.from_key("0x193b7713e8dd900481dba0f136c4a8e712957827666c05abae1f318be52cc557"))
local_test_accounts.append(Account.from_key("0xe020f76c4eafce67f6abda0e7aae037a63159d922d17a44603d37dbf84fbb250"))
local_test_accounts.append(Account.from_key("0xbb9d1719fa787b8ffe70e2a1c988224686062db6e753ec5cfca1b8c597e4491b"))