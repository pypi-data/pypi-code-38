from datetime import datetime, timedelta
import functools

from .environment import ITEM1, ITEM2, ITEM3, create_api_client, print_info
from inmation_api_client.model import Item


@print_info
def execfunction_readhist_test():
    client = create_api_client()
    date_format = '%Y-%m-%dT%H:%M:%S.000Z'

    now = datetime.now()
    now_minus_month = now + timedelta(-30)
    start_time = now_minus_month.strftime(date_format)
    end_time = now.strftime(date_format)

    context = Item('/System/Core/APIContext/WebAPI01')
    farg = {
        "paths": [ITEM1],
        "startTime": start_time,
        "endTime": end_time,
        "aggregates": ['AGG_TYPE_INTERPOLATIVE'],
        "intervals": 10
    }

    client.ExecuteFunction(context, 'histdata-fetcher', 'fetch', farg)
