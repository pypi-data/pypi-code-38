import pandas as pd
from quantx_sdk.util import Util


class BacktestResult:
    """
    バックテスト結果、バックテストの内容を管理します。
    """

    def __init__(self, qx, backtestid, status, updated_at):
        self.qx = qx
        self.backtestid = backtestid
        self.status = status
        self.updated_at = updated_at
        self._detail = None
        self._log = None
        self._result = None

    def _get_detail(self):
        if not self._detail:
            result = self.qx.api("/backtest/{}/detail".format(self.backtestid))
            self._detail = result["result"]
        return self._detail

    def _get_log(self):
        if not self._log:
            result = self.qx.api("/backtest/{}/log".format(self.backtestid))
            self._log = result["result"]
        return self._log

    def _status(self):
        if not self._result:
            status_opts = {"attrs": ["master", "data", "sim"], "lng": "en"}
            path = "/backtest/{}/status".format(self.backtestid)
            self._result = self.qx.api(path, param=status_opts)["result"]
        return self._result

    def _get_history(self, name):
        dims = self._status()["sim"]["history_dims"]
        index = dims.index(name)
        return self._status()["sim"]["history"][index]

    def summary(self):
        """サマリーを取得します。

        ReturnValue, ReturnRatio等を取得します。

        Returns
        -------
        dict
             バックテストサマリ
        """
        indicators = self._status()["sim"]["indicator"]

        # 他、計算で出す値
        # see: StCodingBacktest.vue summary() function

        # 取引機会数
        indicators["TradingDays"] = len(self._status()["sim"]["history"][0])

        # 損益
        indicators["ReturnValue"] = self._get_history("portfolio_value")[-1]

        # 損益率
        indicators["ReturnRatio"] = "{:.3}".format(
            self._get_history("returns")[-1] * 100.0
        )

        # シグナル回数
        txnCount = 0
        for k, v in self._status()["sim"]["assets"].items():
            if k == "history_dims":
                continue
            if "history" in v:
                txnCount += len(v["history"])
        indicators["SignalCount"] = txnCount

        return indicators

    def benchmark(self):
        """損益率推移を取得します。

        Returns
        -------
        pandas.DataFrame
        """
        st = self._status()
        df = pd.DataFrame(
            st["sim"]["history"],
            index=st["sim"]["history_dims"],
            columns=st["data"]["dates"],
        ).T
        columns = [
            "portfolio_value",
            "cash",
            "positions_value",
            "returns",
            "pnl",
            # 'positions', 'open_order_list', 'complete_order_list',
            "portfolio_daily_returns",
            "benchmark",
            "benchmark_cumulative_returns",
            "benchmark_daily_returns",
            "portfolio_cumulative_returns",
        ]
        df = df[columns]
        df = df.reset_index()
        df = Util.convert_df(df, date_columns=["index"], number_columns=columns)
        df = df.set_index(["index"])
        return df

    def symbol_summary(self):
        """銘柄毎サマリを取得します。

        Returns
        -------
        pandas.DataFrame
        """
        st = self._status()
        df = pd.DataFrame(st["master"]["data"], columns=st["master"]["dims"])
        df.set_index("symbol")

        # 銘柄ごとのバックテスト結果をマージする
        columns = ["txn_count", "position_count", "valuation", "return"]
        data = []
        assets = st["sim"]["assets"]
        for symbol in df["symbol"]:
            if symbol not in assets:
                data.append([None for c in columns])
                continue
            row = []
            a = assets[symbol]
            # 取引回数
            if "history" in a:
                row.append(len(a["history"]))
            else:
                row.append(0)

            # 保有数
            row.append(a["amount"])

            # 時価総額
            row.append(a["current_price"] * a["amount"])

            # 損益
            row.append(
                (a["current_price"] * a["amount"])
                + a["total_sell_price"]
                - a["total_buy_price"]
            )
            data.append(row)

        df = df.merge(
            pd.DataFrame(data, columns=columns, index=df.index),
            left_index=True,
            right_index=True,
        )

        return Util.convert_df(
            df,
            date_columns=[],
            number_columns=["txn_count", "position_count", "valuation", "return"],
        )

    def signal_history_by_symbol(self, symbol):
        """シグナル履歴取得

        Parameters
        ----------
        symbol: str
            対象銘柄

        Returns
        -------
        pandas.DataFrame
             対象銘柄のシグナル履歴
        """

        status_opts = {"attrs": [ "data", "data-%s" % symbol], "lng": "en"}
        path = "/backtest/{}/status".format(self.backtestid)
        result = self.qx.api(path, param=status_opts)["result"]

        items = result["data"]["items"]
        dates = result["data"]["dates"]
        df = pd.DataFrame(data=result["data-%s" % symbol], columns=dates, index=items)
        return df.T

    def trade_history_by_symbol(self, symbol):
        """銘柄別取引一覧

        Parameters
        ----------
        symbol: str
            対象銘柄

        Returns
        -------
        pandas.DataFrame
             対象銘柄の取引履歴
        """
        st = self._status()
        if symbol not in st["sim"]["assets"]:
            return None
        df = pd.DataFrame(
            st["sim"]["assets"][symbol]["history"],
            columns=st["sim"]["assets"]["history_dims"],
        )
        df = Util.convert_df(
            df,
            date_columns=["order_date", "complete_date"],
            number_columns=["price", "amount", "comission"],
        )
        return df

    def sim_history(self):
        """バックテスト結果の時系列データを返します

        Returns
        -------
        pandas.DataFrame
             シミュレーション結果の時系列データ
        """
        sim = self._status()["sim"]
        dims = sim["history_dims"]
        df = pd.DataFrame(sim["history"], index=dims, columns=sim["dates"])
        return df.T

    def source(self):
        """このバックテストのソースコードを取得します。

        Returns
        -------
        str
            ソースコード文字列
        """
        return self._get_detail()["seed"]["src"]

    def log(self):
        """このバックテストのログを取得します。

        Returns
        -------
        list
            ログ(dict)のリスト
        """
        return self._get_log()

    def params(self):
        """このバックテストのパラメータを取得します。

        Returns
        -------
        dict
            バックテストパラメータ
        """
        return self._get_detail()["seed"]["bt"]

    def to_dict(self):
        """バックテスト結果をdictに変換します。

        Returns
        -------
        dict
        """
        return {
            "status": self.status,
            "hash": self.backtestid,
            "updated_at": self.updated_at,
        }
