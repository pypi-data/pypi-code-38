import asyncio
import functools
import json
import time

from .environment import ITEM1, ITEM2, ITEM3, create_api_client, print_info
from inmation_api_client.model import Item


def duration_test(client):
    max_reads = 10
    duration_list = []
    script = "return {inmation.getcorepath(), inmation.gettime(inmation.currenttime())}"
    context = Item('/System/Core')

    for _ in range(max_reads):
        start_time = time.perf_counter()
        client.RunScript(context, script)
        duration_list.append(time.perf_counter() - start_time)

    dr_len = len(duration_list)
    avg_duration = functools.reduce(lambda x, y: x + y, duration_list) / dr_len
    print("Average run script duration: {:.3f} ms for {} runs".format(avg_duration * 1000, dr_len))


def perf_test(client):
    max_reads = 1000
    duration_list = []
    script = "return {inmation.getcorepath(), inmation.gettime(inmation.currenttime())}"
    context = Item('/System/Core')

    for _ in range(max_reads):
        start_time = time.perf_counter()
        client.RunScript(context, script)
        duration_list.append(time.perf_counter() - start_time)

    dr_len = len(duration_list)
    avg_duration = functools.reduce(lambda x, y: x + y, duration_list) / dr_len
    print("Average run script duration: {:.3f} ms for {} runs\n".format(avg_duration * 1000, dr_len))


@print_info
def runscript_test():
    client = create_api_client()
    print("Duration test ...")
    duration_test(client)

    time.sleep(1)

    print("\nPeformance test ...")
    perf_test(client)
