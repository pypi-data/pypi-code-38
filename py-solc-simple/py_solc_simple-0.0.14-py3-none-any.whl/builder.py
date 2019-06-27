import json
import os
from solcx import compile_standard
from pathlib import Path

"""
Created by Kelvin Fichter. Code lifted from omisego/plasma-contracts by Paul Peregud and moved into separate package.
"""


class Builder(object):

    def __init__(self, contracts_dir, output_dir):
        self.contracts_dir = contracts_dir
        self.output_dir = output_dir

    def get_solc_input(self):
        """Walks the contract directory and returns a Solidity input dict

        Learn more about Solidity input JSON here: https://goo.gl/7zKBvj

        Returns:
            dict: A Solidity input JSON object as a dict
        """

        def legal(r, file_name):
            hidden = file_name[0] == '.'
            dotsol = len(file_name) > 3 and file_name[-4:] == '.sol'
            path = os.path.normpath(os.path.join(r, file_name))
            notfile = not os.path.isfile(path)
            symlink = Path(path).is_symlink()
            return dotsol and (not (symlink or hidden or notfile))

        solc_input = {
            'language': 'Solidity',
            'sources': {
                file_name: {
                    'urls': [os.path.realpath(os.path.join(r, file_name))]
                } for r, d, f in os.walk(self.contracts_dir) for file_name in f if legal(r, file_name)
            },
            'settings': {
                'optimizer': {
                    'enabled': 1,
                    'runs': 10000
                },
                'outputSelection': {
                    "*": {
                        "": [
                            "legacyAST",
                            "ast"
                        ],
                        "*": [
                            "abi",
                            "evm.bytecode.object",
                            "evm.bytecode.sourceMap",
                            "evm.deployedBytecode.object",
                            "evm.deployedBytecode.sourceMap"
                        ]
                    }
                }
            }
        }

        return solc_input

    def compile_all(self):
        """Compiles all of the contracts in the self.contracts_dir directory

        Creates {contract name}.json files in self.output_dir that contain
        the build output for each contract.
        """

        # Solidity input JSON
        solc_input = self.get_solc_input()

        # Compile the contracts
        real_path = os.path.realpath(self.contracts_dir)
        compilation_result = compile_standard(solc_input, allow_paths=real_path)

        # Create the output folder if it doesn't already exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Write the contract ABI to output files
        compiled_contracts = compilation_result['contracts']
        for contract_file in compiled_contracts:
            for contract in compiled_contracts[contract_file]:
                contract_name = contract.split('.')[0]
                contract_data = compiled_contracts[contract_file][contract_name]

                contract_data_path = self.output_dir + '/{0}.json'.format(contract_name)
                with open(contract_data_path, "w+") as contract_data_file:
                    json.dump(contract_data, contract_data_file)

    def get_contract_data(self, contract_name):
        """Returns the contract data for a given contract

        Args:
            contract_name (str): Name of the contract to return.

        Returns:
            str, str: ABI and bytecode of the contract
        """

        contract_data_path = self.output_dir + '/{0}.json'.format(contract_name)
        with open(contract_data_path, 'r') as contract_data_file:
            contract_data = json.load(contract_data_file)

        abi = contract_data['abi']
        bytecode = contract_data['evm']['bytecode']['object']

        return abi, bytecode


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Compiles solidity contracts. Can also be used as a library.')
    parser.add_argument('-o', '--out_dir', required=True,
                        help='output directory (will be created if needed)')
    parser.add_argument('-i', '--input_dir', required=True,
                        help='input directory (will be recursively crawled)')
    args = parser.parse_args()

    builder = Builder(args.input_dir, args.out_dir)
    builder.compile_all()
