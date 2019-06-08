"""
financials.py
-------------

This module provides the functions to calculate financials of a company.

It contains the following functions:
total_rev: calulates total revenue
gprofit: gross profit
ebitda: earnings before interest, tax, depreciation and amortization
ebit: earnings before interest and tax
ebt: earnings before tax
net_income: net income
inc_statement: calculates income statement items
assets: total assets
liabilities: total liabilities
equity: total shareholders' equity
ret_earnings: ending retained earnings
"""

__author__ = 'Mehmet Dogan'

def total_rev(revenue, other_revenue = 0):
    """
    Computes the total revenue.

    @params
    -------
    revenue: revenue (sales) for the period
    other_revenue: optional, other revenue

    returns
    -------
    Returns total revenue, int or float
    """
    return revenue + other_revenue

def gprofit(total_revenue, cogs):
    """
    Computes the gross profit.

    @params
    -------
    total_revenue: total revenue for the period
    cogs: cost of goods sold

    returns
    -------
    Returns gross profit, int or float
    """
    return total_revenue - cogs

def ebitda(gross_profit, sg_a):
    """
    Computes EBITDA(earnings before interest, tax, depreciation and amortizatin).

    @params
    -------
    gross_profit: gross profit for the period
    sg_a: selling, general and administrative cost

    returns
    -------
    Returns EBITDA, int or float
    """
    return gross_profit - sg_a

def ebit(ebitda, d_and_a):
    """
    Computes EBIT(earnings before interest and tax).

    @params
    -------
    ebitda: EBITDA(earnings before interest, tax, depreciation and amortizatin)
    d_and_a: depreciation and amortizatin

    returns
    -------
    Returns EBIT, int or float
    """
    return ebitda - d_and_a

def ebt(ebit, int_exp):
    """
    Computes EBT(Earnings before tax) the gross profit.

    @params
    -------
    ebit: earnings before interest and tax
    int_exp: interest expense

    returns
    -------
    Returns EBT, int or float
    """
    return ebit - int_exp

def net_income(ebt, tax):
    """
    Computes net income.

    @params
    -------
    ebt: earnings before tax
    tax: tax expense

    returns
    -------
    Returns net income, int or float
    """
    return ebt - tax



def inc_statement(revenue, cogs, sg_a, d_and_a, int_exp, tax, other_revenue = 0):
    """
    Computes the main income statement items.

    @params
    -------
    revenue: revenue for the period
    cogs: cost of goods sold
    sg_a:
    d_and_a: depreciation and amortizatin
    int_exp: interest expense
    tax: income tax
    other_revenue: optional, other revenue

    returns
    -------
    Returns a dictionary with income statement items; total_revenue,
    gross_profit, ebitda, ebit, ebt, net_income
    """
    total_revenue = revenue + other_revenue
    gross_profit = total_revenue - cogs
    ebitda = gross_profit - sg_a
    ebit = ebitda - d_and_a
    ebt = ebit - int_exp
    net_income = ebt - tax
    income_dict = {
        "total_revenue" : total_revenue,
        "gross_profit" : gross_profit,
        "ebitda" : ebitda,
        "ebit" : ebit,
        "ebt" : ebt,
        "net_income" : net_income
    }

    return income_dict


def assets(liabilities, equity):
    """
    Computes total assets.

    @params
    -------
    liabilities: total liabilities
    equity: shareholders' equity

    returns
    -------
    Returns total assets, int or float
    """
    return liabilities + equity


def liabilities(assets, equity):
    """
    Computes total liabilities.

    @params
    -------
    assets: total assets
    equity: shareholders' equity

    returns
    -------
    Returns total liabilities, int or float
    """
    return assets - equity


def equity(assets, liabilities):
    """
    Computes shareholders' equity.

    @params
    -------
    assets: total assets
    liabilities: total liabilities

    returns
    -------
    Returns shareholders' equity, int or float
    """
    return assets - liabilities


def ret_earnings(bre, net_income, dividend):
    """
    Computes ending retained earnings.

    @params
    -------
    bre: beginning retained earnings (at the beginning of the period)
    net_income: net income
    dividend: dividend payment to shareholders

    returns
    -------
    Returns ending retained earnings (at the end of the period), int or float
    """
    return (bre + net_income) - dividend
