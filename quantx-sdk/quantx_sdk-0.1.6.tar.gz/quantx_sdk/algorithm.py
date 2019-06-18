from quantx_sdk.portfolio import Portfolio
import pandas as pd
from quantx_sdk.util import Util


class Algorithm:
    """
    アルゴリズム情報を管理します。
    """

    def __init__(self, qx, name, origin, owner, live_hash):
        self.qx = qx
        self.name = name
        self.origin = origin
        self.owner = owner
        self.live_hash = live_hash
        self._data = None

    def _get(self):
        if not self._data:
            path = "/live/{}".format(self.live_hash)
            result = self.qx.api(path, {"fetch": "full"})
            self._data = result["result"]
        return self._data

    def signals(self, from_date=None, to_date=None):
        """シグナル情報を取得します。

        取得期間を指定しない場合、最新のシグナルが最大1000件返ります。
        一度に取得できる件数の上限は1000件です。
        期間を指定していても、1000件を超える場合、1000件のみが返ります。

        Parameters
        ----------
        from_date : str
            取得開始日。 YYYY-MM-DD フォーマットで指定。
        to_date: str
            取得終了日。 YYYY-MM-DD フォーマットで指定。

        Returns
        -------
        pandas.DataFrame
            シグナル一覧
        """
        result = self.qx.api(
            "/signal/list",
            {"hashes": [self.live_hash], "from": from_date, "to": to_date},
        )

        data = []
        if self.live_hash in result["result"]:
            data = result["result"][self.live_hash]
        columns = ["target_date", "symbol", "pos", "neg", "order_num", "order_comment"]
        rows = [[d[c] for c in columns] for d in data]
        df = pd.DataFrame(rows, columns=columns)
        df = Util.convert_df(
            df, date_columns=["target_date"], number_columns=["pos", "neg", "order_num"]
        )
        return df

    def info(self):
        """アルゴリズム情報を取得します。

        Returns
        -------
        dict
            アルゴリズム情報
        """
        data = self._get()
        info = data["algorithm_info"]
        for k, v in data["bt"].items():
            info[k] = v
        return info

    def summary(self):
        """サマリーを取得します。

        アルゴリズムのMaxDrawdown,Volatility,SharpeRatio等を取得します。

        Returns
        -------
        dict
            アルゴリズム情報
        """
        data = self._get()
        indicators = data["indicator"]
        indicators["TradingDays"] = data["trading_days"]
        indicators["TradedCount"] = data["traded_count"]
        return indicators

    def symbols(self):
        """銘柄一覧を取得します。

        Returns
        -------
        pandas.DataFrame
            銘柄コードがindexのDataFrame。
        """
        data = self._get()
        columns = ["symbol", "name", "sector"]
        rows = []
        for k in sorted(data["master"].keys()):
            d = data["master"][k]
            rows.append([d[c] for c in columns])
        df = pd.DataFrame(rows, columns=columns)
        df = df.set_index("symbol")
        return df

    def orders(self):
        """取引履歴を取得します。

        Returns
        -------
        pandas.DataFrame
            取引履歴
        """
        data = self._get()
        columns = [
            "stock_name",
            "signal_date",
            "trade_date",
            "position_valuation",
            "pos",
            "neg",
            "comment",
        ]
        rows = [o for o in reversed(data["open_orders"])]
        for orders in reversed(data["complete_orders"]):
            rows.extend([o for o in reversed(orders)])
        df = pd.DataFrame(rows, columns=columns)
        df = Util.convert_df(
            df,
            date_columns=["signal_date", "trade_date"],
            number_columns=["position_valuation", "pos", "neg"],
        )
        return df

    def product(self):
        """商品情報を取得します。

        Returns
        -------
        dict
            商品情報
        """
        return self._get().get("product", {})

    def seller(self):
        """販売者を取得します。

        Returns
        -------
        dict
            販売者情報
        """
        return self._get().get("seller", {})

    def portfolio(self, type=None):
        """ポートフォリオを取得します。

        Returns
        -------
        quantx_sdk.Portfolio
            ポートフォリオオブジェクト
        """
        key = "portfolio"
        if type:
            key += "_" + type
        return Portfolio(self._get()[key])

    def to_dict(self):
        """アルゴリズム情報をdictに変換します。

        Returns
        -------
        dict
        """
        return {
            "name": self.name,
            "origin": self.origin,
            "owner": self.owner,
            "hash": self.live_hash,
        }
