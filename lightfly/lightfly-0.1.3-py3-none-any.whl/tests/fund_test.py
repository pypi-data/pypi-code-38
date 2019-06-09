from lightfly.http import Client
from lightfly.fund import Fund
from pandas.core.frame import DataFrame
import os


app_id = os.environ['LIGHTFLY_APP_ID']
secret_key = os.environ['LIGHTFLY_SECRET_KEY']

http = Client(app_id, secret_key)
fund = Fund(http)


def test_daily_history():
    data = fund.daily_history('110022', '2019-01-01', '2019-06-01')
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_internet_banking():
    data = fund.internet_banking()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_basic_info():
    data = fund.basic_info('110022')
    assert list == type(data)
    assert len(data) > 0
