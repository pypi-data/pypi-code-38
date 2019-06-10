def ratios(symbol = 0, write_pickle = False, read_pickle = False):

    '''
    Gathers all ratios (statistics) data from Yahoo Finance for the selected companies,
    defined by symbol, formats the data extensively and places it in a DataFrame.
        
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
    ratios        : DataFrame
                    All obtained ratios data from the selected symbols.
    '''
    
    import lxml
    from lxml import html
    import requests
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import pickle
    pd.options.mode.chained_assignment = None
    
    if read_pickle == True:
        ratios = pd.read_pickle('ratios')
        return ratios
    
    else:
        ratios = {}
        dummy = 0

        if symbol == 0:
            page = requests.get('https://finance.yahoo.com/trending-tickers')
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')
            symbol = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0]['Symbol'].to_list()
            print('No input is given thus using the Trending Tickers from Yahoo Finance: https://finance.yahoo.com/trending-tickers')

    if type(symbol) == list:
        for s in symbol:
            ratios_url = 'https://finance.yahoo.com/quote/' + s + '/key-statistics?p=' + s

            data = {}

            page = requests.get(ratios_url)
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')

            for i in range(0,len(table)-1,1):
                data[i] = pd.read_html(lxml.etree.tostring(table[i], method='html'))[0]

            for d in range(1,len(table)-1,1):
                data[0] = data[0].append(data[d])

            data = data[0].set_index(0)
            data = pd.DataFrame(data[1].fillna(0))

            if 'Volume' in data.T.columns:
                print('Other entity than a company detected therefore not adding ratios for: ' + s)

            else:
                ratios[s] = data[1]
    
    else:
        ratios_url = 'https://finance.yahoo.com/quote/' + symbol + '/key-statistics?p=' + symbol

        data = {}

        page = requests.get(ratios_url)
        tree = html.fromstring(page.content)
        table = tree.xpath('//table')

        for i in range(0,len(table)-1,1):
            data[i] = pd.read_html(lxml.etree.tostring(table[i], method='html'))[0]

        for d in range(1,len(table)-1,1):
            data[0] = data[0].append(data[d])

        data = data[0].set_index(0)
        data = pd.DataFrame(data[1].fillna(0))

        if 'Volume' in data.T.columns:
            print('Other entity than a company detected therefore not adding ratios for: ' + s)

        else:
            ratios[symbol] = data[1]        

    try:
        ratios = pd.DataFrame(ratios).fillna(0)

    except ValueError as e:
        print('Could not convert to a DataFrame due to: ', e)
        
    for x in ratios.columns:
        for i in range(0,len(ratios)):
            if 'M' in str(ratios[x][i]):
                try:
                    ratios[x][i] = float(ratios[x][i].replace('M', '')) * 1000000

                except:
                    continue

            elif 'B' in str(ratios[x][i]):
                try:
                    ratios[x][i] = float(ratios[x][i].replace('B', '')) * 1000000000

                except:
                    continue

            elif '%' in str(ratios[x][i]):
                try:
                    ratios[x][i] = float(ratios[x][i].replace('%', '')) / 100

                except:
                    continue

            else:
                try:
                    ratios[x][i] = float(ratios[x][i])

                except:
                    continue
    
    if write_pickle == True:
        ratios.to_pickle('ratios')

    return ratios