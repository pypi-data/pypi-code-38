#!/usr/bin/env python

from collections import namedtuple
from typing import Callable, List

from .wallet import Wallet


class InflightWalletBalance:
    __slots__ = ["sender", "dst_address", "tx_hash", "send_timestamp", "currency", "amount",
                 "gas_price_gwei", "gas_used", "sent", "received"]

    def __init__(self, sender: Wallet, dst_address: str, tx_hash: str, send_timestamp: float, currency: str,
                 amount: float, gas_price_gwei: float, gas_used: float):
        self.sender: Wallet = sender
        self.dst_address: str = dst_address
        self.tx_hash: str = tx_hash
        self.send_timestamp: float = send_timestamp
        self.currency: str = currency
        self.amount: float = amount
        self.gas_price_gwei: float = gas_price_gwei
        self.gas_used: float = gas_used
        self.sent: bool = False
        self.received: bool = False

    def __repr__(self) -> str:
        return f"InflightWalletBalance('{repr(self.sender)}', '{self.dst_address}', '{self.tx_hash}', " \
               f"{self.send_timestamp}, '{self.currency}', {self.amount}, {self.gas_price_gwei}, {self.gas_amount}) " \
               f"sent={self.sent}, received={self.received}"


class InflightTransaction(namedtuple("_InflightTransaction",
                                     "send_timestamp, tx_hash, func, args")):
    send_timestamp: float
    tx_hash: str
    func: Callable
    args: List[any]


