

class Admin(object):

    def __init__(self, host_addr: str or Admin = None):

        self._abci_info_url = None
        self._abci_query_url = None
        self._block_url = None
        self._block_result_url = None
        self._block_chain_url = None
        self._broadcast_tx_async_url = None
        self._broadcast_tx_commit_url = None
        self._broadcast_tx_sync_url = None
        self._commit_url = None
        self._consensus_params_url = None
        self._dump_consensus_url = None
        self._genesis_url = None
        self._health_url = None
        self._net_info_url = None
        self._num_unconfirmed_txs_url = None
        self._status_url = None
        self._subscribe_url = None
        self._tx_url = None
        self._tx_search_url = None
        self._unconfirmed_txs_url = None
        self._unsubscribe_url = None
        self._unsubscribe_all_url = None
        self._validators_url = None

        if isinstance(host_addr, str):
            self.set_rpc_host(host_addr)
        elif isinstance(host_addr, Admin):
            self.set_rpc_host(host_addr.host)
        elif host_addr is None:
            self.rpc_host = None
        else:
            raise TypeError("not valid admin/host address type")

    @property
    def host(self):
        return self.rpc_host

    @property
    def abci_info_url(self):
        return self._abci_info_url

    @property
    def abci_query_url(self):
        return self._abci_query_url

    @property
    def broadcast_tx_commit_url(self):
        return self._broadcast_tx_commit_url

    def set_rpc_host(self, host_name):
        self.rpc_host = host_name

        self._abci_info_url = self.rpc_host + "/abci_info"
        self._abci_query_url = self.rpc_host + "/abci_query"
        self._broadcast_tx_commit_url = self.rpc_host + "/broadcast_tx_commit"

        return host_name


_admin_singleton = Admin("http://127.0.0.1:26657")
_admin_singleton_mode = False
# _admin_list = []


def _get_admin_singleton(_=None):
    global _admin_singleton
    return _admin_singleton


def _get_admin_no_singleton(*args, **kwargs):
    return Admin(*args, **kwargs)


get_admin = _get_admin_no_singleton


def set_admin_singleton_mode(mode_on):
    global _admin_singleton_mode
    global get_admin
    _admin_singleton_mode = mode_on
    if mode_on:
        get_admin = _get_admin_singleton
    else:
        get_admin = _get_admin_no_singleton
