import argparse
import json
from buguet.debugger import Debugger
from buguet.repl import Repl
from web3.middleware import geth_poa_middleware
from web3 import Web3, HTTPProvider, IPCProvider

def main():
    parser = argparse.ArgumentParser(description='Ethereum debugger')

    parser.add_argument('--rpc', help="RPC of the ethereum node. Default is http://localhost:8545.", default="http://localhost:8545")
    parser.add_argument('--source-roots', help="Comma separated list of directies where source files will be searched in case there are relative source paths in combined json", default=".")
    parser.add_argument('combined_json', help="""
        Comma separated list of json files produced by solidity compiler with --combined-json argument.
        Files should cover all called contracts (original contract can call another during transaction).
        Fields which are required in combined json are ast,bin,bin-runtime,srcmap,srcmap-runtime. See solidity docs.
        Json file also contains the links to source files which will be loaded during debugging (sourceList). Either they
        should be absolute or --source-roots option should be provided for resolving relative paths.
        """)
    parser.add_argument('transaction_id', help='Id of the transaction to debug')

    args = parser.parse_args()

    if args.rpc.startswith("http"):
        provider = HTTPProvider(args.rpc)
    else:
        provider = IPCProvider(args.rpc)

    web3 = Web3(provider)
    web3.middleware_stack.inject(geth_poa_middleware, layer=0)
    json_files = args.combined_json.split(",")
    data = list(map(lambda f: json.load(open(f)), json_files))

    debugger = Debugger(web3, data, args.transaction_id, args.source_roots.split(","))
    Repl(debugger).repl()

