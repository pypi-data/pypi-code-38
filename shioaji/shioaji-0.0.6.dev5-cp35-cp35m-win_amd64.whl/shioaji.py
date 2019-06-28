from shioaji.backend import get_backends
from shioaji.backend import _http, _socket
from shioaji.backend.solace.quote import Quote
import datetime as dt
from shioaji.order import Order
from shioaji.orderprops import OrderProps
from shioaji.account import StockAccount, FutureAccount
from shioaji.contracts import Contract, Stock, Future, Option
from shioaji.utils import log
from shioaji.backend.http.contract import fetch_available_product


class Shioaji:
    """ shioaji api 

    Functions:
        login 
        activate_ca
        list_accounts
        set_default_account
        get_account_margin 
        get_account_openposition
        get_account_settle_profitloss
        get_stock_account_funds
        get_stock_account_unreal_profitloss
        get_stock_account_real_profitloss
        place_order
        update_order
        update_status
        list_trades
    
    Objects:
        Quote
        Contracts
        Order
    """

    def __init__(self,
                 backend='http',
                 simulation=False,
                 proxies={},
                 currency='NTD'):
        """ initialize Shioaji to start trading

        Args:
            backend (str): {http, socket} 
                use http or socket as backend currently only support http, async socket backend coming soon.
            simulation (bool): 
                - False: to trading on real market (just use your Sinopac account to start trading)
                - True: become simulation account(need to contract as to open simulation account)
            proxies (dict): specific the proxies of your https
                ex: {'https': 'your-proxy-url'}
            currency (str): {NTX, USX, NTD, USD, HKD, EUR, JPY, GBP}
                set the default currency for display 
        """
        self.quote = Quote()
        self._http = _http(simulation, proxies)
        self.products = self._http.fetch_products()
        self._socket = _socket(simulation, proxies, products=self.products)
        if _socket and backend == 'socket':
            self._api = self._socket
        else:
            self._api = self._http
        self.stock_account = StockAccount()
        self.fut_account = FutureAccount()
        self.OrderProps = OrderProps
        self.Contracts = getattr(self._http, 'Contracts', None)
        self.Order = Order
        self._currency = currency

    def login(self, person_id, passwd):
        """ login to trading server

        Args:
            person_id (str): Same as your eleader, ileader login id(usually your person ID)
            passwd  (str): the password of your eleader login password(not ca password)
        
        """
        if self._socket:
            self._socket.login(person_id, passwd, self.quote)
        stock_account, future_account = self._http.login(person_id, passwd)
        self.stock_account = self._api.stock_account = stock_account[
            0] if stock_account else None
        self.fut_account = self._api.fut_account = future_account[
            0] if future_account else None
        self.Contracts = getattr(self._http, 'Contracts', None)
        if self.fut_account:
            self.AccountMargin = self._api.get_account_margin(
                self._currency, '1', self.fut_account)
            self.AccountOpenPosition = self._api.get_account_openposition(
                '0', '0', self.fut_account)
            self.AccountSettleProfitLoss = self._api.get_account_settle_profitloss(
                '0', 'Y',
                (dt.date.today() + dt.timedelta(days=10)).strftime('%Y%m%d'),
                dt.date.today().strftime('%Y%m%d'), self._currency,
                self.fut_account)

    def activate_ca(self, ca_path, ca_passwd, person_id):
        """ activate your ca for trading

        Args: 
            ca_path (str):
                the path of your ca, support both absloutely and relatively path, use same ca with eleader
            ca_passwd (str): password of your ca
            person_id (str): the ca belong which person ID
        """
        res = self._api.activate_ca(ca_path, ca_passwd, person_id)
        return res

    def list_accounts(self):
        """ list all account you have
        """
        return self._api.list_accounts()

    def set_default_account(self, account):
        """ set default account for trade when place order not specific 

        Args:
            account (:obj:Account): 
                choice the account from listing account and set as default
        """
        if isinstance(account, StockAccount):
            self._api.stock_account = account
            self.stock_account = account
        elif isinstance(account, FutureAccount):
            self._api.fut_account = account
            self.fut_account = account

    def get_account_margin(self, currency='NTD', margin_type='1', account={}):
        """ query margin

        Args:    
            currency (str):{NTX, USX, NTD, USD, HKD, EUR, JPY, GBP}
                the margin calculate in which currency
                - NTX: 約當台幣
                - USX: 約當美金
                - NTD: 新台幣
                - USD: 美元
                - HKD: 港幣
                - EUR: 歐元
                - JPY: 日幣
                - GBP: 英鎊
            margin_type (str): {'1', '2'}
                query margin type
                - 1 : 即時
                - 2 : 風險
        """
        account = account if account else self.fut_account
        return self._api.get_account_margin(currency, margin_type, account)

    def get_account_openposition(self,
                                 product_type='0',
                                 query_type='0',
                                 account={}):
        """ query open position

        Args:
            product_type (str): {0, 1, 2, 3}
                filter product type of open position
                - 0: all
                - 1: future
                - 2: option
                - 3: usd base
            query_type (str): {0, 1}
                query return with detail or summary
                - 0: detail
                - 1: summary
        """
        account = account if account else self.fut_account
        return self._api.get_account_openposition(product_type, query_type,
                                                  account)

    def get_account_settle_profitloss(self,
                                      product_type='0',
                                      summary='Y',
                                      start_date='',
                                      end_date='',
                                      currency='',
                                      account={}):
        """ query settlement profit loss

        Args:
            product_type (str): {0, 1, 2}
                filter product type of open position
                - 0: all
                - 1: future
                - 2: option
            summary (str): {Y, N}
                query return with detail or summary
                - Y: summary
                - N: detail
            start_date (str): the start date of query range format with %Y%m%d
                ex: 20180101
            end_date (str): the end date of query range format with %Y%m%d
                ex: 20180201
            currency (str): {NTD, USD, HKD, EUR, CAD, BAS}
                the profit loss calculate in which currency
                - NTD: 新台幣
                - USD: 美元
                - HKD: 港幣
                - EUR: 歐元
                - CAD: 加幣 
                - BAS: 基幣
        """
        account = account if account else self.fut_account
        start_date = start_date if start_date else (
            dt.date.today() + dt.timedelta(days=10)).strftime('%Y%m%d')
        end_date = end_date if end_date else dt.date.today().strftime('%Y%m%d')
        currency = currency if currency else self._currency
        return self._api.get_account_settle_profitloss(
            product_type, summary, start_date, end_date, currency, account)

    def get_stock_account_funds(self, include_tax=' ', account=StockAccount()):
        """ query stock account funds

        Args:
            include_tax (str): {' ', '1'}
                - ' ': tax included
                - '1': tax excluded
        """
        account = account if account else self.stock_account
        return self._api.get_stock_account_funds(include_tax, account)

    def get_stock_account_unreal_profitloss(self,
                                            stock_type='A',
                                            currency='A',
                                            filter_rule=' ',
                                            account=StockAccount()):
        """ query stock account unreal profitloss

        Args: 
            stock_type (str): {A, 0, 1, 2, R}
                - 'A': 全部
                - '0': 現-上市櫃
                - '1': 資
                - '2': 券
                - 'R': 興櫃 
            currency (str): {A, NTD, CNY}
                - A: 全部
                - NTD: 新台幣
                - CNY: 人民幣
            filter_rule (str): {' ', 1, 2, 3} 
                - ' ': default, no filter
                - '1': filter delisting stock
                - '2': tax excluded
                - '3': filter delisting stock and tax excluded
        """
        account = account if account else self.stock_account
        return self._api.get_stock_account_unreal_profitloss(
            stock_type, currency, filter_rule, account)

    def get_stock_account_real_profitloss(self,
                                          stock_type='A',
                                          start_date='',
                                          end_date='',
                                          currency='A',
                                          filter_rule=' ',
                                          account=StockAccount()):
        """ query stock account real profitloss

        Args:
            stock_type (str): {A, 0, 1, 2, R}
                - 'A': 全部
                - '0': 現-上市櫃
                - '1': 資
                - '2': 券
                - 'R': 興櫃 
            start_date (str):
                the start date of query range format with %Y%m%d
                ex: 20180201
            end_date (str):
                the end date of query range format with %Y%m%d
                ex: 20180201
            currency (str): {A, NTD, CNY}
                - A: 全部
                - NTD: 新台幣
                - CNY: 人民幣 
            filter_rule (str): {' ', 1}  
                - ' ': default, no filter
                - '1': filter cost is 0
        """
        account = account if account else self.stock_account
        start_date = start_date if start_date else (
            dt.date.today() + dt.timedelta(days=10)).strftime('%Y%m%d')
        end_date = end_date if end_date else dt.date.today().strftime('%Y%m%d')
        return self._api.get_stock_account_real_profitloss(
            stock_type, start_date, end_date, currency, filter_rule, account)

    def place_order(self, contract, order):
        """ placing order

        Args:
            contract (:obj:Shioaji.Contract):
            order (:obj:Shioaji.Order):
                pass Shioaji.Order object to place order
        """
        if not order.account:
            if isinstance(contract, Future) or isinstance(contract, Option):
                order._account = self.fut_account
            elif isinstance(contract, Stock):
                order._account = self.stock_account
            else:
                log.error('Please provide the account place to.')
                return None
        trade = self._api.place_order(contract, order)
        return trade

    def update_order(self, trade, price=None, qty=None):
        """ update the order price or qty

        Args:
            trade (:obj:Trade):
                pass place_order return Trade object to update order
            price (float): the price you want to replace
            qty (int): the qty you want to subtract
        """
        trade = self._api.update_order(trade, price, qty)
        return trade

    def cancel_order(self, trade):
        """ cancel order
        trade: Trade
        """
        trade = self._api.cancel_order(trade)
        return trade

    def update_status(self):
        """ update status of all trades you have

        """
        self._api.update_status()

    def list_trades(self):
        """ list all trades
        """
        return self._api.trades
