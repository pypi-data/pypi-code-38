from lightfly.http import Client
from lightfly.stock import Stock
from pandas.core.frame import DataFrame
import os


app_id = os.environ['LIGHTFLY_APP_ID']
secret_key = os.environ['LIGHTFLY_SECRET_KEY']

http = Client(app_id, secret_key)
stock = Stock(http)


def test_hs300():
    data = stock.hs300()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_daily_history():
    data = stock.daily_history('sz002142', '2019-05-01', '2019-06-01')
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_stock_realtime():
    data = stock.stock_realtime('sz002142')
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_hgs_trade_realtime():
    data = stock.hgs_trade_realtime()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_hgtong_top10():
    data = stock.hgtong_top10()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_sgtong_top10():
    data = stock.sgtong_top10()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_ggtong_top10():
    data = stock.ggtong_top10()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_stock_index():
    data = stock.stock_index()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_sh_index_component():
    data = stock.sh_index_component()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_sh_consumption_index_component():
    data = stock.sh_consumption_index_component()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_sh50_index_component():
    data = stock.sh50_index_component()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_sh_medicine_index_component():
    data = stock.sh_medicine_index_component()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_sz_index_component():
    data = stock.sz_index_component()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_sz_composite_index_component():
    data = stock.sz_composite_index_component()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_zz500_index_component():
    data = stock.zz500_index_component()
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_indicator_main():
    data = stock.indicator_main('002142')
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_profitability():
    data = stock.profitability('002142')
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_solvency():
    data = stock.solvency('002142')
    assert DataFrame == type(data)
    assert len(data.index) > 0


def test_growth_ability():
    data = stock.growth_ability('002142')
    assert DataFrame == type(data)
    assert len(data.index) > 0













