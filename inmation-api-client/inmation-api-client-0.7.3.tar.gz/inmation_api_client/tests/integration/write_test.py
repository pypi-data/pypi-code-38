import time
import asyncio
import functools
from random import randint

from .environment import create_api_client, print_info, ITEM1, ITEM2, ITEM3
from inmation_api_client.model import ItemValue


@print_info
def write_test():
    io_loop = asyncio.get_event_loop()
    client = create_api_client(io_loop)

    max_reads = 100
    duration_list = []

    for _ in range(max_reads):
        items = [
            ItemValue(ITEM1, randint(1, 2**10)),
            ItemValue(ITEM2, randint(1, 2**10)),
            ItemValue(ITEM3, randint(1, 2**10)),
        ]
        start_time = time.perf_counter()
        client.Write(items)
        duration_list.append(time.perf_counter() - start_time)

    dr_len = len(duration_list)
    avg_duration = functools.reduce(lambda x, y: x + y, duration_list) / dr_len
    print("Average duration: {:.3f} ms for {} writes".format(avg_duration * 1000, dr_len))
