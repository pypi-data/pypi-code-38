import numpy as np
#import matplotlib.pyplot as plt

def C(S, K, volatility, days):
    runs = 100000
    k = np.cumprod(1 + np.random.randn(runs, days)*volatility/np.sqrt(252),1) * S
    market_price = np.mean((k[:,-1]-K) * ((k[:,-1]-K) > 0))
    market_price = np.round(market_price,2)
    return market_price

def P(S, K, volatility, days):
    runs = 100000
    k = np.cumprod(1 + np.random.randn(runs, days)*volatility/np.sqrt(252),1) * S
    market_price = -np.mean((k[:,-1]-K) * ((k[:,-1]-K) < 0))
    market_price = np.round(market_price,2)
    return market_price
