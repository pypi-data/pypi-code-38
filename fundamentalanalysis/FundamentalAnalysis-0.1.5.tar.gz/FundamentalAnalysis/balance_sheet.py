def balance_sheet(symbol = 0, write_pickle = False, read_pickle = False):

    '''
    Gathers all balance sheet data from Yahoo Finance for the selected companies,
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
    balance_sheet  : DataFrame
                     All obtained balance sheet data from the selected symbols.
    '''

    import lxml
    from lxml import html
    import requests
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import pickle

    if read_pickle == True:
        balance_sheet = pd.read_pickle('balance_sheet')
        return balance_sheet
    
    else:
        balance_sheet = {}
        dummy = 0
    
        if symbol == 0:
            page = requests.get('https://finance.yahoo.com/trending-tickers')
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')
            symbol = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0]['Symbol'].to_list()
            print('No input is given thus using the Trending Tickers from Yahoo Finance: https://finance.yahoo.com/trending-tickers')

    if type(symbol) == list:
        for s in symbol:
            balance_sheet_url = 'https://finance.yahoo.com/quote/' + s + '/balance-sheet?p=' + s

            page = requests.get(balance_sheet_url)
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')
            data = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0].set_index(0).transpose()

            if len(data) == 0:
                continue

            if 'Volume' in data.columns:
                print('Other entity than a company detected therefore not adding data for: ' + s)

            else:
                for d in data.columns.unique():
                    try:
                        data[d].astype('int64')

                    except ValueError:
                        if '-' in data[d].values:
                            continue

                        elif dummy == 0:
                            index = data['Period Ending']
                            data = data.drop('Period Ending', axis = 1)
                            dummy = 1
                            dates = []

                            for y in index:
                                dates.append(y[-4:])   
                        else:
                            data = data.drop(d, axis=1)

                for c in data.columns: 
                    balance_sheet[s, c] = data[c]
        
    else:
        balance_sheet_url = 'https://finance.yahoo.com/quote/' + symbol + '/balance-sheet?p=' + symbol

        page = requests.get(balance_sheet_url)
        tree = html.fromstring(page.content)
        table = tree.xpath('//table')
        data = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0].set_index(0).transpose()

        if len(data) == 0:
            print('Not data available for' + symbol)

        elif 'Volume' in data.columns:
            print('Other entity than a company detected therefore not adding data for: ' + symbol)

        else:
            for d in data.columns.unique():
                try:
                    data[d].astype('int64')

                except ValueError:
                    if '-' in data[d].values:
                        continue

                    elif dummy == 0:
                        index = data['Period Ending']
                        data = data.drop('Period Ending', axis = 1)
                        dummy = 1
                        dates = []

                        for y in index:
                            dates.append(y[-4:])   
                    else:
                        data = data.drop(d, axis=1)

            for c in data.columns: 
                balance_sheet[symbol, c] = data[c]

    try: 
        balance_sheet = pd.DataFrame(balance_sheet).set_index([dates])
        balance_sheet = balance_sheet.replace('-','0').astype(float).fillna(0)
        balance_sheet = balance_sheet.sort_index()
        
        if write_pickle == True:
            balance_sheet.to_pickle('balance_sheet')

    except ValueError as e:
        print('Could not convert to a DataFrame due to: ', e)

    return balance_sheet