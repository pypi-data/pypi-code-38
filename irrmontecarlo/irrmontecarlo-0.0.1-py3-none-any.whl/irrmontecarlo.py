#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IRR Monte Carlo Framework
"""

import numpy as np
from matplotlib import pyplot as plt
import random as rd
import pandas as pd

#Fund Class - with attributes initialCapital, portfolio and value
class Fund:
    
    def __init__(self, Capital, Portfolio):
        self.initialcapital = Capital
        self.portfolio = Portfolio
        self.value =  sum(asset.price for asset in Portfolio)

#Asset Class with attribute Price, yearly return, currency and daily return. 
class Asset:
    
    def __init__(self, Price, Returnyoy, Currency):
        self.price = Price
        self.returnyoy = Returnyoy
        self.currency = Currency
        self.daily_return = np.exp(np.log(Returnyoy)/252)

# Scales asset prices to fit portfolio value
def portfolioScaling(prices, val):
    
    scaledPrices = []
    a = sum(prices)
    sf = val/a
    
    for i in prices:
        scaledPrices.append(i * sf)
        
    return scaledPrices

# Randomly generates a portfolio with mean returns 8% anually.
def portfolioGenerator(portfolioVal, noAssets, US, EUR, GB, usAssets, eurAssets, gbAssets):
    
    portfolio = []
    usp = []
    eurp = []
    gbp = []
    
    usa = usAssets
    eura = eurAssets
    gba = gbAssets
    
    usval = portfolioVal * US
    eurval = portfolioVal * EUR
    gbval = portfolioVal * GB
    
    for i in range(usa):
        price = rd.randint(0,usval)
        usp.append(price)
        
    for i in range(eura):
        price = rd.randint(0,eurval)
        eurp.append(price)
        
    for i in range(gba):
        price = rd.randint(0,gbval)
        gbp.append(price)
        
    usp = portfolioScaling(usp, usval)    
    eurp = portfolioScaling(eurp, usval)
    gbp = portfolioScaling(gbp, usval)

    p = usp + eurp + gbp
    
    for i in range(len(p)):
        ret = rd.gauss(1.08,0.04)
        if (i > 0 and i <= (usAssets-1)):
            portfolio.append(Asset(p[i], ret, "US"))
        elif (i > (usAssets-1) and i <= (eurAssets-1)):
            portfolio.append(Asset(p[i], ret, "EUR"))
        elif (i > (eurAssets-1)):
            portfolio.append(Asset(p[i], ret, "GB"))
    
    return portfolio

# Provides portfolio of assets with prices in respective currencies.
def portfolioValue(portfolio, eur_price, gbp_price):
    
    for i in range(len(portfolio)):
        
        if(portfolio[i].currency == "EUR"):
            portfolio[i].price = portfolio[i].price / eur_price
        elif(portfolio[i].currency == "GBP"):
            portfolio[i].price = portfolio[i].price / gbp_price
            
    return portfolio   

# Runs a monte carlo simulation from Foreign Exchange price series using the normal distrubtion and daily volatility
def MC(num_sims, eurusd):

    returns = eurusd.pct_change()

    last_price = eurusd[-1]

    num_days = 252
    simulation_df = pd.DataFrame()
    
    for x in range(num_sims):
        count = 0
        daily_vol = returns.std()
        
        price_series = []
        
        price = last_price * (1 + np.random.normal(0, daily_vol))
        price_series.append(price)
        
        for y in range(num_days):
            if count == 251:
                break
            price = price_series[count] * (1 + np.random.normal(0, daily_vol))
            price_series.append(price)
            count += 1
            
        simulation_df[x] = price_series
        
    return simulation_df

# Runs Monte Carlo simulations of two FOREX price series using normal distributions and daily volatility. 
#Returns result in a dataframe where 1st num_sims columns are of eurusd and next num_sims columns are of gbpusd
def multiMC(num_sims, eurusd, gbpusd):

    eur_returns = eurusd.pct_change()
    gbp_returns = gbpusd.pct_change()

    eur_last_price = eurusd[-1]
    gbp_last_price = gbpusd[-1]

    num_days = 252
    eur_simulation_df = pd.DataFrame()
    gbp_simulation_df = pd.DataFrame()
    
    for x in range(num_sims):
        count = 0
        eur_daily_vol = eur_returns.std()
        gbp_daily_vol = gbp_returns.std()
        
        eur_price_series = []
        gbp_price_series = []
        
        eur_price = eur_last_price * (1 + np.random.normal(0, eur_daily_vol))
        eur_price_series.append(eur_price)
        
        gbp_price = gbp_last_price * (1 + np.random.normal(0, gbp_daily_vol))
        gbp_price_series.append(gbp_price)
        
        for y in range(num_days):
            if count == 251:
                break
            eur_price = eur_price_series[count] * (1 + np.random.normal(0, eur_daily_vol))
            eur_price_series.append(eur_price)
            
            gbp_price = gbp_price_series[count] * (1 + np.random.normal(0, gbp_daily_vol))
            gbp_price_series.append(gbp_price)
            count += 1
            
        eur_simulation_df[x] = eur_price_series
        gbp_simulation_df[x+100] = eur_price_series
        
    simulation_df = pd.concat([eur_simulation_df, gbp_simulation_df], axis = 1)    
        
    return simulation_df

# Plots the result of a FOREX monte carlo simulation.
def plotMC(currency_series, num_sims):
    
    sim_df = MC(num_sims, currency_series)

    fig = plt.figure() 
    fig.suptitle('Monte Carlo Simulation')
    plt.plot(sim_df)
    plt.axhline(y = currency_series[0], color = 'r', linestyle = '-')
    plt.xlabel('Day')
    plt.ylabel('Price')
    plt.show()
    
    return

# Uses above FOREX Monte Carlo simulation to simulate the value of a portfolio 1 year (or time period) from now.
def portfolioMC(portfolio, portfolio_init, eurusd, gbpusd, num_sims):
    
    eur_initial = eurusd[0]
    gbp_initial = gbpusd[0]

    sim_df = multiMC(num_sims, eurusd, gbpusd)
    
    port_series = []
    
    for i in range(num_sims):
        portfolio_value = 0
        
        eur_last = sim_df.iloc[251,i]
        gbp_last = sim_df.iloc[251,i+99]
        
        for i in range(len(portfolio)):
            
            if(portfolio[i].currency == "EUR"):
                portfolio[i].price = portfolio[i].price/eur_initial * eur_last * portfolio[i].returnyoy
                portfolio_value += portfolio[i].price
                portfolio[i].price = portfolio_init[i].price
            elif(portfolio[i].currency == "GBP"):
                portfolio[i].price = portfolio[i].price/gbp_initial * gbp_last * portfolio[i].returnyoy
                portfolio_value += portfolio[i].price
                portfolio[i].price = portfolio_init[i].price
            elif(portfolio[i].currency =="US"):
                portfolio[i].price = portfolio[i].price * portfolio[i].returnyoy
                portfolio_value += portfolio[i].price
                portfolio[i].price = portfolio_init[i].price
                
        port_series.append(portfolio_value)
        portfolio_value = 0
        
        
    return port_series

#Generates the mean of a series of simulated portfolio values.
def meanIRR(port_series, Fund):
    
    irr_series = []
    
    for i in range(len(port_series)):
        irr = (port_series[i] / Fund.value) -1
        irr_series.append(irr)
    
    return np.mean(irr_series)

# Returns the IRR for a portfolio using FOREX monte carlo simulation.
def IRRMonteCarlo(num_sims, Fund, portfolio_init, portfolio, eurusd, gbpusd):
    
    port_mc = portfolioMC(portfolio, portfolio_init, eurusd, gbpusd, num_sims)
    irr_avg = meanIRR(port_mc, Fund)
    
    return irr_avg
