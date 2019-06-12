import time
import functools

from .environment import ITEM1, ITEM2, ITEM3, create_api_client, print_info
from inmation_api_client.model import Item


@print_info
def read_test():
    client = create_api_client()
    items = [
        Item(ITEM1), Item(ITEM2), Item(ITEM3)
    ]

    duration_list = []
    max_reads = 100

    for _ in range(max_reads):
        start_time = time.perf_counter()
        client.Read(items)
        duration_list.append(time.perf_counter() - start_time)

    dl_len = len(duration_list)
    avg_duration = functools.reduce(lambda x, y: x + y, duration_list) / dl_len
    print("Average duration: {:.3f} ms for {} reads".format(avg_duration * 1000, dl_len))
