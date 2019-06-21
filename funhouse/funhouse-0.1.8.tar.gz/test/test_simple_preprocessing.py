import time
from datetime import datetime

from funtime import Store, Converter
from funpicker import Query, QueryTypes
from funhouse import TA, index_time

store = Store().create_lib("raw.Price").get_store()
fpq = Query()
btc_data = None
def test_download_btc_data():
    btc_data = fpq.set_period("day").get()
    assert btc_data is not None
    assert len(btc_data) > 0



def test_save_btc_data():
    btc_data = fpq.set_period("day").get()
    for btc in btc_data:
        # 'close': 6478.19, 'high': 6481.47, 'low': 6470.42, 'open': 6471.04, 'volumefrom': 96.06, 'volumeto': 624696.86
        store['raw.Price'].store({
            "type": "price",
            "crypto": "BTC",
            "fiat": "USD",
            "timestamp": float(btc['time']),
            "high": btc['high'],
            "low": btc['low'],
            "open": btc['open'],
            "close": btc['close'],
            "volume": btc['volumeto'],
            "exchange": "CCCAGG",
            "period": "day"
    
        })
    pass

def test_query_btc_data():
    latest = store['raw.Price'].query_time(time_type="before", start=time.time(), query_type="price")
    assert latest is not None
    assert len(list(latest)) != 0

def test_get_preprocessed():
    latest = store['raw.Price'].query_latest({"type": "price", "limit":100, "exchange": "CCCAGG", "period": "minute"})
    late_len = len(list(latest))
    assert late_len != 0
    assert late_len == late_len

    # ldf = Converter.to_dataframe(latest)
    # assert ldf == None
# def test_convert_to_dict():
#     pass

def test_store_preprocessed():
    pass


# test_save_btc_data()
# test_query_btc_data()
# test_get_preprocessed()
latest = store['raw.Price'].query_latest({"type": "price", "limit":500, "exchange": "CCCAGG", "period": "day"})
ldf = Converter.to_dataframe(latest)
print(ldf)
dftimestamp = ldf['timestamp']
dfdate = dftimestamp.apply(lambda x: datetime.utcfromtimestamp(x))
ldf['date'] = dfdate
ldf.set_index('date', inplace=True)
# print(ldf)
ta = TA(ldf).SMA().SMA(100).SMA(250).FIBBB()
print(ta.main.tail(12))
# print(ta.fib)


# print(ldf.resample('3T').mean())