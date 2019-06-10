def balance_sheet_analysis(balance_sheet, symbol = 0, log=False):

    '''
    Graphically gives an overview of the various balance sheet items overtime.
    When selecting multiple symbols, you are able to visually see the difference
    between the companies. 
        
    Parameters
    ----------
    balance_sheet : DataFrame
                    The data created with the balance_sheet() function.
    
    symbol        : string or list
                    Company ticker(s) either displayed as a string for one company or as a list
                    when multiple companies are selected.

    log           : boolean
                    Default on False. Gives the option to convert everything in log values.
        
    Returns
    -------
    The following graphs:
        cash
        inventory
        accounts receivable
        short term investments
        property, plant and equipment
        total current assets
        accounts payable
        long term debt
        other current liabilities
        total current liabilities
        common stock
        preferred stock
        retained earnings
        total stockholder equity
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
    
    cash = pd.DataFrame(index=balance_sheet.index)
    inventory = pd.DataFrame(index=balance_sheet.index)
    accounts_receivable = pd.DataFrame(index=balance_sheet.index)
    short_term_investments = pd.DataFrame(index=balance_sheet.index)
    property_plant_equipment = pd.DataFrame(index=balance_sheet.index)
    total_current_assets = pd.DataFrame(index=balance_sheet.index)
    accounts_payable = pd.DataFrame(index=balance_sheet.index)
    long_term_debt = pd.DataFrame(index=balance_sheet.index)
    other_current_liabilities = pd.DataFrame(index=balance_sheet.index)
    total_current_liabilities = pd.DataFrame(index=balance_sheet.index)
    common_stock = pd.DataFrame(index=balance_sheet.index)
    preferred_stock = pd.DataFrame(index=balance_sheet.index)
    retained_earnings = pd.DataFrame(index=balance_sheet.index)
    total_stockholder_equity = pd.DataFrame(index=balance_sheet.index)
    
    
    if type(symbol) == list:
        if log == True:
            import warnings
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            for x in symbol:
                if x in balance_sheet:
                    try: 
                        cash[x] = np.log(balance_sheet[x, 'Cash And Cash Equivalents'])
                        inventory[x] = np.log(balance_sheet[x, 'Inventory'])
                        accounts_receivable[x] = np.log(balance_sheet[x, 'Net Receivables'])
                        short_term_investments[x] = np.log(balance_sheet[x, 'Short Term Investments'])
                        property_plant_equipment[x] = np.log(balance_sheet[x, 'Property Plant and Equipment'])
                        total_current_assets[x] = np.log(balance_sheet[x, 'Total Current Assets'])

                        accounts_payable[x] = np.log(balance_sheet[x, 'Accounts Payable'])
                        long_term_debt[x] = np.log(balance_sheet[x, 'Long Term Debt'])
                        other_current_liabilities[x] = np.log(balance_sheet[x, 'Other Current Liabilities'])
                        total_current_liabilities[x] = np.log(balance_sheet[x, 'Total Current Liabilities'])

                        common_stock[x] = np.log(balance_sheet[x,'Common Stock'])
                        preferred_stock[x] = np.log(balance_sheet[x,'Preferred Stock'])
                        retained_earnings[x] = np.log(balance_sheet[x, 'Retained Earnings'])
                        total_stockholder_equity[x] = np.log(balance_sheet[x, 'Total Stockholder Equity'])
                    
                    except KeyError:
                        continue

            print('Assets')
            fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15,15))
            cash.plot.bar(ax=axes[0,0], rot=0).set_title('Cash And Cash Equivalents')
            inventory.plot.bar(ax=axes[0,1], rot=0).set_title('Inventory')
            accounts_receivable.plot.bar(ax=axes[1,0], rot=0).set_title('Accounts Receivables')
            short_term_investments.plot.bar(ax=axes[1,1], rot=0).set_title('Short Term Investments')
            property_plant_equipment.plot.bar(ax=axes[2,0], rot=0).set_title('Property Plant and Equipment')
            total_current_assets.plot.bar(ax=axes[2,1], rot=0).set_title('Total Current Assets')
            plt.show()

            print('Liabilities')
            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
            accounts_payable.plot.bar(ax=axes[0,0], rot=0).set_title('Accounts Payable')
            long_term_debt.plot.bar(ax=axes[0,1], rot=0).set_title('Long Term Debt')
            other_current_liabilities.plot.bar(ax=axes[1,0], rot=0).set_title('Other Current Liabilities')
            total_current_liabilities.plot.bar(ax=axes[1,1], rot=0).set_title('Total Current Liabilities')
            plt.show()

            print('Equity')
            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
            common_stock.plot.bar(ax=axes[0,0], rot=0).set_title('Common Stock')
            preferred_stock.plot.bar(ax=axes[0,1], rot=0).set_title('Preferred Stock')
            retained_earnings.plot.bar(ax=axes[1,0], rot=0).set_title('Retained Earnings')
            total_stockholder_equity.plot.bar(ax=axes[1,1], rot=0).set_title('Total Stockholder Equity')
            plt.show()
        
        else:
            for x in symbol:
                if x in balance_sheet:
                    try: 
                        cash[x] = balance_sheet[x, 'Cash And Cash Equivalents']
                        inventory[x] = balance_sheet[x, 'Inventory']
                        accounts_receivable[x] = balance_sheet[x, 'Net Receivables']
                        short_term_investments[x] = balance_sheet[x, 'Short Term Investments']
                        property_plant_equipment[x] = balance_sheet[x, 'Property Plant and Equipment']
                        total_current_assets[x] = balance_sheet[x, 'Total Current Assets']

                        accounts_payable[x] = balance_sheet[x, 'Accounts Payable']
                        long_term_debt[x] = balance_sheet[x, 'Long Term Debt']
                        other_current_liabilities[x] = balance_sheet[x, 'Other Current Liabilities']
                        total_current_liabilities[x] = balance_sheet[x, 'Total Current Liabilities']

                        common_stock[x] = balance_sheet[x,'Common Stock']
                        preferred_stock[x] = balance_sheet[x,'Preferred Stock']
                        retained_earnings[x] = balance_sheet[x, 'Retained Earnings']
                        total_stockholder_equity[x] = balance_sheet[x, 'Total Stockholder Equity']
                    
                    except KeyError:
                        continue

            print('Assets')
            fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15,15))
            cash.plot.bar(ax=axes[0,0], rot=0).set_title('Cash And Cash Equivalents')
            inventory.plot.bar(ax=axes[0,1], rot=0).set_title('Inventory')
            accounts_receivable.plot.bar(ax=axes[1,0], rot=0).set_title('Accounts Receivables')
            short_term_investments.plot.bar(ax=axes[1,1], rot=0).set_title('Short Term Investments')
            property_plant_equipment.plot.bar(ax=axes[2,0], rot=0).set_title('Property Plant and Equipment')
            total_current_assets.plot.bar(ax=axes[2,1], rot=0).set_title('Total Current Assets')
            plt.show()

            print('Liabilities')
            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
            accounts_payable.plot.bar(ax=axes[0,0], rot=0).set_title('Accounts Payable')
            long_term_debt.plot.bar(ax=axes[0,1], rot=0).set_title('Long Term Debt')
            other_current_liabilities.plot.bar(ax=axes[1,0], rot=0).set_title('Other Current Liabilities')
            total_current_liabilities.plot.bar(ax=axes[1,1], rot=0).set_title('Total Current Liabilities')
            plt.show()

            print('Equity')
            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
            common_stock.plot.bar(ax=axes[0,0], rot=0).set_title('Common Stock')
            preferred_stock.plot.bar(ax=axes[0,1], rot=0).set_title('Preferred Stock')
            retained_earnings.plot.bar(ax=axes[1,0], rot=0).set_title('Retained Earnings')
            total_stockholder_equity.plot.bar(ax=axes[1,1], rot=0).set_title('Total Stockholder Equity')
            plt.show()

    else:
        cash[symbol] = balance_sheet[symbol,'Cash And Cash Equivalents']
        inventory[symbol] = balance_sheet[symbol,'Inventory']
        accounts_receivable[symbol] = balance_sheet[symbol,'Net Receivables']
        short_term_investments[symbol] = balance_sheet[symbol,'Short Term Investments']
        property_plant_equipment[symbol] = balance_sheet[symbol,'Property Plant and Equipment']
        total_current_assets[symbol] = balance_sheet[symbol,'Total Current Assets']

        accounts_payable[symbol] = balance_sheet[symbol,'Accounts Payable']
        long_term_debt[symbol] = balance_sheet[symbol,'Long Term Debt']
        other_current_liabilities[symbol] = balance_sheet[symbol,'Other Current Liabilities']
        total_current_liabilities[symbol] = balance_sheet[symbol,'Total Current Liabilities']

        common_stock[symbol] = balance_sheet[symbol,'Common Stock']
        preferred_stock[symbol] = balance_sheet[symbol,'Preferred Stock']
        retained_earnings[symbol] = balance_sheet[symbol,'Retained Earnings']
        total_stockholder_equity[symbol] = balance_sheet[symbol,'Total Stockholder Equity']
        
        print('Assets')
        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15,15))
        cash.plot.bar(ax=axes[0,0], rot=0).set_title('Cash And Cash Equivalents')
        inventory.plot.bar(ax=axes[0,1], rot=0).set_title('Inventory')
        accounts_receivable.plot.bar(ax=axes[1,0], rot=0).set_title('Accounts Receivables')
        short_term_investments.plot.bar(ax=axes[1,1], rot=0).set_title('Short Term Investments')
        property_plant_equipment.plot.bar(ax=axes[2,0], rot=0).set_title('Property Plant and Equipment')
        total_current_assets.plot.bar(ax=axes[2,1], rot=0).set_title('Total Current Assets')
        plt.show()
        
        print('Liabilities')
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
        accounts_payable.plot.bar(ax=axes[0,0], rot=0).set_title('Accounts Payable')
        long_term_debt.plot.bar(ax=axes[0,1], rot=0).set_title('Long Term Debt')
        other_current_liabilities.plot.bar(ax=axes[1,0], rot=0).set_title('Other Current Liabilities')
        total_current_liabilities.plot.bar(ax=axes[1,1], rot=0).set_title('Total Current Liabilities')
        plt.show()
        
        print('Equity')
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
        common_stock.plot.bar(ax=axes[0,0], rot=0).set_title('Common Stock')
        preferred_stock.plot.bar(ax=axes[0,1], rot=0).set_title('Preferred Stock')
        retained_earnings.plot.bar(ax=axes[1,0], rot=0).set_title('Retained Earnings')
        total_stockholder_equity.plot.bar(ax=axes[1,1], rot=0).set_title('Total Stockholder Equity')
        plt.show()