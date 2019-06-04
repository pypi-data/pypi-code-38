from decimal import *
from typing import Tuple
from nomisma.contractapi.asyncexec import UnsentTransaction, Promise
from nomisma.contractapi.meta import ContractMetaData
from nomisma.contractapi.testutil.mockutil import from_abi


# This is code generated. Do not modify! Add methods and overrides to the subclass.
class FullERC20MockAbstract:
    def __init__(self, web3, asyncexec, address, signer=None):
        abi = from_abi('FullERC20Mock.json')['abi']
        self.meta_ = ContractMetaData(web3, asyncexec, address, abi, signer)
        self.w3_contract = web3.eth.contract(abi=abi, address=address)

    def name(self) -> Promise[str]:
        """
        Solidity signature: name()

        :return: a Promise for [str] that is executed asynchronously
        """
        f = self.w3_contract.functions.name()
        return self.meta_.asyncexec.submit(f.call)

    def total_supply(self) -> Promise[int]:
        """
        Solidity signature: totalSupply()
        Total number of tokens in existence

        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.totalSupply()
        return self.meta_.asyncexec.submit(f.call)

    def decimals(self) -> Promise:
        """
        Solidity signature: decimals()

        :return: a Promise for [uint8] that is executed asynchronously
        """
        f = self.w3_contract.functions.decimals()
        return self.meta_.asyncexec.submit(f.call)

    def balance_of(self,
                   owner_address) -> Promise[int]:
        """
        Solidity signature: balanceOf(address)
        Gets the balance of the specified address.

        :param owner_address: (address) : The address to query the balance of.
        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.balanceOf(owner_address)
        return self.meta_.asyncexec.submit(f.call)

    def symbol(self) -> Promise[str]:
        """
        Solidity signature: symbol()

        :return: a Promise for [str] that is executed asynchronously
        """
        f = self.w3_contract.functions.symbol()
        return self.meta_.asyncexec.submit(f.call)

    def is_minter(self,
                  account_address) -> Promise[bool]:
        f = self.w3_contract.functions.isMinter(account_address)
        return self.meta_.asyncexec.submit(f.call)

    def allowance(self,
                  owner_address,
                  spender_address) -> Promise[int]:
        """
        Solidity signature: allowance(address,address)
        Function to check the amount of tokens that an owner allowed to a spender.

        :param owner_address: (address) : address The address which owns the funds.
        :param spender_address: (address) : address The address which will spend the funds.
        :return: a Promise for [int] that is executed asynchronously
        """
        f = self.w3_contract.functions.allowance(owner_address, spender_address)
        return self.meta_.asyncexec.submit(f.call)

    def approve(self,
                spender_address,
                value: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: approve(address,uint256)
        Approve the passed address to spend the specified amount of tokens on behalf of msg.sender. Beware that changing an allowance with this method brings the risk that someone may use both the old and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards: https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729

        :param spender_address: (address) : The address which will spend the funds.
        :param value: (int) : The amount of tokens to be spent.
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.approve(spender_address, value))

    def transfer_from(self,
                      from_address,
                      to_address,
                      value: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: transferFrom(address,address,uint256)
        Transfer tokens from one address to another. Note that while this function emits an Approval event, this is not required as per the specification, and other compliant implementations may not emit the event.

        :param from_address: (address) : address The address which you want to send tokens from
        :param to_address: (address) : address The address which you want to transfer to
        :param value: (int) : uint256 the amount of tokens to be transferred
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.transferFrom(from_address, to_address, value))

    def increase_allowance(self,
                           spender_address,
                           added_value: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: increaseAllowance(address,uint256)
        Increase the amount of tokens that an owner allowed to a spender. approve should be called when _allowed[msg.sender][spender] == 0. To increment allowed value is better to use this function to avoid 2 calls (and wait until the first transaction is mined) From MonolithDAO Token.sol Emits an Approval event.

        :param spender_address: (address) : The address which will spend the funds.
        :param added_value: (int) : The amount of tokens to increase the allowance by.
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.increaseAllowance(spender_address, added_value))

    def mint(self,
             to_address,
             value: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: mint(address,uint256)
        Function to mint tokens

        :param to_address: (address) : The address that will receive the minted tokens.
        :param value: (int) : The amount of tokens to mint.
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.mint(to_address, value))

    def burn(self,
             value: int) -> UnsentTransaction[None]:
        """
        Solidity signature: burn(uint256)
        Burns a specific amount of tokens.

        :param value: (int) : The amount of token to be burned.
        :return: an UnsentTransaction for [None]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.burn(value))

    def burn_from(self,
                  from_address,
                  value: int) -> UnsentTransaction[None]:
        """
        Solidity signature: burnFrom(address,uint256)
        Burns a specific amount of tokens from the target address and decrements allowance

        :param from_address: (address) : address The account whose tokens will be burned.
        :param value: (int) : uint256 The amount of token to be burned.
        :return: an UnsentTransaction for [None]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.burnFrom(from_address, value))

    def add_minter(self,
                   account_address) -> UnsentTransaction[None]:
        return UnsentTransaction(self.meta_, self.w3_contract.functions.addMinter(account_address))

    def renounce_minter(self) -> UnsentTransaction[None]:
        return UnsentTransaction(self.meta_, self.w3_contract.functions.renounceMinter())

    def decrease_allowance(self,
                           spender_address,
                           subtracted_value: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: decreaseAllowance(address,uint256)
        Decrease the amount of tokens that an owner allowed to a spender. approve should be called when _allowed[msg.sender][spender] == 0. To decrement allowed value is better to use this function to avoid 2 calls (and wait until the first transaction is mined) From MonolithDAO Token.sol Emits an Approval event.

        :param spender_address: (address) : The address which will spend the funds.
        :param subtracted_value: (int) : The amount of tokens to decrease the allowance by.
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.decreaseAllowance(spender_address, subtracted_value))

    def transfer(self,
                 to_address,
                 value: int) -> UnsentTransaction[bool]:
        """
        Solidity signature: transfer(address,uint256)
        Transfer token to a specified address

        :param to_address: (address) : The address to transfer to.
        :param value: (int) : The amount to be transferred.
        :return: an UnsentTransaction for [bool]
        """
        return UnsentTransaction(self.meta_, self.w3_contract.functions.transfer(to_address, value))
