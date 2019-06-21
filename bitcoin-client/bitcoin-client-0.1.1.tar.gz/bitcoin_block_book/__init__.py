import requests
from urllib.parse import urljoin


class BitcoinClient:
    def __init__(self, host):
        self.api_host = host

    def get_last_height(self):
        """
        Get last height.
        :return:
        """
        url = urljoin(self.api_host, "api/status/")
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()['backend']['blocks']
        return data

    def get_block_hash(self, block_num):
        """
        Get block hash by block num.
        """
        url = urljoin(self.api_host, f"api/block-index/{block_num}")
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()['blockHash']
        return data

    def get_sender_address(self, txid):
        """
        Get sender address
        :param txid:
        :return: address or None
        """
        url = urljoin(self.api_host, f"/api/tx/{txid}")

        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        vin = data['vin']
        try:
            address = vin[0]["addresses"][0]
        except:
            address = None
        return address

    def get_block(self, block_hash, page_num=1):
        """
        Get block info by hash per page
        :param block_hash:
        :param page_num:
        :return:
        """
        url = urljoin(self.api_host, f"/api/block/{block_hash}?page={page_num}")
        r = requests.get(url)
        r.raise_for_status()
        block = r.json()
        return block

    def get_tx(self, tx_hash):
        """
        Get tx info by tx hash
        :param tx_hash:
        :return:
        """
        url = urljoin(self.api_host, f"/api/tx/{tx_hash}")
        r = requests.get(url)
        r.raise_for_status()
        block = r.json()
        return block


