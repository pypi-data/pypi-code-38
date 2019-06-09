def income_statement(symbol = 0, write_pickle = False, read_pickle = False):
    
    '''
    Gathers all income statement data from Yahoo Finance for the selected companies,
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
    income_statement  : DataFrame
                        All obtained income statement data from the selected symbols.
    '''
    
    import lxml
    from lxml import html
    import requests
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import pickle
    
    if read_pickle == True:
        income_statement = pd.read_pickle('income_statement')
        return income_statement
    
    else:
        income_statement = {}
        dummy = 0

        if symbol == 0:
            page = requests.get('https://finance.yahoo.com/trending-tickers')
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')
            symbol = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0]['Symbol'].to_list()
            print('No input is given thus using the Trending Tickers from Yahoo Finance: https://finance.yahoo.com/trending-tickers')
        
    if type(symbol) == list:
        for s in symbol:
            income_statement_url = 'https://finance.yahoo.com/quote/' + s + '/income_statement?p=' + s

            page = requests.get(income_statement_url)
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
                            index = data['Revenue']
                            data = data.drop('Revenue', axis = 1)
                            dummy = 1
                            dates = []

                            for y in index:
                                dates.append(y[-4:])   
                        else:
                            data = data.drop(d, axis=1)

                for c in data.columns:
                    income_statement[s, c] = data[c]
                    
    else:
        income_statement_url = 'https://finance.yahoo.com/quote/' + symbol + '/income_statement?p=' + symbol

        page = requests.get(income_statement_url)
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
                        index = data['Revenue']
                        data = data.drop('Revenue', axis = 1)
                        dummy = 1
                        dates = []

                        for y in index:
                            dates.append(y[-4:])   
                    else:
                        data = data.drop(d, axis=1)

            for c in data.columns:
                income_statement[symbol, c] = data[c]

    try:
        income_statement = pd.DataFrame(income_statement).set_index([dates])
        income_statement = income_statement.replace('-','0').astype(float).fillna(0)
        income_statement = income_statement.sort_index()
        
        if write_pickle == True:
            income_statement.to_pickle('income_statement')

    except ValueError as e:
        print('Could not convert to a DataFrame due to: ', e)

    return income_statement