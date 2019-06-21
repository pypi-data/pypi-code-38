import pandas as pd
import numpy as np
import talib as ta
from copy import deepcopy, copy
import weakref

# Idea. Use context to temporarily sort the item
#TODO: Might need to shift to ascending
class TA:
    """
        TA is the class that will convert all of the price information into a technical analysis pandas    
    """
    def __init__(self, origin):
        origin = origin.copy(deep=True)

        if not isinstance(origin, pd.DataFrame):
            raise TypeError("Not a dataframe")
        else:
            col_list = list(origin.columns)
            self.origin = origin
            self.info = {}
            self.info['main'] = pd.DataFrame()
            self.fib = pd.DataFrame()
            
            # Get a list of columns
            # Figure out which ones are most similar to time
            # Pick one
            # Try to get the datetime using for loop until it has either run out of not failed
            # Place the date-time into a variable
            available = []
            time_names = ['date', 'time', 'datetime', 'timestamp']
            
            time_candidate = False

            for tname in time_names:
                if tname in col_list:
                    time_candidate = True
                    available.append(tname)
            if time_candidate is False:
                raise AttributeError("You lack a variable that is specified to time please include: [date, time, datetime, timestamp]")
            time_series = None

            for avail in available:
                try:
                    time_series = pd.to_datetime(origin[avail], unit='s')
                except:
                    pass
            
            if time_series is None:
                raise AttributeError("None of your time items were formatted correctly")
                # time_series = pd.to_datetime(origin['time'], unit='s')
            last_price = origin['close'].iloc[-1]

            if last_price < 0.5:
                # Increase general price to increase the overall significance
                self.origin.loc[:, 'close'] = origin['close'] * 100000.11
                self.origin.loc[:, 'low'] = origin['low'] * 100000.11
                self.origin.loc[:, 'high'] = origin['high'] * 100000.11
                self.origin.loc[:, 'open'] = origin['open'] * 100000.11
            
            self.info['main'].loc[:, 'price'] = origin['close']
            self.info['main'].set_index(time_series, inplace=True)
            # self.info['main'].sort_index()
            self.fib.loc[:, 'price'] = origin['close'].values
            self.fib.set_index(time_series, inplace=True)
            self.fib.loc[:, :] = self.fib.sort_index(ascending=True)
            self.info['main'].loc[:, :] = self.info['main'].sort_index(ascending=True)
            self.origin.loc[:, :] = self.origin.sort_index(ascending=True)
            # self.fib.sort_index()
        del origin

    def reverse(self, l):
        """

        """
        # print(type(l))
        return list(reversed(l))
            
    def SMA(self, window=30):
        temp = self.info['main']
        # .sort_index(ascending=False)
        simple = ta.SMA(temp['price'].values, timeperiod=window)

        # Reverse before placing in
        
        sma_name = "SMA_{}".format(window)
        self.info['main'].loc[:, sma_name] = list(simple)
        return self
    
    def TRIX(self, window=14):
        temp = self.origin
        # .sort_index(ascending=False)
        simple_trix = ta.TRIX(temp.close.values, timeperiod=window)

        # Reverse before placing in
        
        trix_name = "TRIX_{}".format(window)
        aroon_down_name = "TRIX_{}".format(window)
        self.info['main'].loc[:, trix_name] = list(simple_trix)
        # self.info['main'].loc[:, aroon_down_name] = list(aroondown)
        return self
    
    def MACD(self):
        temp = self.origin
        macd, macdsignal, macdhist = ta.MACD(temp.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
        # self.info['main'].loc[:, "MACD"] = list(macd)
        # self.info['main'].loc[:, "MACDSIGNAL"] = list(macdsignal)
        self.info['main'].loc[:, "MACDHIST"] = list(macdhist)
        return self


    
    def LSTAT(self, window=5):
        """ A list of statistical functions that give relavant information such as trend"""
        temp = self.origin
        # .sort_index(ascending=False)
        aroondown, aroonup = ta.AROON(temp.close.values, temp.low.values, timeperiod=window)

        # Reverse before placing in
        
        aroon_up_name = "AROON_{}_UP".format(window)
        aroon_down_name = "AROON_{}_DOWN".format(window)
        self.info['main'].loc[:, aroon_up_name] = list(aroonup)
        self.info['main'].loc[:, aroon_down_name] = list(aroondown)
        return self

    def RSI(self, window=14):
        try:
            self.rsi_count += 1
        except Exception:
            self.rsi_count = 0

        temp = self.info['main']
        # .sort_index(ascending=False)
        pp = temp['price'].values
        # print(pp)
        rsi_simple = ta.RSI(pp, timeperiod=window)
        rsi_name = "RSI_{}".format(window)
        self.info['main'].loc[:, rsi_name] = list(rsi_simple)
        return self
    
    def EMA(self, window=30):
        temp = self.info['main']
        # .sort_index(ascending=False)
        ema_simple = ta.EMA(temp['price'].values, timeperiod=window)
        ema_name = "EMA_{}".format(window)
        self.info['main'].loc[:, ema_name] = list(ema_simple)
        return self
    
    def TripleEMA(self, window=30):
        # real = TEMA(close, timeperiod=30)
        try:
            self.tema_count += 1
        except Exception:
            self.tema_count = 0
        return self
    
    def BOLL(self, dev=2, window=30):
        temp = self.info['main']
        # .sort_index(ascending=False)
        upper, middle, lower = ta.BBANDS(self.info['main']['price'].values, timeperiod=window, nbdevup=dev)
        boll_name = "BOLL_{0}_{1}".format(dev, window)
        self.info['main'].loc[:, (boll_name+"_UP")] = upper
        self.info['main'].loc[:, (boll_name+"_MID")] = middle
        self.info['main'].loc[:, (boll_name+"_LOW")] = lower
        return self
    
    def ATR(self, window=40):
        temp = self.origin
        # .sort_index(ascending=False)
        atr = ta.ATR(temp['high'].values, temp['low'].values, temp['close'].values,timeperiod=window)
        atr_name = "ATR_{}".format(window)
        self.info['main'].loc[:, atr_name] = atr
        return self
    
    def VolTrans(self, window=40):
        temp = self.origin
        # .sort_index(ascending=False)
        atr = ta.ATR(temp['high'].values, temp['low'].values, temp['close'].values,timeperiod=window)
        voltrans_rsi = ta.RSI(atr)
        
        atr_name = "ATR_{}".format(window)
        self.info['main'].loc[:, atr_name] = atr
        self.info['main'].loc[:, "voltrans_rsi"] = voltrans_rsi
        return self

    
    def FIBBB(self, stdev=2, window=100):
        # Get EMA
        # Get real = STDDEV(close, timeperiod=5, nbdev=1)
        temp = self.origin
        # .sort_index(ascending=False)
        # base = self.origin['base'].iloc[0]

        # print(temp.index.values)
        sti2 = pd.Series(temp['close'].values).rolling(window).std() * 3

        sti = ta.STDDEV(temp['close'].values, timeperiod=window)
        dev = sti * stdev
        basis = ta.EMA(temp['close'].values, timeperiod=window)
        # print(dev)
        upper_1= basis + (0.236*sti2)
        upper_2= basis + (0.382*sti2)
        upper_3= basis + (0.5*sti2)
        upper_4= basis + (0.618*sti2)
        upper_5= basis + (0.764*sti2)
        upper_6= basis + (1*sti2)
        lower_1= basis - (0.236*sti2)
        lower_2= basis - (0.382*sti2)
        lower_3= basis - (0.5*sti2)
        lower_4= basis - (0.618*sti2)
        lower_5= basis - (0.764*sti2)
        lower_6= basis - (1*sti2)
        
        self.fib.loc[:, "price"] = self.origin['close']
        self.fib.loc[:, "up1"] = list(upper_1)  
        self.fib.loc[:, "up2"] = list(upper_2)
        self.fib.loc[:, "up3"] = list(upper_3)
        self.fib.loc[:, "up4"] = list(upper_4)
        self.fib.loc[:, "up5"] = list(upper_5)
        self.fib.loc[:, "up6"] = list(upper_6)
        self.fib.loc[:, "basis"] = list(basis)
        self.fib.loc[:, "low1"] = list(lower_1)
        self.fib.loc[:, "low2"] = list(lower_2)
        self.fib.loc[:, "low3"] = list(lower_3)
        self.fib.loc[:, "low4"] = list(lower_4)
        self.fib.loc[:, "low5"] = list(lower_5)
        self.fib.loc[:, "low6"] = list(lower_6)
        
        # time_series = pd.to_datetime(self.origin['time'], unit='s')
        # fibframe.set_index(time_series, inplace=True)
        self.fib.loc[:, :] = self.fib.dropna()
        # self.fib = fibframe
        return self
    
    def __getattr__(self, name):
        if name in ('main', 'fib'):
            if name == "main":
                del self.origin
                return self.info[name].dropna()
            else:
                return self.fib
    