"""
ratios.py
---------

This module provides functions to calculate main financial ratios used in financial analysis.
"""

__author__ = 'Mehmet Dogan'

def inventory_turnover(cogs, average_inventory):
    """Computes inventory turnover ratio.

    @params
    -------
    cogs: cost of goods sold
    average_inventory: average inventory for the period

    returns
    -------
    Turnover ratio, int or float

    explanation
    -----------

    """
    return  cogs / average_inventory



def days_of_inventory_on_hand(number_of_days, inventory_turnover):
    """Computes days of inventory on hand.

    @params
    -------
    number_of_days: number of days in period
    inventory_turnover: inventory_turnover

    returns
    -------
    Days of inventory on hand, int or float

    explanation
    -----------

    """
    return number_of_days / inventory_turnover



def receivables_turnover(revenue, average_receivables):
    """Computes receivables turnover.

    @params
    -------
    revenue: revenue
    average_receivables: average receivables for the period

    returns
    -------
    Receivables turnover, int or float

    explanation
    -----------
    Receivables should be studied in relation to the annual sales, where available,
    and in relation to changes shown over a period of years. If the receivables seem
    unusuallu large in proportion to sales, or to other items, there is some indication
    that an unduly liberal credit policy has been pursued, and that more or less serious losses
    are likely to be sustained from bad accounts.
    """
    return revenue / average_receivables



def days_of_sales_outstanding(number_of_days, receivables_turnover):
    """Computes days of sales outstanding.

    @params
    -------
    number_of_days: number of days in period
    receivables_turnover: receivables_turnover

    returns
    -------
    Days of sales outstanding, int or float

    explanation
    -----------

    """
    return number_of_days / receivables_turnover


def payables_turnover(purchases, average_trade_payables):
    """Computes payables turnover.

    @params
    -------
    purchases: purchases
    average_trade_payables: average_trade_payables

    returns
    -------
    Purchases turnover, int or float

    explanation
    -----------

    """
    return purchases / average_trade_payables


    def number_of_days_of_payables(number_of_days, payables_turnover):
        """Computes number of days of payables.

        @params
        -------
        number_of_days: number of days in period
        payables_turnover: payables turnover

        returns
        -------
        Number of days of payables, int or float

        explanation
        -----------

        """
        return number_of_days / payables_turnover


    def working_capital_turnover(revenue, average_working_capital):
        """Computes working capital turnover.

        @params
        -------
        revenue: revenue
        average_working_capital: average working capital in period

        returns
        -------
        Working capital turnover, int or float

        explanation
        -----------

        """
        return revenue / average_working_capital


def fixed_asset_turnover(revenue, average_net_fixed_assets):
    """Computes fixed asset turnover.

    @params
    -------
    revenue: revenue
    average_net_fixed_assets: average net fixed assets in period

    returns
    -------
    Fixed asset turnover, int or float

    explanation
    -----------

    """
    return revenue / average_net_fixed_assets



def total_asset_turnover(revenue, average_total_assets):
    """Computes total asset turnover.

    @params
    -------
    revenue: revenue
    average_total_assets: average total assets in period

    returns
    -------
    Total asset turnover, int or float

    explanation
    -----------

    """
    return revenue / average_total_assets


##### Liquidity

def current_ratio(current_assets, current_liabilities, inventory = 0):
    """Computes current ratio.

    @params
    -------
    current_assets: current assets
    current_liabilities: current_liabilities
    inventory: inventory

    returns
    -------
    Current ratio, int or float

    explanation
    -----------

    """
    return (current_assets-inventory) / current_liabilities



def quick_ratio(cash, investments, receivables, current_liabilities):
    """Computes quick ratio.

    @params
    -------
    cash: cash
    investments: short-term marketible investments
    receivables: receivables
    current_liabilities: current_liabilities

    returns
    -------
    Quick ratio, int or float

    explanation
    -----------

    """
    return (cash + investments + receivables) / current_liabilities



