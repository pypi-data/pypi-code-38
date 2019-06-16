import numpy as np
import numpy.random as rng

import pandas as pd

import dynmix as dm

import matplotlib.cm as cm
import matplotlib.pyplot as plt

def get_eu(raw, show=True):
    # Get EU country codes
    code_eu = pd.read_excel('/home/vsartor/Drive/Masters/Reports/EU/CODE_EU.xls')
    # Select only EU countries
    eu = raw[[(x in code_eu['Country Code'].values) for x in raw['Country Code']]]
    # Drop useless columns
    eu = eu.drop(['Indicator Name', 'Indicator Code'], 1)
    # Fetch the years
    years = eu.columns[2:]
    
    # Find out count of complete data per year
    complete_count = np.zeros(len(years))
    for i, year in enumerate(years):
        complete_count[i] = np.sum(np.logical_not(np.isnan(eu[year]).values))
    # Find out the indexes with complete data
    maxes = np.argwhere(complete_count == np.amax(complete_count))
    
    # Display
    if show:
        # Find out first year and last year
        begin, end = years[np.min(maxes)], years[np.max(maxes)]
        # Display
        plt.plot(years, complete_count)
        plt.xticks(rotation='vertical')
        plt.axvline(begin, color='k', linestyle='--')
        plt.axvline(end, color='k', linestyle='--')
        plt.axhline(eu.shape[0], color='k', linestyle=':')
        plt.show()   
    
    return eu[['Country Name', 'Country Code'] + list(years[maxes])]

def show_series(df):
    Y = df.drop(df.columns[:2], 1).values
    x = df['Country Code'].values
    years = np.array([int(x) for x in df.columns[2:]])
    
    for name, series in zip(x, Y):
        plt.plot(years, series, label=name)
        plt.legend(bbox_to_anchor=(1.05, 1), ncol=2)
        plt.axhline(0, linestyle='--', color='k')
    plt.show()

# Renewable
raw = pd.read_excel('/home/vsartor/Drive/Masters/Reports/EU/RENEWABLE_RAW.xls', skiprows=2, header=1)
df = get_eu(raw, show=False)

Y = df.drop(df.columns[:2], 1).values.T
n, T = Y.shape
years = np.array([int(x) for x in df.columns[2:]])

F_list = [np.eye(1), np.eye(1)]
G_list = [np.eye(1), np.eye(1)]

eta, theta, phi, W = dm.static.estimator(Y, F_list, G_list)
