from typing import Sequence

import click
from web3 import Web3, EthereumTesterProvider, Account
from web3._utils.abi import get_constructor_abi, get_abi_input_types
from eth_utils import encode_hex

from .files import (
    write_pretty_json_asset,
    ensure_path_for_file_exists,
    write_minified_json_asset,
    validate_and_format_address,
    InvalidAddressException,
)
from .deploy import (
    decrypt_private_key,
    build_transaction_options,
    deploy_compiled_contract,
    send_function_call_transaction,
)
from .compile import filter_contracts, UnknownContractException, compile_project


# we need test_provider and test_json_rpc for running the tests in test_cli
# they need to persist between multiple calls to runner.invoke and are
# therefore initialized on the module level.
test_provider = EthereumTesterProvider()
test_json_rpc = Web3(test_provider)


def validate_address(ctx, param, value):
    try:
        return validate_and_format_address(value)
    except InvalidAddressException as e:
        raise click.BadParameter(
            f"The address parameter is not recognized to be an address: {value}"
        ) from e


jsonrpc_option = click.option(
    "--jsonrpc",
    help="JsonRPC URL of the ethereum client",
    default="http://127.0.0.1:8545",
    show_default=True,
    metavar="URL",
)
keystore_option = click.option(
    "--keystore",
    help="Path to the encrypted keystore",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
)
gas_option = click.option(
    "--gas", help="Gas of the transaction to be sent", type=int, default=None
)
gas_price_option = click.option(
    "--gas-price",
    help="Gas price of the transaction to be sent",
    type=int,
    default=None,
)
nonce_option = click.option(
    "--nonce", help="Nonce of the first transaction to be sent", type=int, default=None
)
auto_nonce_option = click.option(
    "--auto-nonce",
    help="automatically determine the nonce of first transaction to be sent",
    default=False,
    is_flag=True,
)

contracts_dir_option = click.option(
    "--contracts-dir",
    "-d",
    help="Directory of the contracts sources",
    default="contracts",
    show_default=True,
    type=click.Path(file_okay=False, exists=True),
)
optimize_option = click.option(
    "--optimize",
    "-O",
    default=False,
    help="Turns on the solidity optimizer",
    is_flag=True,
)
evm_version_option = click.option(
    "--evm-version",
    type=str,
    help="The evm target version, one of: "
    "petersburg, constantinople, byzantium, spuriousDragon, tangerineWhistle, or homestead",
    show_default=True,
    default="byzantium",
)
contract_address_option = click.option(
    "--contract-address",
    help=("The address of the deployed contract, '0x' prefixed string"),
    type=str,
    required=True,
    callback=validate_address,
)


@click.group()
def main():
    pass


@main.command(short_help="Compile all contracts")
@contracts_dir_option
@optimize_option
@evm_version_option
@click.option(
    "--only-abi",
    default=False,
    help="Only include the abi of the contracts",
    is_flag=True,
)
@click.option(
    "--minimize",
    default=False,
    help="Minimizes the output file by removing unnecessary whitespaces",
    is_flag=True,
)
@click.option(
    "--contract-names",
    default=None,
    help="Comma separated list of contract names to include in the output, default is to include all contracts",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True, exists=False),
    help="Name of the output file",
    show_default=True,
    default="build/contracts.json",
)
def compile(
    contracts_dir, optimize, evm_version, only_abi, minimize, contract_names, output
):
    if contract_names is not None:
        contract_names = contract_names.split(",")

    ensure_path_for_file_exists(output)

    try:
        compiled_contracts = filter_contracts(
            contract_names,
            compile_project(
                contracts_dir,
                optimize=optimize,
                only_abi=only_abi,
                evm_version=evm_version,
            ),
        )
    except UnknownContractException as e:
        raise click.BadOptionUsage(
            "contract-names", f"Could not find contract: {e.args[0]}"
        )
    if minimize:
        write_minified_json_asset(compiled_contracts, output)
    else:
        write_pretty_json_asset(compiled_contracts, output)


@main.command(short_help="Deploys a contract")
@click.argument("contract-name", type=str)
@click.argument("args", nargs=-1, type=str)
@gas_option
@gas_price_option
@nonce_option
@auto_nonce_option
@keystore_option
@jsonrpc_option
@contracts_dir_option
@optimize_option
@evm_version_option
def deploy(
    contract_name: str,
    args: Sequence[str],
    gas: int,
    gas_price: int,
    nonce: int,
    auto_nonce: bool,
    keystore: str,
    jsonrpc: str,
    contracts_dir,
    optimize,
    evm_version,
):
    """
    Deploys a contract

    Deploys a contract with the name CONTRACT_NAME and the constructor arguments ARGS.

    """
    web3 = connect_to_json_rpc(jsonrpc)
    private_key = retrieve_private_key(keystore)

    nonce = get_nonce(
        web3=web3, nonce=nonce, auto_nonce=auto_nonce, private_key=private_key
    )
    transaction_options = build_transaction_options(
        gas=gas, gas_price=gas_price, nonce=nonce
    )

    compiled_contracts = compile_project(
        contracts_dir, optimize=optimize, evm_version=evm_version
    )

    if contract_name not in compiled_contracts:
        raise click.BadArgumentUsage(f"Contract {contract_name} was not found.")

    abi = compiled_contracts[contract_name]["abi"]
    bytecode = compiled_contracts[contract_name]["bytecode"]

    contract = deploy_compiled_contract(
        abi=abi,
        bytecode=bytecode,
        constructor_args=parse_args_to_matching_types_for_constructor(args, abi),
        web3=web3,
        transaction_options=transaction_options,
        private_key=private_key,
    )

    click.echo(contract.address)


