import json
import os
from typing import List, Dict, Any

from solc import compile_standard
from eth_utils import add_0x_prefix

from .files import find_files

DEFAULT_OUTPUT_SELECTION = [
    "abi",
    "devdoc",
    "userdoc",
    "metadata",
    "evm.bytecode",
    "evm.deployedBytecode",
]

ABI_OUTPUT_SELECTION = ["abi", "userdoc"]


def load_sources(file_paths: List[str]):
    result = {}
    for file_path in file_paths:
        with open(file_path) as source_file:
            result[file_path] = {"content": source_file.read()}
    return result


def normalize_contract_data(contract_data: Dict):
    result = {}

    for key, value in contract_data.items():
        if key == "evm":
            evm_data = value

            if "bytecode" in evm_data:
                result["bytecode"] = add_0x_prefix(
                    evm_data["bytecode"].get("object", "")
                )

            if "deployedBytecode" in evm_data:
                result["deployedBytecode"] = add_0x_prefix(
                    evm_data["deployedBytecode"].get("object", "")
                )

        elif key == "metadata":
            if value:
                result[key] = json.loads(value)

        else:
            result[key] = value

    return result


def normalize_compiled_contracts(compiled_contracts: Dict, file_paths: List[str]):
    result: Dict[str, Dict] = {}

    for source_path, file_contracts in compiled_contracts.items():
        if source_path not in file_paths:
            continue

        for contract_name, raw_contract_data in file_contracts.items():
            contract_data = normalize_contract_data(raw_contract_data)
            if contract_name not in result:
                result[contract_name] = contract_data
            else:
                raise BaseException("Can not compile two contracts with the same name")

    return result


def log_compilation_errors(errors: List[Dict]):
    for error in errors:
        if "formattedMessage" in error:
            print(error["formattedMessage"])
        else:
            print(error["message"])


def compile_project(
    contracts_path: str = None,
    *,
    file_paths: List[str] = None,
    allow_paths: List[str] = None,
    pattern="*.sol",
    optimize=False,
    only_abi=False,
    evm_version: str = "byzantium",
):
    """
    Compiles all contracts of the project into a single output
    Args:
        contracts_path: The path of the folder that includes the contracts, defaults to 'contracts'
        file_paths: A list of to compiled contracts can be provided (optional)
        allow_paths: Additional paths from where it is allowed to load contracts
        pattern: The pattern to find the solidity files
        optimize: Whether to turn on the solidity optimizer
        only_abi: Whether to only create the abi or not
        evm_version: target evm version to use for generated code

    Returns: A dictionary containing the compiled assets of the contracts

    """

    if file_paths is None:
        file_paths = []

    if allow_paths is None:
        allow_paths = []

    if contracts_path is None and not file_paths:
        contracts_path = "contracts"

    if contracts_path is not None:
        file_paths.extend(find_files(contracts_path, pattern=pattern))
        allow_paths.append(contracts_path)

    sources = load_sources(file_paths)

    if only_abi:
        output_selection = ABI_OUTPUT_SELECTION
    else:
        output_selection = DEFAULT_OUTPUT_SELECTION

    std_input = {
        "language": "Solidity",
        "sources": sources,
        "settings": {
            "outputSelection": {"*": {"*": output_selection}},
            "evmVersion": evm_version,
        },
    }

    if optimize:
        std_input["settings"]["optimizer"] = {"enabled": True, "runs": 500}

    compilation_result = compile_standard(
        std_input, allow_paths=",".join(os.path.abspath(path) for path in allow_paths)
    )

    if "errors" in compilation_result:
        log_compilation_errors(compilation_result["errors"])

    compiled_contracts = normalize_compiled_contracts(
        compilation_result["contracts"], file_paths
    )
    return compiled_contracts


def compile_contract(
    name: str, *, contracts_path="contracts", file_extension=".sol", optimize=False
):
    filename = name + file_extension
    file_paths = list(find_files(contracts_path, filename))

    if len(file_paths) < 1:
        raise ValueError("File not found: {}".format(filename))

    if len(file_paths) > 1:
        raise ValueError("Multiple files found: {}".format(file_paths))

    compiled_contracts = compile_project(
        file_paths=file_paths, allow_paths=[contracts_path], optimize=optimize
    )
    return compiled_contracts[name]


class UnknownContractException(Exception):
    pass


def filter_contracts(
    contract_names: List[str], contract_assets_in: Dict[str, Any]
) -> Dict[str, Any]:
    if contract_names is None:
        return contract_assets_in.copy()

    output_dict: Dict[str, Any] = {}
    try:
        for contract_name in contract_names:
            output_dict[contract_name] = contract_assets_in[contract_name]
    except KeyError as e:
        raise UnknownContractException(*e.args) from e

    return output_dict
