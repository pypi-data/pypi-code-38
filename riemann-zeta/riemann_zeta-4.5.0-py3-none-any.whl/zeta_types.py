from riemann import tx
from mypy_extensions import TypedDict

from typing import Union, List, Optional


class Header(TypedDict):
    hash: str
    version: int
    prev_block: str
    merkle_root: str
    timestamp: int
    nbits: str
    nonce: str
    difficulty: int
    hex: str
    height: int
    accumulated_work: int


class AddressEntry(TypedDict):
    address: str
    script: bytes  # the redeem script for p2sh/p2wsh
    script_pubkeys: List[str]  # parsed pubkeys in the redeem script


class Outpoint(TypedDict):
    tx_id: str  # block explorer format
    index: int


class Prevout(TypedDict):
    outpoint: Outpoint
    value: int  # in satoshi
    spent_at: int  # block height
    spent_by: str  # txid
    address: str


class PrevoutEntry(TypedDict):  # the DB formatted prevout
    outpoint: str  # tx serialization format
    tx_id: str  # block explorers
    idx: int
    value: int  # in sat
    spent_at: int  # block height
    spent_by: str  # txid
    address: str


class KeyEntry(TypedDict):
    address: str
    privkey: bytes  # encrypted when in the DB
    pubkey: str
    derivation: str
    chain: str  # deprecated


class TransactionEntry(TypedDict):
    tx_id: str
    lock_time: int
    version: int
    num_tx_ins: int
    num_tx_outs: int
    total_value_out: int
    confirmed_in: Optional[str]  # block hash
    confirmed_height: int  # block height
    merkle_verified: bool
    hex: str
    object: tx.Tx


class InputEntry(TypedDict):
    spent_by: str
    outpoint: str
    tx_id: str
    idx: int
    sequence: int


class OutputEntry(TypedDict):
    included_in: str
    value: int
    pubkey_script: bytes
    address: str
    outpoint: str


class ElectrumGetHeadersResponse(TypedDict):
    count: int
    hex: str
    max: int


class ElectrumHeader(TypedDict):
    height: int
    hex: str


class ElectrumStatusDict(TypedDict):
    scripthash: str
    status: str


class ElectrumHistoryTx(TypedDict):
    height: int
    tx_hash: str


class ElectrumMempoolTx(ElectrumHistoryTx):
    fee: int


ElectrumHeaderNotification = \
    Union[List[ElectrumHeader], ElectrumHeader]


ElectrumScripthashNotification = \
    Union[List[ElectrumStatusDict], ElectrumStatusDict]