@main.command(short_help="Sends a transaction to a contract function")
@click.argument("contract-name", type=str)
@click.argument("function-name", type=str)
@click.argument("args", nargs=-1, type=str)
@gas_option
@gas_price_option
@nonce_option
@auto_nonce_option
@keystore_option
@jsonrpc_option
@contracts_dir_option
@contract_address_option
def transact(
    contract_name: str,
    function_name: str,
    args: Sequence[str],
    gas: int,
    gas_price: int,
    nonce: int,
    auto_nonce: bool,
    keystore: str,
    jsonrpc: str,
    contracts_dir,
    contract_address,
):
    web3 = connect_to_json_rpc(jsonrpc)
    private_key = retrieve_private_key(keystore)

    nonce = get_nonce(
        web3=web3, nonce=nonce, auto_nonce=auto_nonce, private_key=private_key
    )
    transaction_options = build_transaction_options(
        gas=gas, gas_price=gas_price, nonce=nonce
    )

    compiled_contracts = compile_project(contracts_dir)

    if contract_name not in compiled_contracts:
        raise click.BadArgumentUsage(f"Contract {contract_name} was not found.")

    contract_abi = compiled_contracts[contract_name]["abi"]
    contract = web3.eth.contract(abi=contract_abi, address=contract_address)
    function_abi = get_contract_matching_function(contract_abi, function_name, args)
    parsed_arguments = parse_args_to_matching_types_for_function(args, function_abi)
    function_call = contract.functions[function_name](*parsed_arguments)

    receipt = send_function_call_transaction(
        function_call,
        web3=web3,
        transaction_options=transaction_options,
        private_key=private_key,
    )

    click.echo(encode_hex(receipt.transactionHash))


def connect_to_json_rpc(jsonrpc) -> Web3:
    if jsonrpc == "test":
        web3 = test_json_rpc
    else:
        web3 = Web3(Web3.HTTPProvider(jsonrpc, request_kwargs={"timeout": 180}))
    return web3


def retrieve_private_key(keystore_path):
    """
    return the private key corresponding to keystore or none if keystore is none
    """

    private_key = None

    if keystore_path is not None:
        password = click.prompt(
            "Please enter the password to decrypt the keystore",
            type=str,
            hide_input=True,
        )
        private_key = decrypt_private_key(keystore_path, password)

    return private_key


def get_nonce(*, web3: Web3, nonce: int, auto_nonce: bool, private_key: bytes):
    """get the nonce to be used as specified via command line options

     we do some option checking in this function. It would be better to do this
     before doing any real work, but we would need another function then.
    """
    if auto_nonce and not private_key:
        raise click.UsageError("--auto-nonce requires --keystore argument")
    if nonce is not None and auto_nonce:
        raise click.UsageError(
            "--nonce and --auto-nonce cannot be used at the same time"
        )

    if auto_nonce:
        return web3.eth.getTransactionCount(
            Account.privateKeyToAccount(private_key).address, block_identifier="pending"
        )
    else:
        return nonce


def get_contract_matching_function(contract_abi, function_name, args):
    candidates = [
        abi
        for abi in contract_abi
        if abi["type"] == "function"
        and abi["name"] == function_name
        and len(abi["inputs"]) == len(args)
    ]

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        raise ValueError("Found no function matching the name and input length.")
    elif len(candidates) > 1:
        raise ValueError("Found multiple function matching name and input length.")


def parse_args_to_matching_types_for_constructor(args, contract_abi):
    """Parses a list of commandline arguments to the abi matching python types"""
    constructor_abi = get_constructor_abi(contract_abi)
    if constructor_abi:
        return parse_args_to_matching_types_for_function(args, constructor_abi)
    return []


def parse_args_to_matching_types_for_function(args, function_abi):
    types = get_abi_input_types(function_abi)
    return [parse_arg_to_matching_type(arg, type) for arg, type in zip(args, types)]


def parse_arg_to_matching_type(arg, type: str):
    """Parses a commandline argument to the abi matching python type"""
    if type.find("int") != -1:
        return int(arg)
    if type.find("bool") != -1:
        if arg.lower() == "true":
            return True
        if arg.lower() == "false":
            return False
        raise ValueError(f"Expected true or false, but got {arg}")
    if (
        type.find("address") != -1
        or type.find("bytes") != -1
        or type.find("string") != -1
    ):
        return arg
    raise ValueError(f"Cannot handle parameter of type {type} yet.")
