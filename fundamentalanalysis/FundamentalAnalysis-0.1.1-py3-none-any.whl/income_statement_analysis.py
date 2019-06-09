def income_statement_analysis(income_statement, symbol = 0, log=False):
    
    '''
    Graphically gives an overview of the various income statement items overtime.
    When selecting multiple symbols, you are able to visually see the difference
    between the companies. 
        
    Parameters
    ----------
    income_statement : DataFrame
                       The data created with the cashflows() function.
    
    symbol           : string or list
                       Company ticker(s) either displayed as a string for one company or as a list
                       when multiple companies are selected.

    log              : boolean
                       Default on False. Gives the option to convert everything in log values.
        
    Returns
    -------
    The following graphs:
        total revenue
        cost of revenue
        general expenses
        research development
        operating profit
        net income

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
        
    total_revenue = pd.DataFrame(index=income_statement.index)
    cost_of_revenue = pd.DataFrame(index=income_statement.index)
    general_expenses = pd.DataFrame(index=income_statement.index)
    research_development = pd.DataFrame(index=income_statement.index)
    operating_profit = pd.DataFrame(index=income_statement.index)
    net_income = pd.DataFrame(index=income_statement.index)
        
    
    if type(symbol) == list:
        if log == True:
            import warnings
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            for x in symbol:
                if x in income_statement:
                    try:
                        total_revenue[x] = np.log(income_statement[x,'Total Revenue'])
                        cost_of_revenue[x] = np.log(income_statement[x,'Cost of Revenue'])
                        general_expenses[x] = np.log(income_statement[x, 'Selling General and Administrative'])
                        research_development[x] = np.log(income_statement[x,'Research Development'])
                        operating_profit[x] = np.log(income_statement[x,'Operating Income or Loss'])
                        net_income[x] = np.log(income_statement[x,'Net Income From Continuing Ops'])
                
                    except KeyError:
                        continue
                    

            fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15,15))
            total_revenue.plot.bar(ax=axes[0,0], rot=0).set_title('Total Revenue')
            cost_of_revenue.plot.bar(ax=axes[0,1], rot=0).set_title('Cost of Revenue (COGS)')
            general_expenses.plot.bar(ax=axes[1,0], rot=0).set_title('Selling, General and Administrative Expenses (SG&A)')
            research_development.plot.bar(ax=axes[1,1], rot=0).set_title('Research Development')
            operating_profit.plot.bar(ax=axes[2,0], rot=0).set_title('Operating Income or Loss')
            net_income.plot.bar(ax=axes[2,1], rot=0).set_title('Net Income From Continuing Ops')
            plt.show()

        else:
            for x in symbol:
                if x in income_statement:
                    try:
                        total_revenue[x] = income_statement[x,'Total Revenue']
                        cost_of_revenue[x] = income_statement[x,'Cost of Revenue']
                        general_expenses[x] = income_statement[x, 'Selling General and Administrative']
                        research_development[x] = income_statement[x,'Research Development']
                        operating_profit[x] = income_statement[x,'Operating Income or Loss']
                        net_income[x] = income_statement[x,'Net Income From Continuing Ops']

                    except KeyError:
                        continue

            fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15,15))
            total_revenue.plot.bar(ax=axes[0,0], rot=0).set_title('Total Revenue')
            cost_of_revenue.plot.bar(ax=axes[0,1], rot=0).set_title('Cost of Revenue (COGS)')
            general_expenses.plot.bar(ax=axes[1,0], rot=0).set_title('Selling, General and Administrative Expenses (SG&A)')
            research_development.plot.bar(ax=axes[1,1], rot=0).set_title('Research Development')
            operating_profit.plot.bar(ax=axes[2,0], rot=0).set_title('Operating Income or Loss')
            net_income.plot.bar(ax=axes[2,1], rot=0).set_title('Net Income From Continuing Ops')
            plt.show()
        
    else:
        total_revenue[symbol] = income_statement[symbol,'Total Revenue']
        cost_of_revenue[symbol] = income_statement[symbol,'Cost of Revenue']
        general_expenses[symbol] = income_statement[symbol, 'Selling General and Administrative']
        research_development[symbol] = income_statement[symbol,'Research Development']
        operating_profit[symbol] = income_statement[symbol,'Operating Income or Loss']
        net_income[symbol] = income_statement[symbol,'Net Income From Continuing Ops']

        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15,15))
        total_revenue.plot.bar(ax=axes[0,0], rot=0).set_title('Total Revenue')
        cost_of_revenue.plot.bar(ax=axes[0,1], rot=0).set_title('Cost of Revenue (COGS)')
        general_expenses.plot.bar(ax=axes[1,0], rot=0).set_title('Selling, General and Administrative Expenses (SG&A)')
        research_development.plot.bar(ax=axes[1,1], rot=0).set_title('Research Development')
        operating_profit.plot.bar(ax=axes[2,0], rot=0).set_title('Operating Income or Loss')
        net_income.plot.bar(ax=axes[2,1], rot=0).set_title('Net Income From Continuing Ops')
        plt.show()