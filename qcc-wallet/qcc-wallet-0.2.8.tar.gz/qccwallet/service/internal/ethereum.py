import config
from tweb.error_exception import ErrException, ERROR
from web3 import Web3
import glob
from eth_account.messages import defunct_hash_message
import logging

provider = Web3.IPCProvider('{}/geth.ipc'.format(config.Ethereum['internal']['path']))
web3 = Web3(provider)

contracts = dict()


def wei2ether(number):
    return web3.fromWei(number, 'ether')


def new_account(pwd):
    return web3.personal.newAccount(pwd).lower()


def is_address(address):
    return web3.isAddress(address)


def get_contract(contract_address, abi):
    try:
        contract_address = to_crc_address(contract_address)
        ret = contracts.get(contract_address)
        if ret is None:
            ret = web3.eth.contract(contract_address, abi=abi)
            contracts[contract_address] = ret
        return ret
    except Exception as e:
        logging.exception(e)
        return None


def to_crc_address(address):
    return web3.toChecksumAddress(address)


def sign_tx(sender_address, tx, password):
    sender_address = web3.toChecksumAddress(sender_address)

    files = glob.glob(r'{}/keystore/*--{}'.format(config.Ethereum['internal']['path'], sender_address.lower()[2:]))
    if len(files) > 0:
        with open(files[0]) as key_file:
            try:
                signed = web3.eth.account.signTransaction(tx, web3.eth.account.decrypt(key_file.read(), password))
            except Exception as e:
                raise ErrException(ERROR.E40000, extra='sign failed, %s' % e)
            return {
                'rawTransaction': signed.rawTransaction.hex(),
                'tx': tx
            }
    else:
        raise ErrException(ERROR.E40000, extra='not found the from address')


def sign_msg(sender_address, msg, password):
    sender_address = web3.toChecksumAddress(sender_address)

    msg_hash = defunct_hash_message(text=msg)

    files = glob.glob(r'{}/keystore/*--{}'.format(config.Ethereum['internal']['path'], sender_address.lower()[2:]))
    if len(files) > 0:
        with open(files[0]) as key_file:
            try:
                signed = web3.eth.account.signHash(msg_hash, web3.eth.account.decrypt(key_file.read(), password))
            except ValueError:
                raise ErrException(ERROR.E40000, extra='sign failed, address and password not match')

            return {
                'rawMessage': signed.messageHash.hex(),
                'message_hash': msg_hash
            }
    else:
        raise ErrException(ERROR.E40000, extra='not found the from address')


async def check_pwd(sender_address, password):
    check_pwd_sync(sender_address, password)


def check_pwd_sync(sender_address, password):
    sender_address = web3.toChecksumAddress(sender_address)

    files = glob.glob(r'{}/keystore/*--{}'.format(config.Ethereum['internal']['path'], sender_address.lower()[2:]))
    if len(files) > 0:
        with open(files[0]) as key_file:
            try:
                web3.eth.account.decrypt(key_file.read(), password)
            except ValueError:
                raise ErrException(ERROR.E40000, extra='sign failed, address and password not match')
    else:
        raise ErrException(ERROR.E40000, extra='not found the from address')