def cash_ratio(cash, investments, current_liabilities):
    """Computes cash ratio.

    @params
    -------
    cash: cash
    investments: short-term marketible investments
    current_liabilities: current_liabilities

    returns
    -------
    Cash ratio, int or float

    explanation
    -----------

    """
    return (cash + investments) / current_liabilities


### Profitability
def gross_profit_margin(gross_profit, revenue):
    """Computes gross profit margin.

    @params
    -------
    gross_profit: gross profit
    revenue: revenue (or sales)

    returns
    -------
    Gross profit margin, int or float

    explanation
    -----------

    """
    return gross_profit / revenue



def operating_profit_margin(operating_income, revenue):
    """Computes operating profit margin.

    @params
    -------
    operating_income: gross profit
    revenue: revenue (or sales)

    returns
    -------
    Gross operating profit margin, int or float

    explanation
    -----------

    """
    return operating_income / revenue



def pretax_margin(ebt, revenue):
    """Computes pretax margin.

    @params
    -------
    ebt: earnings before tax but after interest
    revenue: revenue (or sales)

    returns
    -------
    Gross pretax margin, int or float

    explanation
    -----------

    """
    return ebt / revenue



def net_profit_margin(net_income, revenue):
    """Computes net profit margin.

    @params
    -------
    net_income: net income
    revenue: revenue (or sales)

    returns
    -------
    Net profit margin, int or float

    explanation
    -----------

    """
    return net_income / revenue



def operating_roa(operating_income, average_assets):
    """Computes operating return on assets.

    @params
    -------
    operating_income: operating income
    average_assets: average total assets

    returns
    -------
    Operating return on assets, int or float

    explanation
    -----------

    """
    return operating_income / average_assets



def roa(net_income, average_assets):
    """Computes return on assets.

    @params
    -------
    net_income: net income
    average_assets: average total assets

    returns
    -------
    Return on assets, int or float

    explanation
    -----------

    """
    return net_income / average_assets



def rotc(ebit, debt, equity):
    """Computes return on total capital.

    @params
    -------
    ebit: earnins before interest and taxes
    debt: short- and long-term debt
    equity: equity

    returns
    -------
    Return on total capital, int or float

    explanation
    -----------

    """
    return ebit / (debt - equity)



def roe(net_income, average_equity):
    """Computes return on equity.

    @params
    -------
    net_income: net income
    average_equity: average total equity

    returns
    -------
    Return on equity, int or float

    explanation
    -----------

    """
    return net_income / average_equity



def roce(net_income, preferred_dividends, average_common_equity):
    """Computes return on common equity.

    @params
    -------
    net_income: net income
    preferred_dividends: preferred dividends
    average_common_equity: average common equity

    returns
    -------
    Return on common equity, int or float

    explanation
    -----------

    """
    return (net_income - preferred_dividends) / average_common_equity


### Solvency
def debt_to_asset_ratio(debt, assets):
    """Computes debt-to-asset ratio.

    @params
    -------
    debt: total debt
    assets: total assets

    returns
    -------
    Debt-to-asset ratio, int or float

    explanation
    -----------

    """
    return debt / assets



def debt_to_capital_ratio(debt, equity):
    """Computes debt-to-caital ratio.

    @params
    -------
    debt: total debt
    equity: total shareholders' equity

    returns
    -------
    Debt-to-capital ratio, int or float

    explanation
    -----------

    """
    return debt / (debt + equity)



def debt_to_equity_ratio(debt, equity):
    """Computes debt-to-caital ratio.

    @params
    -------
    debt: total debt
    equity: total shareholders' equity

    returns
    -------
    Debt-to-equity-ratio, int or float

    explanation
    -----------

    """
    return debt / equity



def financial_leverage_ratio(average_assets, average_equity):
    """Computes financial leverage ratio.

    @params
    -------
    average_assets: average total assets
    average_equity: average total equity

    returns
    -------
    Financial leverage, int or float

    explanation
    -----------

    """
    return average_assets / average_equity



def interest_coverage(ebit, interest_payments):
    """Computes interest coverage ratio.

    @params
    -------
    ebit: earnings before interest and taxes
    interest_payments: interest payments

    returns
    -------
    Intrest coverage ratio, int or float

    explanation
    -----------

    """
    return ebit / interest_payments



