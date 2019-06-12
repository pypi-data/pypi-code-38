from datetime import datetime, timedelta

from .environment import ITEM1, ITEM2, create_api_client, print_info
from inmation_api_client.model import HistoricalDataItem


@print_info
def readhistoricaldata_test():
    client = create_api_client()

    now = datetime.now()
    now_minus_month = now + timedelta(-30)
    date_format = '%Y-%m-%dT%H:%M:%S.000Z'

    start_time = now_minus_month.strftime(date_format)
    end_time = now.strftime(date_format)

    hdi1 = HistoricalDataItem(ITEM1, "AGG_TYPE_RAW")
    hdi2 = HistoricalDataItem(ITEM2, "AGG_TYPE_RAW")

    num_intervals = 1
    max_req = 3

    for i in range(max_req):
        print("Number of outstanding req {} of total {}".format(i + 1, max_req))
        client.ReadHistoricalData([hdi1, hdi2], start_time, end_time, num_intervals)
