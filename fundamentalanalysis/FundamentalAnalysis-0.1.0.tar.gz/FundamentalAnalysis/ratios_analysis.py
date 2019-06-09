def ratio_analysis(ratios, rotation = False):

    '''
    Graphically gives an overview of the various ratios items sorted from low to high.
    When the ratios DataFrame features multiple companies, you are able to visually 
    see the difference between the companies. 
        
    Parameters
    ----------
    ratios        : DataFrame
                    The data created with the ratios() function.

    rotation      : boolean
                    Default on False. Rotates xlabels vertically when True.
        
    Returns
    -------
    The following graphs:
        pe trailing
        pe forward
        peg ratio
        price to sales ratio
        price to book ratio
        book value per share
        return on assets (ROA)
        return on equity (ROE)
        profit margin
        beta
        current ratio
        debt to equity ratio
    '''

    import numpy as np
    import pandas as pd 
    import matplotlib.pyplot as plt

    ratios = ratios.T
    
    pe_trailing = pd.DataFrame(index=ratios.index)
    pe_forward = pd.DataFrame(index=ratios.index)
    peg_ratio = pd.DataFrame(index=ratios.index)
    price_sales = pd.DataFrame(index=ratios.index)
    price_book = pd.DataFrame(index=ratios.index)
    book_value_per_share = pd.DataFrame(index=ratios.index)
    
    return_on_assets = pd.DataFrame(index=ratios.index)
    return_on_equity = pd.DataFrame(index=ratios.index)
    profit_margin = pd.DataFrame(index=ratios.index)
    beta = pd.DataFrame(index=ratios.index)
    
    current_ratio = pd.DataFrame(index=ratios.index)
    debt_to_equity = pd.DataFrame(index=ratios.index)
    
    pe_trailing = ratios['Trailing P/E']
    pe_forward = ratios['Forward P/E 1']
    peg_ratio = ratios['PEG Ratio (5 yr expected) 1']
    price_sales = ratios['Price/Sales (ttm)']
    price_book = ratios['Price/Book (mrq)']
    book_value_per_share = ratios['Book Value Per Share (mrq)']
    return_on_assets = ratios['Return on Assets (ttm)']
    return_on_equity = ratios['Return on Equity (ttm)']
    profit_margin = ratios['Profit Margin']
    beta = ratios['Beta (3Y Monthly)']
    current_ratio = ratios['Current Ratio (mrq)']
    debt_to_equity = ratios['Total Debt/Equity (mrq)']
    
    if rotation == False:
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
        pe_trailing.sort_values().plot.bar(ax=axes[0,0], rot=0).set_title('P/E Trailing')    
        pe_forward.sort_values().plot.bar(ax=axes[0,1], rot=0).set_title('P/E Forward')
        peg_ratio.sort_values().plot.bar(ax=axes[1,0], rot=0).set_title('PEG Ratio')
        price_sales.sort_values().plot.bar(ax=axes[1,1], rot=0).set_title('Price/Sales')
        plt.show()

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
        price_book.sort_values().plot.bar(ax=axes[0,0], rot=0).set_title('Price/Book')
        book_value_per_share.sort_values().plot.bar(ax=axes[0,1], rot=0).set_title('Book Value per Share')
        return_on_assets.sort_values().plot.bar(ax=axes[1,0], rot=0).set_title('Return on Assets (ROA)')
        return_on_equity.sort_values().plot.bar(ax=axes[1,1], rot=0).set_title('Return on Equity (ROE)')
        plt.show()

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
        profit_margin.sort_values().plot.bar(ax=axes[0,0], rot=0).set_title('Net Profit Margin')
        beta.sort_values().plot.bar(ax=axes[0,1], rot=0).set_title('Beta')
        current_ratio.sort_values().plot.bar(ax=axes[1,0], rot=0).set_title('Current Ratio')
        debt_to_equity.sort_values().plot.bar(ax=axes[1,1], rot=0).set_title('Debt to Equity')
        
        
    else:
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
        pe_trailing.sort_values().plot.bar(ax=axes[0,0]).set_title('P/E Trailing')    
        pe_forward.sort_values().plot.bar(ax=axes[0,1]).set_title('P/E Forward')
        peg_ratio.sort_values().plot.bar(ax=axes[1,0]).set_title('PEG Ratio')
        price_sales.sort_values().plot.bar(ax=axes[1,1]).set_title('Price/Sales')
        plt.show()

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
        price_book.sort_values().plot.bar(ax=axes[0,0]).set_title('Price/Book')
        book_value_per_share.sort_values().plot.bar(ax=axes[0,1]).set_title('Book Value per Share')
        return_on_assets.sort_values().plot.bar(ax=axes[1,0]).set_title('Return on Assets (ROA)')
        return_on_equity.sort_values().plot.bar(ax=axes[1,1]).set_title('Return on Equity (ROE)')
        plt.show()

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15,15))
        profit_margin.sort_values().plot.bar(ax=axes[0,0]).set_title('Net Profit Margin')
        beta.sort_values().plot.bar(ax=axes[0,1]).set_title('Beta')
        current_ratio.sort_values().plot.bar(ax=axes[1,0]).set_title('Current Ratio')
        debt_to_equity.sort_values().plot.bar(ax=axes[1,1]).set_title('Debt to Equity')
        
    plt.show()