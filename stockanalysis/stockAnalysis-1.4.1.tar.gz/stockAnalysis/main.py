
'''
Auhtor : Sadik Erisen
Version : 1.3
'''

import os, time, datetime, json ,six
from typing import Callable, List, Any

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


ENDPOINTS = ["https://query1.finance.yahoo.com/v8/finance/chart/"]


class AbstractComsumer(object):
    class handleError(Exception):
        pass
    
    def __init__(self):
        self.dataframe = None
 
    def fetch(self, url): 
        FLAG = False
        counter = 0
        raw = None

        while not FLAG:
            try:
                raw =  requests.get(url)
                FLAG = True
            except (requests.HTTPError, requests.ConnectionError) as e:
                if counter < 3:
                   counter += 1
                   waitfor = 5 ** counter
                   time.sleep(waitfor)
                else:
                    raise (e)
        return  raw         

    def HandleDate(self,  d: []) -> None:
        return [str(datetime.datetime.fromtimestamp(t)) for t in d]

    def write_file(self, data, path='output.json'):
        with open(path, 'w+') as f:
            json.dump(data, f, ensure_ascii=True)


    def read_series(self, path, qs, series=[]):
        with pd.option_context('display.max_rows',99999, 'display.max_columns', 99999):
            with open(path, encoding='utf-8') as data_file:
                data = json.loads(data_file.read())
                for i in range(0,len(data)):
                    series.append(data[i][qs])
            return series


class YahooFinance(AbstractComsumer):

    def __init__(self, symbol:str, duration:str, interval:str)-> str:
        super().__init__()
        self.url = ENDPOINTS[0]
        self.symbol = symbol
        self.duration = duration
        self.interval = interval



    def create_URL(self, query=[]):
        ''' 
        $symbol is the stock ticker symbol, e.g. AAPL for Apple
        $range/duration is the desired range of the query, allowed parameters are [1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max]
        $interval is the desired interval of the quote, e.g. every 5 minutes, allowed parameters are [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3m
        ''' 
        url = ('%s?range=%s&interval=%s' % (self.symbol, self.duration, self.interval))
        query= self.url + url
        return query    

    def reponseContent(self):
        result = self.fetch(self.create_URL())
        data = result.json()
        return data

    def CompanyMetaData(self):
        raw =  self.reponseContent()
        with pd.option_context('display.max_rows', 100, 'display.max_columns', 1100):
            dataFrame = pd.DataFrame(raw)
            data = dataFrame['chart']['result'][0]
        return data

    def CompanyQuotes(self, obj=[]):
        data = self.CompanyMetaData()
        newDate = self.HandleDate(data['timestamp'])
        if not "adjclose" in data['indicators'].keys():
            for i in range(0, len(data['timestamp'])):
                company = {
                        "symbol": data['meta']['symbol'],
                        "date": newDate[i],
                        "high": data['indicators']['quote'][0]['high'][i],
                        "low": data['indicators']['quote'][0]['low'][i],
                        "open": data['indicators']['quote'][0]['open'][i],
                        "close": data['indicators']['quote'][0]['close'][i],
                        "volume": data['indicators']['quote'][0]['volume'][i],
                }  
                obj.append(company)
        else :
            for i in range(0, len(data['timestamp'])):
                company = {
                        "symbol":data['meta']['symbol'],
                        "date":newDate[i],  
                        "high":data['indicators']['quote'][0]['high'][i],
                        "low":data['indicators']['quote'][0]['low'][i],
                        "open":data['indicators']['quote'][0]['open'][i],
                        "close":data['indicators']['quote'][0]['close'][i],
                        "volume":data['indicators']['quote'][0]['volume'][i],
                        "adj":data['indicators']['adjclose'][0]['adjclose'][i]
                }
                obj.append(company)
        return obj
                
    def writeOutput(self):
        data = self.CompanyQuotes()
        return self.write_file(data)

    def readOutput(self, path, qs):
        return self.read_series(path, qs)  

    def sma(self, data, window):
        weight = np.repeat(1.0, window) / window
        avg = np.convolve(data, weight, mode='valid')
        return avg

    def ema(self, data, window):
        weight = np.exp(np.linspace(-1.0 , 0.0 , window))
        weight /= weight.sum()
        avg = np.convolve(data, weight, mode='full')[:len(data)]
        avg[:window] = avg[window]
        return avg

    def discreteDiff(self, obj: List[float]) -> List[float]:
        series = pd.Series(obj)
        return series.diff(periods=14).dropna()


    #reading data function, is just method that calucates the mean of the data and returns the value. Thought we need to manually pass the datafile.


    def RSI(self, data , period):
        ema_res = self.ema(data, period)
        deltas = np.diff(ema_res)
        newArry = deltas[:period + 1]
        up = newArry[newArry >= 0].sum()/period
        down = -newArry[newArry < 0].sum() / period
        relativeStrenght = up/down
        rsi = np.zeros_like(ema_res)
        rsi[:period] = 100. - 100. / (1. + relativeStrenght)
        for i in range(period, len(ema_res)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            up = (up*(period-1) + upval)/period
            down = (down*(period-1) + downval)/period
            rs = up//down
            rsi[i] = 100. - 100./(1.+rs)
        return rsi


    def macd(self, data, slow, fast):
        emaFast = self.ema(data, fast)
        emaSlow = self.ema(data, slow)
        # print(emaFast, emaSlow, emaFast - emaSlow)
        return emaFast, emaSlow, emaFast - emaSlow

    

'''Create an instance of yahoo finance class and pass the parameters as string '''
yf = YahooFinance('AAPL', '6mo', '1d')

'''Gets all the prices within given time frame'''
get_quotes = yf.CompanyQuotes()

'''Populates the output data as a json file '''
write_data = yf.writeOutput()

'''Reads from the output file. Takes only two parameter Path and Data Series 
   Parameter string should be [High, Low, Open , Close] '''
r_data = yf.readOutput('output.json', 'close')

'''SMA and EMA methods takes two parameters first param is Data and second is the time frame. '''
get_sma = yf.sma(r_data, 14)
get_ema = yf.ema(r_data, 14)
'''RSI method takes two parameters first param is Data and second is the time frame. '''
get_rsi = yf.RSI(r_data, 14)
'''MACD method takes three parameters first param is Data, second is the slows  and third one is the fast'''
get_macd = yf.macd(r_data, 25, 14)












 
