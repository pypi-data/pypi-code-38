def rss_feed(symbol = 0, write_pickle = True, read_pickle = False):  

    '''
    Provides latest news from Yahoo Finance for each selected symbol.
        
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
    rss_feed      : DataFrame
                    Shows news items from Yahoo Finance.
    '''

    import lxml
    from lxml import html
    import requests
    import numpy as np
    import pandas as pd
    import feedparser as fp
    import pickle 

    if read_pickle == True:
        rss_feed = pd.read_pickle('newsfeed')
        return rss_feed
    
    else:
        rss_feed = {}

        if symbol == 0:
            page = requests.get('https://finance.yahoo.com/trending-tickers')
            tree = html.fromstring(page.content)
            table = tree.xpath('//table')
            symbol = pd.read_html(lxml.etree.tostring(table[0], method='html'))[0]['Symbol'].to_list()
            print('No input is given thus using the Trending Tickers from Yahoo Finance: https://finance.yahoo.com/trending-tickers')
    
    if len(str(symbol)) > 6:
        for s in symbol:
            rss_feed[s,'Title'] = []
            rss_feed[s,'Link'] = []

            feed = fp.parse('http://finance.yahoo.com/rss/headline?s=' + s)


            # RSS Feed Data
            for post in feed['entries']:
                try:
                    rss_feed[s,'Title'].append(post.title)
                    rss_feed[s,'Link'].append(post.link)

                except KeyError:
                    continue
    else:
        rss_feed[symbol,'Title'] = []
        rss_feed[symbol,'Link'] = []

        feed = fp.parse('http://finance.yahoo.com/rss/headline?s=' + symbol)


        # RSS Feed Data
        for post in feed['entries']:
            try:
                rss_feed[symbol,'Title'].append(post.title)
                rss_feed[symbol,'Link'].append(post.link)

            except KeyError:
                continue
    try:
        rss_feed = pd.DataFrame(rss_feed.values(), index=rss_feed.keys()).transpose()
        
        if write_pickle == True:
            rss_feed.to_pickle('newsfeed')

    except ValueError as e:
        print('Could not convert rss_feed to a DataFrame due to: ', e)

    return rss_feed