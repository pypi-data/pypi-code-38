
import pandas as pd
from datetime import datetime
import requests

class HiddenAlphabet(object):
    
    
    def __init__(self, ticker, pandas=False):
        """
        hiddenAlphabet API connection object
        takes in a list of stock tickers as well as the timeframe.
        """
        self.ticker = ticker

        
        # as of now both start and enddates are pandas timestamped times.
        #self.start = pd.to_datetime(start)
        #self.end = pd.to_datetime(end)
        
        # where it says time_series is where we send it to your api.
        # i think we should be returning a timestamp and a sentiment score
        # all manipulation of the data will be done here.
        
        self.rawSentimentData =  requests.post(url='https://intense-bastion-55085.herokuapp.com/api', data=json.dumps({'query': ticker})).json()
        self.sentiment_time_series = pd.DataFrame(self.rawSentimentData).to_dict()
        self.tickerTimeSeries = None
        self.pandas = pandas

    
    def pandas_check_return(self):
        if self.pandas:
            return pd.DataFrame(self.sentimentTimeSeries)
        else:
            return self.sentimentTimeSeries
    
    
    def getSentiment(self, text):
        """
        Label a text document or a series of text documents. 
        """
        if type(text) == list:
            text = text
            requests.post('https://intense-bastion-55085.herokuapp.com/calculate', data=json.dumps({"text": {str(text)}))
        elif type(text) == str:
            text = text
            requests.post('https://intense-bastion-55085.herokuapp.com/calculate', data=json.dumps({"text": {str(list(text)))}))
        else:
            return 'text needs to be a string or a list'
    
    def removeNulls(self):
        """
        Removes scores for text that got a score of 0.
        """

        self.sentimentTimeSeries = df[df.sentiment_score != 0].to_dict()

        return self.pandas_check_return

    def aggregateData(self, aggregate_by='day'):
        """
        Aggregating scores by the day
        """
        try:
            df = pd.DataFrame(self.sentimentTimeSeries)
            df = df.groupby(pd.to_datetime(df.time).dt.date).mean()
            self.sentimentTimeSeries = df.to_dict()

            return self.pandas_check_return()
        else:
            return "Apologies - more aggregation support coming soon."


    def sentiment_volatility(self, data, periods, min_periods=1):
        """
        gets the volatility of the sentiment score.
        periods is the number of periods to use in the volatility calculation.
        """
        
        df = self.to_pandas()
        
        df['rolling_mean_sentiment'] = df.sentiment_score.rolling(window=periods, min_periods=1).mean()
        df['5day_vol'] = (((df['rolling_mean_sentiment'] - df.sentiment_score) ** 2)
                          .rolling(window=periods, min_periods=1).sum() / periods)**(1/2)
        self.sentimentTimeSeries = df.drop(columns=['rolling_mean_sentiment']).to_dict()
        return self.pandas_check_return()
    
    
    def stockTimeseries(self, ticker=self.ticker):
        """
        Stock timeSeries
        """

        r = requests.post(url, json.dumps({'symbol': str(ticker)})).json()

        if self.pandas:
            self.tickerTimeSeries = pd.DataFrame(r)
            return self.tickerTimeSeries
        else:
            self.tickerTimeSeries = r
            return self.tickerTimeSeries

    def historicalVolatility(self, data, periods, min_periods=1):
        """
        gets the volatility of the stock score.
        periods is the number of periods to use in the volatility calculation.
        data should be structured such that theres a time index and a price index
        """
        df = pd.DataFrame(self.data)
        df['rolling_mean'] = df.price.rolling(window=periods, min_periods=1).mean()
        df[str(periods) + 'dayVolatility'] = (((df['rolling_mean'] - df.price) ** 2)
                          .rolling(window=periods, min_periods=1).sum() / periods)**(1/2)
        
        if self.pandas:
            return df[str(periods) + 'dayVolatility']
        else:
            return df[str(periods) + 'dayVolatility'].to_dict()