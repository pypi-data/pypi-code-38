def summary(symbol = 0, write_pickle = False, read_pickle = False):
    
    '''
    Gathers all summary data (homepage) from Yahoo Finance for the selected companies,
    defined by symbol, formats the data and places it in a DataFrame.
        
    Parameters
    ----------
    symbol        : string or list
                    Company ticker(s) either displayed as a string for one company or as a list
                    when multiple companies are selected.

    write_pickle  : boolean
                    Default on False. Gives the option to write to pickle.

    read_pickle   : boolean
                    Default on False. Gives the option to read the last created pickle.
        
    Returns
    -------
    summary       : DataFrame
                     All obtained summary data from the selected symbols.
    '''

    import lxml
    from lxml import html
    import requests
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import pickle

    if read_pickle == True:
        summary = pd.read_pickle('summary')
        return summary

    else:
        summary = {}
        dummy = 0
    
        if symbol == 0:
            page = requests.get('https://finance.yahoo.com/trending-tickers')
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')
            symbol = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0]['Symbol'].to_list()
            print('No input is given thus using the Trending Tickers from Yahoo Finance: https://finance.yahoo.com/trending-tickers')

    if type(symbol) == list:
        for s in symbol:
            summary_url = 'https://finance.yahoo.com/quote/' + s + '?p=' + s

            data = {}

            page = requests.get(summary_url)
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')

            data[0] = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0]
            data[1] = pd.read_html(lxml.etree.tostring(table[1], method='html'))[0]

            data[0] = data[0].append(data[1])

            data = data[0].set_index(0)
            data = pd.DataFrame(data[1].fillna(0))

            summary[s] = data[1]
                
    else:
            summary_url = 'https://finance.yahoo.com/quote/' + symbol + '?p=' + symbol

            data = {}

            page = requests.get(summary_url)
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')

            data[0] = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0]
            data[1] = pd.read_html(lxml.etree.tostring(table[1], method='html'))[0]

            data[0] = data[0].append(data[1])

            data = data[0].set_index(0)
            data = pd.DataFrame(data[1].fillna(0))

            summary[symbol] = data[1]
        
    summary = pd.DataFrame(summary).fillna(0)
    
    for x in summary.columns:
        for i in range(0,len(summary)):
            if 'M' in str(summary[x][i]):
                try:
                    summary[x][i] = float(summary[x][i].replace('M', '')) * 1000000

                except:
                    continue

            elif 'B' in str(summary[x][i]):
                try:
                    summary[x][i] = float(summary[x][i].replace('B', '')) * 1000000000

                except:
                    continue

            elif '%' in str(summary[x][i]):
                try:
                    summary[x][i] = float(summary[x][i].replace('%', '')) / 100

                except:
                    continue

            else:
                try:
                    summary[x][i] = float(summary[x][i])

                except:
                    continue

    if write_pickle == True:
        summary.to_pickle('summary')
    
    return summary