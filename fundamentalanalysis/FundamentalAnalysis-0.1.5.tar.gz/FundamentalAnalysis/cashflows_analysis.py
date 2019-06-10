def cashflows_analysis(cashflows, symbol=0, log=False):   

    '''
    Graphically gives an overview of the various cashflows items overtime.
    When selecting multiple symbols, you are able to visually see the difference
    between the companies. 
        
    Parameters
    ----------
    cashflows     : DataFrame
                    The data created with the cashflows() function.
    
    symbol        : string or list
                    Company ticker(s) either displayed as a string for one company or as a list
                    when multiple companies are selected.

    log           : boolean
                    Default on False. Gives the option to convert everything in log values.
        
    Returns
    -------
    The following graphs:
        net income
        total operating actitivies
        total investing activities
        total financing activities
        operating profit
    '''

    import lxml
    from lxml import html
    import requests
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    if symbol == 0:
        page = requests.get('https://finance.yahoo.com/trending-tickers')
        tree = html.fromstring(page.content)
        table = tree.xpath('//table')
        symbol = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0]['Symbol'].to_list()
        print('No input is given thus using the Trending Tickers from Yahoo Finance: https://finance.yahoo.com/trending-tickers')
        
    net_income = pd.DataFrame(index=cashflows.index)
    total_operating_activities = pd.DataFrame(index=cashflows.index)
    total_investing_activities = pd.DataFrame(index=cashflows.index)
    total_financing_activities = pd.DataFrame(index=cashflows.index)
    operating_profit = pd.DataFrame(index=cashflows.index)
            
    if type(symbol) == list:
        if log == True:
            import warnings
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            for x in symbol:
                if x in cashflows:
                    try:
                        net_income[x] = np.log(cashflows[x,'Net Income'])
                        total_operating_activities[x] = np.log(cashflows[x,'Total Cash Flow From Operating Activities'])
                        total_investing_activities[x] = np.log(cashflows[x, 'Total Cash Flows From Investing Activities'])
                        total_financing_activities[x] = np.log(cashflows[x,'Total Cash Flows From Financing Activities'])
                
                    except KeyError:
                        continue
                    

            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
            net_income.plot.bar(ax=axes[0,0], rot=0).set_title('Net Income')
            total_operating_activities.plot.bar(ax=axes[0,1], rot=0).set_title('Total Cash Flow From Operating Activities')
            total_investing_activities.plot.bar(ax=axes[1,0], rot=0).set_title('Total Cash Flows From Investing Activities')
            total_financing_activities.plot.bar(ax=axes[1,1], rot=0).set_title('Total Cash Flows From Financing Activities')
            plt.show()

        else:
            for x in symbol:
                if x in cashflows:
                    try:
                        net_income[x] = cashflows[x,'Net Income']
                        total_operating_activities[x] = cashflows[x,'Total Cash Flow From Operating Activities']
                        total_investing_activities[x] = cashflows[x, 'Total Cash Flows From Investing Activities']
                        total_financing_activities[x] = cashflows[x,'Total Cash Flows From Financing Activities']

                    except KeyError:
                        continue

            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
            net_income.plot.bar(ax=axes[0,0], rot=0).set_title('Net Income')
            total_operating_activities.plot.bar(ax=axes[0,1], rot=0).set_title('Total Cash Flow From Operating Activities ')
            total_investing_activities.plot.bar(ax=axes[1,0], rot=0).set_title('Total Cash Flows From Investing Activities')
            total_financing_activities.plot.bar(ax=axes[1,1], rot=0).set_title('Total Cash Flows From Financing Activities')
            plt.show()
        
    else:
        net_income[symbol] = cashflows[symbol,'Net Income']
        total_operating_activities[symbol] = cashflows[symbol,'Total Cash Flow From Operating Activities']
        total_investing_activities[symbol] = cashflows[symbol, 'Total Cash Flows From Investing Activities']
        total_financing_activities[symbol] = cashflows[symbol,'Total Cash Flows From Financing Activities']

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
        net_income.plot.bar(ax=axes[0,0], rot=0).set_title('Net Income')
        total_operating_activities.plot.bar(ax=axes[0,1], rot=0).set_title('Total Cash Flow From Operating Activities ')
        total_investing_activities.plot.bar(ax=axes[1,0], rot=0).set_title('Total Cash Flows From Investing Activities')
        total_financing_activities.plot.bar(ax=axes[1,1], rot=0).set_title('Total Cash Flows From Financing Activities')
        plt.show()