def fixed_charge_coverage(ebit, lease_payments, interest_payments):
    """Computes fixed chage coverage ratio.

    @params
    -------
    ebit: earnings before interest and taxes
    lease_payments: lease payments
    interest_payments: interest payments

    returns
    -------
    Fixed charged coverage ratio, int or float

    explanation
    -----------

    """
    return (ebit + lease_payments) / (interest_payments + lease_payments)


# Valuation

def weighted_eps(net_income, dividend, outstanding_shares):
    """Computes weighted earnings per share.

    @params
    -------
    net_income: net income of company for the last 1-year period
    dividend: dividend payment of company for the last period
    outstanding_shares: # of outstanding shares, can be used dilluted shares

    returns
    -------
    Returns weighted earnings per share, int or float
    """
    weighted_eps = (net_income-dividend) / outstanding_shares

    return weighted_eps



def price_to_earnings(price, eps):
    """Computes price to earnings ratio.

    @params
    -------
    price: price per share
    eps: earnings per share, calculated by "net income / # of shares"

    returns
    -------
    Returns price to earnings ratio, int or float
    """
    pe = price / eps

    return pe



def price_to_bookvalue(price, bookvalue_per_share):
    """Computes price to book value ratio.

    @params
    -------
    price: price per share
    bookvalue_per_share: book value per share, calculated by "total coomon stock value / tangible book value"

    returns
    -------
    Returns price to book value, int or float

    explanation
    -----------
    Market price of the company should follow the its tangible book value. Deviations from its tangible book
    makes the company overvalued and undervalued.
    """
    price_to_book = price / bookvalue_per_share

    return price_to_book


def net_profit_margin(net_income, sales):
    """Computes net profit margin.

    @params
    -------
    net_income: net income
    sales: sales (revenue)

    returns
    -------
    Returns net profit margin, int or float

    explanation
    -----------
    Market price of the company should follow the its tangible book value. Deviations from its tangible book
    makes the company overvalued and undervalued.
    """
    npm = net_income / sales

    return npm



def working_capital(current_assets, current_liabilities):
    """Computes working capital.

    @params
    -------
    current_assets: current assets
    current_liabilities: current liabilities

    returns
    -------
    Working capital, int or float

    explanation
    -----------
    Working capital is important for determining the financial strength of an enterprice.
    In the working capital is found the measure of the company's ability to carry on its normal business
    comfortably and without financial stringency, to expand its operations without the need of new financing,
    and to meet emergencies and losses without disaster.
    """
    working_cap = current_assets - current_liabilities

    return working_cap






def book_value(assets, liabilities):
    """Computes book value.

    @params
    -------
    assets: total assets
    liabilities: total liabilities

    returns
    -------
    Book value of an enterprice, int or float

    explanation
    -----------
    It is assumed that if the company were to liquidate, it would receive in cash the value at which
    its various tangible assets are carried on the books.
    """
    bv = assets - liabilities

    return bv


def net_book_value(assets, liabilities, intangibles):
    """Computes net book value.

    @params
    -------
    assets: total assets
    liabilities: total liabilities
    intangibles: intangible assets

    returns
    -------
    Net [Adjusted (intangibles)] book value of an enterprice, int or float

    explanation
    -----------
    Generally the value of intangibles on the balance sheet is arbitrary and should be deducted from assets when
    calculating book value. (It is also referred to as the "net tangible assets" or "net book value" of the company)
    """

    return (assets - intangibles) - liabilities


def book_value_per_share(book_value, total_shares):
    """Computes book value per share.

    @params
    -------
    book_value: book value (equity) of an enterprice
    total_shares: total number of shares

    returns
    -------
    Book value per share, int or float

    explanation
    -----------
    Book value per share is often used as a valuation measure for companies. If it is less than the
    market price of a stock, the stock is considered as overvalued and if more than market price, stock is
    considered as undervalued.
    """


    return book_value / total_shares



