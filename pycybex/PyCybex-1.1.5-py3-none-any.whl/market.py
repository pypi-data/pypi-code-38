from bitshares.market import Market as BitsharesMarket
from bitshares.price import Price as BitsharesPrice
from bitshares.amount import Amount as BitsharesAmount
from bitshares.account import Account as BitsharesAccount
from bitshares.utils import formatTime, formatTimeFromNow
from . import cybex_operations

class Kline(dict):
    def __init__(self, d, instance):
        self['base'] = instance.rpc.get_asset(d['key']['base'])
        self['quote'] = instance.rpc.get_asset(d['key']['quote'])
        for i in ['open', 'close', 'high', 'low']:
            for j in ['Base', 'Quote']:
                self['{}{}Volume'.format(i, j)] = BitsharesAmount(
                    amount = int(d['{}_{}'.format(i, j.lower())]),
                    asset = self[j.lower()],
                    bitshares_instance = instance
                )
            self['{}Price'.format(i)] = BitsharesPrice(
                base = self['{}BaseVolume'.format(i)],
                quote = self['{}QuoteVolume'.format(i)],
                bitshares_instance = instance)

class Market(BitsharesMarket):
    def __init__(
        self,
        *args,
        base = None,
        quote = None,
        cybex_instance = None,
        **kwargs
    ):
        if 'rte' in kwargs and isinstance(kwargs['rte'], bool):
            self.is_rte = kwargs['rte'] 
        else:
            self.is_rte = False

        super(Market, self).__init__(args = args, base = base, quote = quote, bitshares_instance = cybex_instance)

    def get_market_history(
        self,
        bucket_seconds,
        start,
        end
    ):
        return [Kline(d, self.bitshares) 
                for d in self.bitshares.rpc.get_market_history(
                self['base']['id'],
                self['quote']['id'],
                bucket_seconds,
                formatTime(start),
                formatTime(end),
                api = 'history'
            )]

    def get_fill_order_history(
        self,
        limit = 100):
        return self.bitshares.rpc.get_fill_order_history(
                self['base']['id'],
                self['quote']['id'],
                limit,
                api = 'history'
            )

    def buy(
        self,
        price,
        amount,
        expiration=None,
        killfill=False,
        account=None,
        returnOrderId=False,
        **kwargs
        ):
        """ Places a buy order in a given market

            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to buy
            :param number expiration: (optional) expiration time of the order in seconds (defaults to 7 days)
            :param bool killfill: flag that indicates if the order shall be killed if it is not filled (defaults to False)
            :param string account: Account name that executes that order
            :param string returnOrderId: If set to "head" or "irreversible" the call will wait for the tx to appear in
                                        the head/irreversible block and add the key "orderid" to the tx output

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reversed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTC.
                That way you can multiply prices with `1.05` to get a +5%.

            .. warning::

                Since buy orders are placed as
                limit-sell orders for the base asset,
                you may end up obtaining more of the
                buy asset than you placed the order
                for. Example:

                    * You place and order to buy 10 USD for 100 BTS/USD
                    * This means that you actually place a sell order for 1000 BTS in order to obtain **at least** 10 USD
                    * If an order on the market exists that sells USD for cheaper, you will end up with more than 10 USD
        """
        if not expiration:
            expiration = self.bitshares.config["order-expiration"]
        if not account:
            if "default_account" in self.bitshares.config:
                account = self.bitshares.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = BitsharesAccount(account, bitshares_instance=self.bitshares)

        if isinstance(price, BitsharesPrice):
            price = price.as_base(self["base"]["symbol"])

        if isinstance(amount, BitsharesAmount):
            amount = BitsharesAmount(amount, bitshares_instance=self.bitshares)
            assert(amount["asset"]["symbol"] == self["quote"]["symbol"]), \
                "Price: {} does not match amount: {}".format(
                    str(price), str(amount))
        else:
            amount = BitsharesAmount(amount, self["quote"]["symbol"], bitshares_instance=self.bitshares)

        if 'rte_buy' in kwargs and kwargs['rte_buy']:
            extensions = [[7, {'is_buy': True}]]
        else:
            extensions = []

        order = cybex_operations.Limit_order_create(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "seller": account["id"],
            "amount_to_sell": {
                "amount": int(float(amount) * float(price) * 10 ** self["base"]["precision"]),
                "asset_id": self["base"]["id"]
            },
            "min_to_receive": {
                "amount": int(float(amount) * 10 ** self["quote"]["precision"]),
                "asset_id": self["quote"]["id"]
            },
            "expiration": formatTimeFromNow(expiration),
            "fill_or_kill": killfill,
            "extensions": extensions
        })

        if returnOrderId:
            # Make blocking broadcasts
            prevblocking = self.bitshares.blocking
            self.bitshares.blocking = returnOrderId

        tx = self.bitshares.finalizeOp(order, account["name"], "active")

        if returnOrderId:
            tx["orderid"] = tx["operation_results"][0][1]
            self.bitshares.blocking = prevblocking
        if not self.is_rte:
            return tx

        return {'tx': tx, 'txid': self.bitshares.tx().tx.id}

    def sell(
        self,
        price,
        amount,
        expiration=None,
        killfill=False,
        account=None,
        returnOrderId=False,
        **kwargs
        ):
        """ Places a sell order in a given market

            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to sell
            :param number expiration: (optional) expiration time of the order in seconds (defaults to 7 days)
            :param bool killfill: flag that indicates if the order shall be killed if it is not filled (defaults to False)
            :param string account: Account name that executes that order
            :param string returnOrderId: If set to "head" or "irreversible" the call will wait for the tx to appear in
                                        the head/irreversible block and add the key "orderid" to the tx output

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reversed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTC.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        if not expiration:
            expiration = self.bitshares.config["order-expiration"]
        if not account:
            if "default_account" in self.bitshares.config:
                account = self.bitshares.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = BitsharesAccount(account, bitshares_instance=self.bitshares)
        if isinstance(price, BitsharesPrice):
            price = price.as_base(self["base"]["symbol"])

        if isinstance(amount, BitsharesAmount):
            amount = BitsharesAmount(amount, bitshares_instance=self.bitshares)
            assert(amount["asset"]["symbol"] == self["quote"]["symbol"]), \
                "Price: {} does not match amount: {}".format(
                    str(price), str(amount))
        else:
            amount = BitsharesAmount(amount, self["quote"]["symbol"], bitshares_instance=self.bitshares)

        if 'rte_buy' in kwargs and kwargs['rte_buy']:
            extensions = [[7, {'is_buy': True}]]
        else:
            extensions = []

        order = cybex_operations.Limit_order_create(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "seller": account["id"],
            "amount_to_sell": {
                "amount": int(float(amount) * 10 ** self["quote"]["precision"]),
                "asset_id": self["quote"]["id"]
            },
            "min_to_receive": {
                "amount": int(float(amount) * float(price) * 10 ** self["base"]["precision"]),
                "asset_id": self["base"]["id"]
            },
            "expiration": formatTimeFromNow(expiration),
            "fill_or_kill": killfill,
            "extensions": extensions
        })

        if returnOrderId:
            # Make blocking broadcasts
            prevblocking = self.bitshares.blocking
            self.bitshares.blocking = returnOrderId

        tx = self.bitshares.finalizeOp(order, account["name"], "active")

        if returnOrderId:
            tx["orderid"] = tx["operation_results"][0][1]
            self.bitshares.blocking = prevblocking

        if not self.is_rte:
            return tx

        return {'tx': tx, 'txid': self.bitshares.tx().tx.id}
