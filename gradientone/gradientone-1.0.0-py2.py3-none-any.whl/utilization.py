import base
import datetime
import json
import requests

import settings

URL = settings.BASE_URL + '/utilization'
TESTRIG_ID = settings.GATEWAY_ID
HEADERS = base.get_headers()
DT_FORMAT = settings.DATETIME_FORMAT


def record_start(testrig_id=TESTRIG_ID):
    # create the data for recording start
    dt_now = datetime.datetime.now()
    start_timestamp = datetime.datetime.strftime(dt_now, DT_FORMAT)
    data_for_start = {
        "testrig_id": testrig_id,
        "start": start_timestamp,
    }
    # post data to api to record start time
    try:
        requests.post(URL, data=json.dumps(data_for_start), headers=HEADERS)
    except Exception as e:
        print("Exception in record_start() " + str(e))


def record_end(testrig_id=TESTRIG_ID):
    # create the data for recording end
    dt_now = datetime.datetime.now()
    end_timestamp = datetime.datetime.strftime(dt_now, DT_FORMAT)
    data_for_end = {
        "testrig_id": testrig_id,
        "end": end_timestamp,
    }
    # post data to api to record end time
    try:
        requests.post(URL, data=json.dumps(data_for_end), headers=HEADERS)
    except Exception as e:
        print("Exception in record_start() " + str(e))
