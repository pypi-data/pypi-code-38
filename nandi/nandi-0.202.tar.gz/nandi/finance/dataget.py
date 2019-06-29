# Module to import data from STOCK market
# Refer to this webpage for more details
#       http://theautomatic.net/yahoo_fin-documentation/#get_data
#
#
#### Credit to :
#         Yahoo_fin is a Python 3 package I wrote to scrape historical stock price data, as well as
#           to provide current information on market caps, dividend yields, and which stocks comprise
#           the major exchanges. Additional functionality includes scraping income statements, balance
#           sheets, cash flows, holder information, and analyst data. The package includes the ability to
#           get live stock prices, capture cryptocurrency data, and get the most actively traded stocks
#           on a current trading day
#
# sudo /Applications/Python\ 3.6/Install\ Certificates.command
# Packeges required are:
#       yahoo_fin : pip install yahoo_fin
#                       pip install yahoo_fin --upgrade if you have installed a older version
#


# All the routines are currently supported through yahoo-fin
from yahoo_fin.stock_info import *
import datetime

#Now this is in git

def get_data (ticker, start_date = None, end_date = None, index_as_date = True):
    """
        ticker
            Stock ticker (e.g. 'MSFT', 'AMZN', etc.).  Case insensitive. Only ONE TICKER This is the only required argument.
        start_date
            The date the price history should begin.
        end_date
            The date the price history should end.
        index_as_date
            Default is True.  If index_as_date = True, then the index of the returned data i
            frame is the date associated with each record.  
            Otherwise, the date is returned as its own column.

        returns
            Price history in a dataframe
                                  open        high         low       close    adjclose    volume ticker
            date                                                                                   
        2019-06-03  123.849998  124.370003  119.010002  119.839996  119.839996  37983600   MSFT
        2019-06-04  121.279999  123.279999  120.650002  123.160004  123.160004  29382600   MSFT
        2019-06-05  124.949997  125.870003  124.209999  125.830002  125.830002  24926100   MSFT
    """
    return get_data(ticker, start_date = start_date, end_date = end_date, index_as_date = index_as_date)


def get_live_price (ticker):
    """
        ticker : a Single ticker
        returns : current price (or last price)
                i.e 352.010009765625
    """
    return get_live_price(ticker)

def get_quote_table(ticker , dict_result = False):
    """
        ticker : a single ticker
        dict_results : Default is False.  If True, the function returns the results in a dict format.
                    Otherwise, the results are returned in a data frame.

        returns :
                                                                       value
                    attribute                                            
                1y Target Est                                  143.16
                52 Week Range                          93.96 - 134.24
                Ask                                     131.62 x 1400
                Avg. Volume                               2.51255e+07
                Beta (3Y Monthly)                                1.05
                Bid                                      131.60 x 800
                Day's Range                           131.38 - 134.24
                EPS (TTM)                                         4.5
                Earnings Date             Jul 17, 2019 - Jul 22, 2019
                Ex-Dividend Date                           2019-05-15
                Forward Dividend & Yield                 1.84 (1.49%)
                Market Cap                                     1.009T
                Open                                           133.88
                PE Ratio (TTM)                                  29.26
                Previous Close                                  132.6
                Quote Price                                    131.68
                Volume                                    1.31666e+07
    """

    table =  get_quote_table (ticker, dict_result = dict_result)
    table.set_index('attribute', inplace=True)
    return table

#    return (get_quote_table(ticker, dict_result = dict_result).set_index('attribute',inplace=True))   
    
if __name__ == "__main__":
    
    nflx = get_live_price('nflx')
    print (nflx)

    tickers = tickers_dow()
    print (tickers)
    
    st_dt =(datetime.datetime.today().strftime('%m/%d/%Y'))
    print (st_dt)
    st_dt = '06/01/2019'
    en_dt = '06/06/2019'
    stock ='MSFT'
    nflx_data = get_data(stock, start_date=  st_dt, end_date = en_dt)
    print (nflx_data.head())

    print (get_quote_table(stock ))