def net_book_value_per_share(book_value, total_shares, intangibles):
    """Computes book value per share.

    @params
    -------
    book_value: book value (equity) of an enterprice
    total_shares: total number of shares
    intangibles: total value of intangibles

    returns
    -------
    Net book value per share, int or float

    explanation
    -----------
    Net book value per share is more correct version of book value per share and often used as a valuation
    measure for companies. If it is less than the market price of a stock, the stock is considered as
    overvalued and if more than market price, stock is considered as undervalued.
    """

    return (book_value - intangibles) / total_shares



def times_interest_earned(ebit, interest_expense):
    """Computes the times interest earned ratio.

    @params
    -------
    ebit: earnings before interest and taxes
    interest_expense: interest charges

    returns
    -------
    Times interest earned ratio, int or float

    explanation
    -----------
    The times interest earned ratio is an indicator of a company's ability to
    meet the interest payments on its debt. Higher ratio is favorable.
    """

    return ebit / interest_expense



def price_to_earnings(price_per_share, earnings_per_share):
    """Computes price to earnings ratio.

    @params
    -------
    price_per_share: share price
    earnings_per_share: earnings per share

    returns
    -------
    Price to earnings ratio, int or float

    explanation
    -----------

    """
    return price_per_share / earnings_per_share



def price_to_cash_flow(price_per_share, cash_flow_per_share):
    """Computes price to cash flow ratio.

    @params
    -------
    price_per_share: share price
    cash_flow_per_share: cash flow per share

    returns
    -------
    Price to cash flow ratio, int or float

    explanation
    -----------

    """
    return price_per_share / cash_flow_per_share


def price_to_sales(price_per_share, sales_per_share):
    """Computes price to sales ratio.

    @params
    -------
    price_per_share: share price
    sales_per_share: sales (or revenue) per share

    returns
    -------
    Price to sales ratio, int or float

    explanation
    -----------

    """
    return price_per_share / sales_per_share



def price_to_book_value(price_per_share, book_value_per_share):
    """Computes price to book value.

    @params
    -------
    price_per_share: share price
    book_value_per_share: book value per share

    returns
    -------
    Price to book value, int or float

    explanation
    -----------

    """
    return price_per_share / book_value_per_share



def eps(net_income, preferred_dividends, shares_outstanding):
    """Computes basic earnings per share.

    @params
    -------
    net_income: net income
    preferred_dividends: preferred dividends
    shares_outstanding: weighted average number of ordinary shares outstanding

    returns
    -------
    Earnings per share, int or float

    explanation
    -----------

    """
    return (net_income - preferred_dividends) / shares_outstanding



def diluted_eps(adj_net_income, shares_outstanding):
    """Computes diluted earnings per share.

    @params
    -------
    adj_net_income: adjusted income available for ordinary shares, reflecting conversion of dilutive securities
    shares_outstanding: weighted average number of ordinary and potential ordinary shares outstanding

    returns
    -------
    Diluted earnings per share, int or float

    explanation
    -----------

    """
    return adj_net_income / shares_outstanding



def cash_flow_per_share(cash_flow, shares_outstanding):
    """Computes cash flow per share.

    @params
    -------
    cash_flow: cash flow from operations
    shares_outstanding: weighted average number of shares outstanding

    returns
    -------
    Cash flow per share, int or float

    explanation
    -----------

    """
    return cash_flow / shares_outstanding


def ebitda_per_share(ebitda, shares_outstanding):
    """Computes EBITDA per share.

    @params
    -------
    ebitda: earnings before interest, taxes, depreciation and amortization
    shares_outstanding: weighted average number of shares outstanding

    returns
    -------
    EBITDA per share, int or float

    explanation
    -----------

    """
    return ebitda / shares_outstanding



def dividends_per_share(dividends, shares_outstanding):
    """Computes dividends per share.

    @params
    -------
    dividends: Common dividends declared
    shares_outstanding: weighted average number of ordinary shares outstanding

    returns
    -------
    Dividends per share, int or float

    explanation
    -----------

    """
    return dividends / shares_outstanding
