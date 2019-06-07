
from datetime import datetime as dt
import numpy as np
# import pandas as pd
import pandas_datareader as pdr
from data._util import *
# import multiprocessing
# import os

# ---------- PRICE DATA ----------

# Get price data of the firm
def get_a_price(code, start, end, source='yahoo'):
    try:
        return pdr.DataReader(code, source, start, end)
    except:
        return False


# Get price data for Republic of KOREA, Stock market.
def price_slow(stock_list, start, end=dt.now().strftime('%Y-%m-%d'), source='yahoo'):
    # Suppose that the type of data is 'List'

    # 기업들의 기록 형식을 Yahoo finance API에 적절한 형태로 변환
    if type(stock_list) == str: stock_list = [stock_list]
    data = list(map(lambda stock: code_df['code'][list(np.where(code_df == stock)[0])[0]] + code_df['market'][
        list(np.where(code_df == stock)[0])[0]], stock_list))

    result = pd.DataFrame()
    success_list = []
    fail_list = []
    for index, stock in enumerate(data):
        data = get_a_price(stock, start, end)
        if type(data) != bool:
            success_list.append(stock)
            result = result.append(data.T)
        else:
            fail_list.append(stock)

    result.index = pd.MultiIndex.from_product([success_list, ['high', 'low', 'open', 'close', 'volume', 'adj_close']])

    return result



