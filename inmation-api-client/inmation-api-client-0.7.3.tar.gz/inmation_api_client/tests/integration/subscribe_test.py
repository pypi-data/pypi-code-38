import asyncio
import functools
import time
from random import randint

from .environment import ITEM4, ITEM5, create_api_client
from inmation_api_client.model import Item, SubscriptionType

items = [
    Item(ITEM4), Item(ITEM5)
]

io_loop = asyncio.get_event_loop()
client = create_api_client(io_loop)
client.DEBUG_LOG = True


def on_data_changed(*args):
    err = args[0]
    if err:
        print(err.message)
    else:
        _items = args[1]
        if isinstance(_items, list):
            for item in _items:
                item_val = item['v'] if 'v' in item else 'No Value'
                print("{} - {}".format(item['p'], item_val))


async def subscribe_to_data_changes():
    def s_cbk(*args):
        """Subscribe to data changes callback"""
        err = args[0]
        if err:
            print(err.message)
            return
        else:
            if args[1]:
                print('Successful subscription.')

    await client.SubscribeAsync(items, SubscriptionType.DataChanged, s_cbk)


async def unsubscribe_from_data_changes():
    await asyncio.sleep(3)
    await client.UnsubscribeAsync(items[0], SubscriptionType.DataChanged)
    await asyncio.sleep(8)
    await client.UnsubscribeAsync(items[1:], SubscriptionType.DataChanged)


def subscribe_test():
    client.OnDataChanged(on_data_changed)

    print('\n*** START subscribe_test\n')
    client.RunAsync([
        subscribe_to_data_changes(),
        unsubscribe_from_data_changes(),
    ])
    print('\n*** END subscribe_test\n')
