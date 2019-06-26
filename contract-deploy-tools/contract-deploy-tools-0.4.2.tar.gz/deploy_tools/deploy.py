from typing import Dict
import pkg_resources
import json

from eth_keyfile import extract_key_from_keyfile
from web3.contract import Contract
from web3 import Web3
from web3.eth import Account
from web3._utils.transactions import fill_nonce


def deploy_compiled_contract(
    *,
    abi,
    bytecode,
    web3: Web3,
    constructor_args=(),
    transaction_options: Dict = None,
    private_key=None
) -> Contract:
    """
    Deploys a compiled contract either using an account of the node, or a local private key
    It will block until the transaction was successfully mined.

    Returns: The deployed contract as a web3 contract

    """
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    constuctor_call = contract.constructor(*constructor_args)

    receipt = send_function_call_transaction(
        constuctor_call,
        web3=web3,
        transaction_options=transaction_options,
        private_key=private_key,
    )

    address = receipt["contractAddress"]
    return contract(address)


def send_function_call_transaction(
    function_call, *, web3: Web3, transaction_options: Dict = None, private_key=None
):
    """
    Creates, signs and sends a transaction from a function call (for example created with `contract.functions.foo()`.
    Will either use an account of the node(default), or a local private key(if given) to sign the transaction.
    It will block until the transaction was successfully mined.

    Returns: The transaction receipt

    """
    if transaction_options is None:
        transaction_options = {}

    if private_key is not None:
        signed_transaction = _build_and_sign_transaction(
            function_call,
            web3=web3,
            transaction_options=transaction_options,
            private_key=private_key,
        )
        tx_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
    else:
        tx_hash = function_call.transact(transaction_options)

    return wait_for_successful_transaction_receipt(web3, tx_hash)


class TransactionFailed(Exception):
    pass


def wait_for_successful_transaction_receipt(web3: Web3, txid: str, timeout=180) -> dict:
    """See if transaction went through (Solidity code did not throw).
    :return: Transaction receipt
    """
    receipt = web3.eth.waitForTransactionReceipt(txid, timeout=timeout)
    status = receipt.get("status", None)
    if status is False:
        raise TransactionFailed
    return receipt


def load_contracts_json(package_name, filename="contracts.json") -> Dict:
    resource_package = package_name
    json_string = pkg_resources.resource_string(resource_package, filename)
    return json.loads(json_string)


def decrypt_private_key(keystore_path: str, password: str) -> bytes:
    return extract_key_from_keyfile(keystore_path, password.encode("utf-8"))


def build_transaction_options(*, gas, gas_price, nonce):

    transaction_options = {}

    if gas is not None:
        transaction_options["gas"] = gas
    if gas_price is not None:
        transaction_options["gasPrice"] = gas_price
    if nonce is not None:
        transaction_options["nonce"] = nonce

    return transaction_options


def increase_transaction_options_nonce(transaction_options: Dict) -> None:
    """Increases the nonce inside of `transaction_options` by 1 if present.
    If there is no nonce in `transaction_options`, this function will not do anything
    """
    if "nonce" in transaction_options:
        transaction_options["nonce"] = transaction_options["nonce"] + 1


def _build_and_sign_transaction(
    function_call, *, web3, transaction_options, private_key
):
    account = Account.privateKeyToAccount(private_key)

    if "from" in transaction_options and transaction_options["from"] != account.address:
        raise ValueError(
            "From can not be set in transaction_options if a private key is used"
        )
    transaction_options["from"] = account.address

    transaction = fill_nonce(web3, function_call.buildTransaction(transaction_options))

    return account.signTransaction(transaction)
