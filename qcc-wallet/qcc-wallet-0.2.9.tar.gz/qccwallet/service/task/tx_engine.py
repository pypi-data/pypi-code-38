from tweb import scheduler, time
from ...db import mongo as db
from ...service import ctrl_wallet, ctrl_contract
import asyncio
from ..external import ethereum as ex_ethereum


def start():
    interval = 1
    scheduler.add_interval(_tx_checking, interval)


async def _tx_checking():
    cursor = db.tx.find({
        'status': {'$in': [0, 10]}
    })

    pending_list = list()
    wallets = dict()

    # 按from地址分组
    for tx in cursor:
        if tx['status'] == 0:
            address = tx['from']
            if address not in wallets:
                wallets[address] = list()
            wallets[address].append(tx)
        elif tx['status'] == 10:
            pending_list.append(tx)

    # 对已广播的交易查询是否已在链上确认
    if len(pending_list) > 0:
        tasks = [_check(tx) for tx in pending_list]
        await asyncio.gather(*tuple(tasks))

    # 对未广播交易列表进行广播
    if len(wallets) > 0:
        tasks = [_cast(address, tx_list) for address, tx_list in wallets.items()]
        await asyncio.gather(*tuple(tasks))


async def _cast(sender_address, tx_list):
    nonce = ex_ethereum.get_tx_count(sender_address)

    last = db.tx.find_one({'from': sender_address, 'status': {'$in': [10, 20]}})
    if last is not None:
        last_nonce = last['nonce'] + 1
        nonce = max(nonce, last_nonce)

    for tx in tx_list:
        contract_id = tx['contract_id']
        data = tx['raw_data']

        tx_info = await ctrl_wallet.tx_cast(contract_id, sender_address, data, nonce=nonce)
        nonce += 1

        tx_info.pop('from')
        tx.update(tx_info)
        tx['status'] = 10
        tx['ts_cast'] = time.millisecond()
        db.tx.update_one({'_id': tx['_id']}, {'$set': tx})


async def _check(tx):
    block_number = ex_ethereum.block_number()
    contract = ctrl_contract.simple_read(tx['contract_id'])

    tx_info = await ctrl_wallet.tx_info(contract['catalog']['cid'], tx['hash'])

    block_no = tx_info.get('blockNumber')
    if block_no is not None and block_number - block_no >= 0:
        tx_info.pop('from')
        tx.update(tx_info)
        tx['status'] = 20
        tx['ts_mined'] = time.millisecond()
        db.tx.update_one({'_id': tx['_id']}, {'$set': tx})
