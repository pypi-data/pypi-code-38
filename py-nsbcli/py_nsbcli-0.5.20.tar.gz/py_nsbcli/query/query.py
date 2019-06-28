
from py_nsbcli.modules import Client


class QueryX:
    def __init__(self, bind_cli):
        self.cli = Client(bind_cli)

    def get_account_info(self, data: str, height=0, prove=False):
        return self.cli.abci_query('acc_getAccInfo', data, height, prove)

    def query_map(self, data: str, height=0, prove=False):
        return self.cli.abci_query('prove_on_state_trie', data, height, prove)

    def query_tx_map(self, data: str, height=0, prove=False):
        return self.cli.abci_query('prove_on_tx_trie', data, height, prove)

    def query_account_map(self, data: str, height=0, prove=False):
        return self.cli.abci_query('prove_on_account_trie', data, height, prove)

    def query_action_map(self, data: str, height=0, prove=False):
        return self.cli.abci_query('prove_on_action_trie', data, height, prove)

    def query_valid_merkle_proof_map(self, data: str, height=0, prove=False):
        return self.cli.abci_query('prove_on_valid_merkle_proof_trie', data, height, prove)

    def query_valid_on_chain_merkle_proof_map(self, data: str, height=0, prove=False):
        return self.cli.abci_query('prove_on_valid_on_chain_merkle_proof_trie', data, height, prove)

    def get_storage_at(self, data: str, height=0, prove=False):
        return self.cli.abci_query('prove_get_storage_at', data, height, prove)


