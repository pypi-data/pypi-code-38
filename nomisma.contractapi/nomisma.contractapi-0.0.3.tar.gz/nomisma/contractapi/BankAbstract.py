from decimal import *
from typing import Tuple
from nomisma.contractapi.asyncexec import UnsentTransaction, Promise
from nomisma.contractapi.meta import ContractMetaData
from nomisma.contractapi.util import from_abi


# This is code generated. Do not modify! Add methods and overrides to the subclass.
class BankAbstract:
    def __init__(self, web3, asyncexec, address, signer=None):
        abi = from_abi('Bank.json')['abi']
        self.meta_ = ContractMetaData(web3, asyncexec, address, abi, signer)
        self.w3_contract = web3.eth.contract(abi=abi, address=address)

    def get_loan_token(self) -> Promise:
        """
        Solidity signature: getLoanToken()
        Returns an address of `loanToken`.

        :return: a Promise for [address] that is executed asynchronously
        """
        f = self.w3_contract.functions.getLoanToken()
        return self.meta_.asyncexec.submit(f.call)

    def resolver(self) -> Promise:
        f = self.w3_contract.functions.resolver()
        return self.meta_.asyncexec.submit(f.call)

    def loan_token(self) -> Promise:
        f = self.w3_contract.functions.loanToken()
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

    def get_ltv_interest_length_for_token(self,
                                          token_address) -> Promise[int]:
        """
        Solidity signature: getLtvInterestLengthForToken(address)
        Gets all loan-to-value rates (`ltvRates` array) for a chosen token.

        :param token_address: (address) : - address of a chosen token.
        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.getLtvInterestLengthForToken(token_address)
        return self.meta_.asyncexec.submit(f.call)

    def collateral_tokens(self,
                          param0: int) -> Promise:
        f = self.w3_contract.functions.collateralTokens(param0)
        return self.meta_.asyncexec.submit(f.call)

    def get_ethereum_address(self) -> Promise:
        """
        Solidity signature: getEthereumAddress()
        Returns ethereum address using `TokenManager` contract.

        :return: a Promise for [address] that is executed asynchronously
        """
        f = self.w3_contract.functions.getEthereumAddress()
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

    def ltv_rates(self,
                  param0_address,
                  param1: int) -> Promise[int]:
        f = self.w3_contract.functions.ltvRates(param0_address, param1)
        return self.meta_.asyncexec.submit(f.call)

    def borrower_loan_idxes(self,
                            param0_address,
                            param1: int) -> Promise[int]:
        f = self.w3_contract.functions.borrowerLoanIdxes(param0_address, param1)
        return self.meta_.asyncexec.submit(f.call)

    def token_manager(self) -> Promise:
        f = self.w3_contract.functions.tokenManager()
        return self.meta_.asyncexec.submit(f.call)

    def get_rate_matrix_for_collateral_type(self,
                                            collateral_type_address) -> Promise:
        """
        Solidity signature: getRateMatrixForCollateralType(address)
        Gets rate matrix (`ltvRates` + `interestRates` arrays) for a chosen `collateralType` token. For every collateral token address that this bank accepts it specifies an array of collateral ratio and interest rate pairs. When the loan is issued the borrower picks collateral token and an index of appropriate collateral ratio and interest rate pair. The respective pair is used to calculate loan interest rate and loan amount given collateral ratio.

        :param collateral_type_address: (address) : - address of a chosen `collateralToken` to get rate matrix for.
        :return: a Promise for [Tuple[uint256[], uint256[]]] that is executed asynchronously
        """
        f = self.w3_contract.functions.getRateMatrixForCollateralType(collateral_type_address)
        return self.meta_.asyncexec.submit(f.call)

    def get_debt_payout(self,
                        tokens_amount: int) -> Promise[int]:
        f = self.w3_contract.functions.getDebtPayout(tokens_amount)
        return self.meta_.asyncexec.submit(f.call)

    def get_rate_by_ctype_idx(self,
                              collateral_type_address,
                              idx: int) -> Promise[Tuple[int, int]]:
        """
        Solidity signature: getRateByCtypeIdx(address,uint256)
        Returns `ltvRate` and `interestRate` for a chosen collateral type.

        :param collateral_type_address: (address) : - address of a chosen `collateralToken` to get rates for.
        :param idx: (int) : - index of a row in ltv and interest rate matrix.
        :return: a Promise for [Tuple[int, int]] that is executed asynchronously
        """
        f = self.w3_contract.functions.getRateByCtypeIdx(collateral_type_address, idx)
        return self.meta_.asyncexec.submit(f.call)

    def commission_beneficiary(self) -> Promise:
        f = self.w3_contract.functions.commissionBeneficiary()
        return self.meta_.asyncexec.submit(f.call)

    def get_loan(self,
                 idx: int) -> Promise:
        """
        Solidity signature: getLoan(uint256)
        Gets bytes type `Loan` hash from index passed.

        :param idx: (int) : - index of a `Loan` to get.
        :return: a Promise for [bytes] that is executed asynchronously
        """
        f = self.w3_contract.functions.getLoan(idx)
        return self.meta_.asyncexec.submit(f.call)

    def get_token(self,
                  equity: bool) -> Promise:
        """
        Solidity signature: getToken(bool)
        Returns ERC20 token address of `equityToken` or `debtToken`.

        :param equity: (bool) : - boolean value that represents if the token is `equityToken` or `debtToken`.
        :return: a Promise for [address] that is executed asynchronously
        """
        f = self.w3_contract.functions.getToken(equity)
        return self.meta_.asyncexec.submit(f.call)

    def total_debt_payout(self) -> Promise[int]:
        f = self.w3_contract.functions.totalDebtPayout()
        return self.meta_.asyncexec.submit(f.call)

    def loan_outstanding_amount(self) -> Promise[int]:
        """
        Solidity signature: loanOutstandingAmount()
        Function shows how much should be paid to close all current `Loans`.

        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.loanOutstandingAmount()
        return self.meta_.asyncexec.submit(f.call)

    def get_exchange_rate(self,
                          src_address,
                          dest_address,
                          src_amount: int) -> Promise[int]:
        """
        Solidity signature: getExchangeRate(address,address,uint256)
        Gets exchange rate between two chosen ERC20 tokens using `ExchangeConnector` contract.

        :param src_address: (address) : - source token.
        :param dest_address: (address) : - destination token.
        :param src_amount: (int) : - the amount of source token to calculate exchange rate for.
        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.getExchangeRate(src_address, dest_address, src_amount)
        return self.meta_.asyncexec.submit(f.call)

    def get_repay_amount(self,
                         loan_idx: int) -> Promise[int]:
        """
        Solidity signature: getRepayAmount(uint256)
        Gets `repayAmount` for a chosen `Loan`.

        :param loan_idx: (int) : - index of a `Loan` struct to get `repayAmount` for.
        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.getRepayAmount(loan_idx)
        return self.meta_.asyncexec.submit(f.call)

    def max_loans_per_borrower(self) -> Promise[int]:
        f = self.w3_contract.functions.MAX_LOANS_PER_BORROWER()
        return self.meta_.asyncexec.submit(f.call)

    def get_collateral_tokens_length(self) -> Promise[int]:
        """
        Solidity signature: getCollateralTokensLength()
        Gets the amount of `collateralTokens` used (length of `collateralTokens` array).

        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.getCollateralTokensLength()
        return self.meta_.asyncexec.submit(f.call)

    def registry(self) -> Promise:
        f = self.w3_contract.functions.registry()
        return self.meta_.asyncexec.submit(f.call)

    def bank_properties(self) -> Promise[Tuple[int, int, bool, int, int, int, int, int, int, bool, int, int, int, bool]]:
        f = self.w3_contract.functions.bankProperties()
        return self.meta_.asyncexec.submit(f.call)

    def date_keeper(self) -> Promise:
        f = self.w3_contract.functions.dateKeeper()
        return self.meta_.asyncexec.submit(f.call)

    def event_emitter(self) -> Promise:
        f = self.w3_contract.functions.eventEmitter()
        return self.meta_.asyncexec.submit(f.call)

    def get_outstanding_repay_amount(self,
                                     loan_idx: int) -> Promise[int]:
        f = self.w3_contract.functions.getOutstandingRepayAmount(loan_idx)
        return self.meta_.asyncexec.submit(f.call)

    def base_multiplier(self) -> Promise[int]:
        f = self.w3_contract.functions.BASE_MULTIPLIER()
        return self.meta_.asyncexec.submit(f.call)

    def interest_rates(self,
                       param0_address,
                       param1: int) -> Promise[int]:
        f = self.w3_contract.functions.interestRates(param0_address, param1)
        return self.meta_.asyncexec.submit(f.call)

    def get_resolver(self) -> Promise:
        """
        Solidity signature: getResolver()
        Gets the address of a Resolver contract.

        :return: a Promise for [address] that is executed asynchronously
        """
        f = self.w3_contract.functions.getResolver()
        return self.meta_.asyncexec.submit(f.call)

    def get_bank_properties(self) -> Promise[Tuple[int, int, int, int, int]]:
        f = self.w3_contract.functions.getBankProperties()
        return self.meta_.asyncexec.submit(f.call)

    def get_equity_payout(self,
                          tokens_amount: int) -> Promise[int]:
        """
        Solidity signature: getEquityPayout(uint256)
        Calculates payout for `equityTokens` (how much `equityToken` would be paid according to a situation).

        :param tokens_amount: (int) : - the amount of `equityTokens`.
        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.getEquityPayout(tokens_amount)
        return self.meta_.asyncexec.submit(f.call)

    def exchange_connector(self) -> Promise:
        f = self.w3_contract.functions.exchangeConnector()
        return self.meta_.asyncexec.submit(f.call)

    def equity_token(self) -> Promise:
        f = self.w3_contract.functions.equityToken()
        return self.meta_.asyncexec.submit(f.call)

    def raw_data(self) -> Promise:
        f = self.w3_contract.functions.rawData()
        return self.meta_.asyncexec.submit(f.call)

    def rate_precision_multiplier(self) -> Promise[int]:
        f = self.w3_contract.functions.RATE_PRECISION_MULTIPLIER()
        return self.meta_.asyncexec.submit(f.call)

    def max_loans(self) -> Promise[int]:
        f = self.w3_contract.functions.MAX_LOANS()
        return self.meta_.asyncexec.submit(f.call)

    def loans(self,
              param0: int) -> Promise:
        f = self.w3_contract.functions.loans(param0)
        return self.meta_.asyncexec.submit(f.call)

    def maclaurin_precision(self) -> Promise[int]:
        f = self.w3_contract.functions.MACLAURIN_PRECISION()
        return self.meta_.asyncexec.submit(f.call)

    def get_borrow_amount(self,
                          collateral_type_address,
                          collateral_amount: int,
                          desired_idx: int) -> Promise[int]:
        """
        Solidity signature: getBorrowAmount(address,uint256,uint256)
        Gets `borrowAmount` for a chosen `Loan`.

        :param collateral_type_address: (address) : - address of a chosen `collateralToken`.
        :param collateral_amount: (int) : - the amount of a chosen `collateralToken`.
        :param desired_idx: (int) : - index used to get `ltvRates` and `interestRates` for a chosen `collateralToken`.
        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.getBorrowAmount(collateral_type_address, collateral_amount, desired_idx)
        return self.meta_.asyncexec.submit(f.call)

    def get_event_emitter(self) -> Promise:
        """
        Solidity signature: getEventEmitter()
        Gets the address of a BankEventEmitter contract through BankRegistry contract.

        :return: a Promise for [address] that is executed asynchronously
        """
        f = self.w3_contract.functions.getEventEmitter()
        return self.meta_.asyncexec.submit(f.call)

    def governance_role_name(self) -> Promise[str]:
        f = self.w3_contract.functions.GOVERNANCE_ROLE_NAME()
        return self.meta_.asyncexec.submit(f.call)

    def get_loans_length(self) -> Promise[int]:
        """
        Solidity signature: getLoansLength()
        Returns length of `loans` array.

        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.getLoansLength()
        return self.meta_.asyncexec.submit(f.call)

    def debt_token(self) -> Promise:
        f = self.w3_contract.functions.debtToken()
        return self.meta_.asyncexec.submit(f.call)

    def redeem_debt_tokens(self,
                           tokens_amount: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: redeemDebtTokens(uint256)
        Function used to redeem `debtTokens` from `borrowers` in case of a repaid or defaulted loan. Checks necessary conditions and transfers tokens. payoutAmount =  = ((totalRepaid - totalBorrowed) * equityDebtRatio * tokensAmount / debtTokensSuppy) + tokensAmount where: payoutAmount - amount in loanToken which debt depositor receives totalRepaid - amount in loanToken of repaid loans (only borrows which are actually repaid are taken into account here) totalBorrowed - amount in loanToken of borrowed loans (only borrows which are actually repaid are taken into account here) equityDebtRatio - value between 0 and 1 which defines the profits split between equity depositor and debt depositor tokensAmount - amount of debtTokens the debtDepositor is redeeming debtTokensSuppy - total amount of debtTokens issued (across all debt depositors)

        :param tokens_amount: (int) : - the amount of `debtTokens` to be redeemed.
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.redeemDebtTokens(tokens_amount))

    def redeem_equity_tokens(self,
                             tokens_amount: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: redeemEquityTokens(uint256)
        Function used to redeem `equityTokens` in case of a repaid or defaulted loan. Checks necessary conditions and transfers tokens.

        :param tokens_amount: (int) : - the amount of `equityTokens` to be redeemed.
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.redeemEquityTokens(tokens_amount))

    def deposit_equity(self,
                       to_pay_ether: Decimal,
                       amount: int,
                       commission: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: depositEquity(uint256,uint256)
        Mints and deposits equity. Sets corresponding state variables (`stateNumVariables`).

        :param to_pay_ether: (Decimal) : amount (in ether) to transfer from the calling account
        :param amount: (int) : - the amount of `equityTokens` to be minted and deposited.
        :param commission: (int) : - the commission of investment which correlates with amount using commissionPercentage rule
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.depositEquity(amount, commission), to_pay_ether)

    def deposit_debt(self,
                     to_pay_ether: Decimal,
                     amount: int,
                     commission: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: depositDebt(uint256,uint256)
        Mints and deposits debt. Sets corresponding state variables (`stateNumVariables`).

        :param to_pay_ether: (Decimal) : amount (in ether) to transfer from the calling account
        :param amount: (int) : - the amount of `debtTokens` to be minted and deposited.
        :param commission: (int) : - the commission of deposit which correlates with amount using commissionPercentage rule
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.depositDebt(amount, commission), to_pay_ether)

    def borrow(self,
               to_pay_ether: Decimal,
               collateral_type_address,
               collateral_amount: int,
               desired_idx: int) -> UnsentTransaction[None]:
        """
        Solidity signature: borrow(address,uint256,uint256)
        Function used to borrow tokens from Bank by setting state variables, creating `Loan` structs and transfering `loanToken`.

        :param to_pay_ether: (Decimal) : amount (in ether) to transfer from the calling account
        :param collateral_type_address: (address) : - ERC20 token used as a `collateralToken`.
        :param collateral_amount: (int) : 
        :param desired_idx: (int) : - index used to get `ltvRates` and `interestRates` for a chosen `collateralToken`.
        :return: an UnsentTransaction for [None]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.borrow(collateral_type_address, collateral_amount, desired_idx), to_pay_ether)

    def pay_back_loans(self,
                       to_pay_ether: Decimal,
                       loan_idxes_uint256_list,
                       payback_amounts_uint256_list) -> UnsentTransaction[None]:
        """
        Solidity signature: payBackLoans(uint256[],uint256[])
        Pays back `Loan` s according to requirements. Does all necessery transfers.

        :param to_pay_ether: (Decimal) : amount (in ether) to transfer from the calling account
        :param loan_idxes_uint256_list: (uint256[]) : - indexes of loans to be paid back.
        :param payback_amounts_uint256_list: (uint256[]) : - amounts to be paid back for each of the respective loanIdxes.
        :return: an UnsentTransaction for [None]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.payBackLoans(loan_idxes_uint256_list, payback_amounts_uint256_list), to_pay_ether)

    def preinit(self,
                to_pay_ether: Decimal,
                address_args_address_array_8,
                number_args_uint256_array_6,
                date_args_uint256_array_4,
                data_bytes) -> UnsentTransaction[bool]:
        """
        Solidity signature: preinit(address[8],uint256[6],uint256[4],bytes)
        Initializes all necessary contracts for BankProtocol, sets state variables, runs before `init` function. and setting `BankEventEmitter` contract.

        :param to_pay_ether: (Decimal) : amount (in ether) to transfer from the calling account
        :param address_args_address_array_8: (address[8]) : - 0 - eventEmitter address 1 - exchangeConnector address 2 - tokenManager address - `ERC20` contract used for creating `loanTokens`. 3 - dateKeeper address 4 - commissionBeneficiary - beneficiary of all bank commission. This address would receive all commission collected by this bank. 5 - loanToken address - loan token is the token which is the main token for the bank. Loans are issued in loan token and debt depositors as well as equity depositors can deposit equity/debt only in loanToken terms. Loan token can be any ERC‌-20 asset as well as Ethereum itself. 6 - bank creator address 7 - token validator address
        :param number_args_uint256_array_6: (uint256[6]) : - 0 - debtInterest - debt interest ratio with RATE_PRECISION_MULTIPLIER as precision. Should be always lower then RATE_PRECISION_MULTIPLIER. 1 - minEquityBalance - minimum balance in Ether that has to be passed upon bank construction. If minimum balance requirement is not met - bank deployment would revert. 2 - commissionPercentage - percentage size of commission for invest/deposit transaction which should be submitted with every invest/deposit transaction as well as on bank deployment for covering minEquity. 3 - srcAmount - actual amount that bank creator wants to invest in equity. Usable only when loanToken is not Ether itself. 4 - commission - commission amount sent together with bank deployment transaction 5 - minimumReserveRatio - minimum amount of equity/debt to keep in reserve when creating loans. This value is provided in percentage with RATE_PRECISION_MULTIPLIER as a multiplier and thus would be always lower then RATE_PRECISION_MULTIPLIER. if minimumReserveRatio is equal to RATE_PRECISION_MULTIPLIER this means that minimumReserveRatio is 100%.
        :param date_args_uint256_array_4: (uint256[4]) : - 0 - expirationDate - date when bank expire. 1 - lddInvestEquity - timestamp 2 - lddInvestDebt - timestamp 3 - lddBorrow - timestamp
        :param data_bytes: (bytes) : 
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.preinit(address_args_address_array_8, number_args_uint256_array_6, date_args_uint256_array_4, data_bytes), to_pay_ether)
