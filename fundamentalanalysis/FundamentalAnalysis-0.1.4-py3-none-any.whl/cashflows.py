def cashflows(symbol = 0, write_pickle = False, read_pickle = False):
    
    '''
    Gathers all cashflows data from Yahoo Finance for the selected companies,
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
    cashflows     : DataFrame
                    All obtained cashflows data from the selected symbols.
    '''
    
    import lxml
    from lxml import html
    import requests
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import pickle
    
    if read_pickle == True:
        cashflows = pd.read_pickle('cashflows')
        return cashflows
    
    else:
        cashflows = {}
        dummy = 0

        if symbol == 0:
            page = requests.get('https://finance.yahoo.com/trending-tickers')
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')
            symbol = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0]['Symbol'].to_list()
            print('No input is given thus using the Trending Tickers from Yahoo Finance: https://finance.yahoo.com/trending-tickers')
    
    if type(symbol) == list:
        for s in symbol:
            cashflows_url = 'https://finance.yahoo.com/quote/' + s + '/cash-flow?p=' + s
            
            page = requests.get(cashflows_url)
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
                    cashflows[s, c] = data[c]
        
    else:
        cashflows_url = 'https://finance.yahoo.com/quote/' + symbol + '/cash-flow?p=' + symbol

        page = requests.get(cashflows_url)
        tree = html.fromstring(page.content)
        table = tree.xpath('//table')
        data = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0].set_index(0).transpose()

        if len(data) == 0:
            print('Not data available for' + symbol)

        if 'Volume' in data.columns:
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
                cashflows[symbol, c] = data[c]

    try:
        cashflows = pd.DataFrame(cashflows).set_index([dates])
        cashflows = cashflows.replace('-','0').astype(float).fillna(0)
        cashflows = cashflows.sort_index()
        
        if write_pickle == True:
            cashflows.to_pickle('cashflows')

    except ValueError as e:
        print('Could not convert to a DataFrame due to: ', e)

    return cashflows