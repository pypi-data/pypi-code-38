"""
Author  : Jiwoo Park
Date    : 2019. 1. 21
Desc    : Pocket - Balance Record System for Quant
"""
import sys
import pandas as pd
import numpy as np

from record import Record
from datetime import datetime
import util

PRICE_DF = pd.read_csv("./PRICE.csv", index_col=[0], parse_dates=[0])


class Pocket():
    """
    Balance System
    """
    def __init__(self, cash):
        """
        :param cash:    (Int) Amount of Cash in the pocket
        :param cur_stocks:  (Dataframe) of Stocks and its amount in the pocket
                            Which Column has [code, name, amount, purchase_date, purchase_price,
                                             purchase_volume, current_price, current_volume, return]
        """
        self.cash = cash
        columns = ["NAME", "AMOUNT", "DATE_PURCHASE", "PRICE_PURCHASE", "VOLUME_PURCHASE"]
        self.cur_stocks = pd.DataFrame(columns=columns) # cur_stock : code, name, amount, price_purchase, volume_purchase, return,
                                                        # price_current
        self.history = []
        self.logs = False


    def _set_one_stock(self, stock, amount, date):
        # buy or sell unit stock
        target_firm = util.code2firm(stock)
        try:
            price_at_date = PRICE_DF.loc[date]
        except Exception as e:
            print(e)
            raise ValueError("Invalid Date to Order - by KSIF Tech")

        try:
            price_of_firm = price_at_date[stock]
            if not price_of_firm:
                raise ValueError("Ordered Stock doesn't have proper price info.")
        except Exception as e:
            print(e)
            raise ValueError("Ordered Stock is not available to trade. - by KSIF Tech")

        # if stock already in position, how to do it??? --> Where to put cash concept in abstraction.
        if stock not in self.cur_stocks.index:
            self.cur_stocks.loc[stock] = [target_firm["회사명"].values[0], amount, date,
                                          price_of_firm, price_of_firm * amount]
        elif amount == 0:
            self.cur_stocks = self.cur_stocks.drop(stock)

        else:
            self.cur_stocks.at[stock, "AMOUNT"] += amount
            self.cur_stocks.at[stock, "VOLUME_PURCHASE"] += price_of_firm * amount

    def _set_cur_stocks(self, stocks, amount, date):
        if isinstance(stocks, type("")):
            self._set_one_stock(stocks, amount, date)
        elif isinstance(stocks, type({})):
            for stock, amount in stocks.items():
                self._set_one_stock(stock, amount, date)

    def order(self, date, stocks, amount=None):
        # Set cur_stocks and Add new record to history
        success = True
        if not date:
            raise ValueError("Date is Required")

        try:
            new_record = util._pack_record(date, stocks, amount)
            self._set_cur_stocks(stocks, amount, date)
            self.history.append(new_record)
        except Exception as e:
            print("Your Order has been failed because of following reason.")
            success = False
            print(e)

        if self.logs and success:
            print(new_record)

        return success

    def view_history(self):
        for hist in self.history:
            print(hist)

    def evaluate_cur_stocks(self):
        """
        Evaluate current holding stocks at Today and update cur stock attribute
        :return: No return
        """
        today = datetime.today()
        close_val = PRICE_DF.iloc[PRICE_DF.index.get_loc(today, method="ffill")]
        close_val = close_val[self.cur_stocks.index]
        close_val = pd.DataFrame({"PRICE_CURRENT" : close_val.values}, index=self.cur_stocks.index)
        evaluated_stocks = pd.merge(self.cur_stocks, close_val, left_index=True, right_index=True)
        evaluated_stocks["VOLUME_CURRENT"] = evaluated_stocks["AMOUNT"] * evaluated_stocks["PRICE_CURRENT"]
        evaluated_stocks["RETURN"] = (evaluated_stocks["VOLUME_CURRENT"] / evaluated_stocks["VOLUME_PURCHASE"]) - 1
        return evaluated_stocks

    def evaluate_history(self, price_info):
        """
        Make historical change of price for pocket
        :return: Historical DataFrame for holding stocks
        """

        historic_stocks = util.historic_stocks(self)
        historic_df = pd.DataFrame(columns=historic_stocks)

        for record in self.history:
            update_row = util.update_row(historic_df, record)
            historic_df.loc[record.date] = update_row
            print(historic_df)

        start_date = self.history[0].date
        end_date = self.history[-1].date

        price_info = price_info.loc[(price_info.index >= start_date) & (price_info.index <= end_date)][historic_stocks]
        historic_stocks = price_info.merge(historic_df,
                                           how="left", left_index=True, right_index=True,
                                           suffixes=("_price", "_amount"))
        return historic_stocks


    def flush(self):
        """ Make Pocket cur holding stock to empty
        :return:
        """
        self.cur_stocks = self.cur_stocks.drop(self.cur_stocks.index)
        # add history that flushed whole stocks

    def cal_return(self, price_info):
        # pick trades belongs to start ~ end
        # for those trades calculate returns each

        self.evaluate_history(price_info)


    def analyze(self, start, end):
        """ Analyzing the performance of manager's pocket.
        :param start:   (datetime) Datetime starting analyzing date
        :param end:     (datetime) Datetime ending analyzing date
        :return:        (DataFrame) Dataframe that contain summary statistics
        """
        return



def get_update_list(new_portfolio_dict, portfolio_dict):
    enterance_dict = {}
    for stock_code, quantity in new_portfolio_dict.items():
        if stock_code not in portfolio_dict:
            enterance_dict[stock_code] = quantity

    exit_dict = {}
    for stock_code, quantity in portfolio_dict.items():
        if stock_code not in new_portfolio_dict:
            exit_dict[stock_code] = quantity

    update_stock_list = []

    update_portfolio_list = []


if __name__ == "__main__":
    pkt = Pocket(0)
    pkt.logs = False # Activate Logging
    PRICE_DF = pd.read_csv("./PRICE.csv", index_col=[0], parse_dates=[0])

    pkt.order(datetime(2010, 9, 30), "A000030", 3)

    sample_dict = {"A000660": 10, "A000400" : 100}
    pkt.order(datetime(2011, 9, 30), sample_dict)

    sample_dict = {"A000660": 1, "A000400": -10, "A000030" : 0}
    pkt.order(datetime(2012, 9, 28), sample_dict)
    # pkt.cal_return(datetime(2011, 5, 8), datetime(2013, 10, 20))
    pkt.cal_return(PRICE_DF)

