import asyncio
import functools
import json
import time

from .environment import create_api_client, print_info
from inmation_api_client.model import Item


@print_info
def execfunction_test():
    context = Item('/System/Core/APIContext/WebAPI01')
    start_time = time.perf_counter()

    client = create_api_client()
    data = client.ExecuteFunction(context, 'testlib', 'test', {'name': 'test'})

    duration = time.perf_counter() - start_time
    print("Result in {:.3f} ms: {}".format(duration * 1000, json.dumps(data)))
