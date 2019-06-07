import pandas as pd
import numpy as np
from record import *
from copy import deepcopy

CODE_DF = pd.DataFrame(pd.read_html("./firm_code.xls")[0])
CODE_DF = CODE_DF.rename(columns=CODE_DF.iloc[0])[1:]

def code2firm(code):
    code = code[1:]
    return CODE_DF.loc[CODE_DF["종목코드"] == code]


def _pack_record(date, stocks, amount):
    if amount:
        return Record(date, [(stocks, code2firm(stocks)["회사명"], amount)])
    else:
        return Record(date, [(stock, code2firm(stock)["회사명"], amount) for stock, amount in stocks.items()])

def historic_stocks(pocket):
    historic_stocks = []
    for record in pocket.history:
        historic_stocks.extend([stock_code for stock_code, _, _ in record.assets])

    historic_stocks = list(set(historic_stocks))
    return historic_stocks

def update_row(historic_df, record):
    if not historic_df.index.empty:
        latest = deepcopy(pd.Series(data=historic_df.iloc[-1].values, index=historic_df.columns))
        for stock_code, _, amount in record.assets:
            latest[stock_code] += amount

        return latest.rename(None)

    else:
        result = pd.Series(index = historic_df.columns)
        for stock_code, _, amount in record.assets:
            result[stock_code] = amount
        return result.fillna(0)





