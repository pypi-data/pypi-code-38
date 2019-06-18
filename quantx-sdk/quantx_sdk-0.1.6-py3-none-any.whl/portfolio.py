import pandas as pd
from quantx_sdk.util import Util


class Portfolio:
    """
    ポートフォリオを管理します。
    """

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def summary(self):
        """サマリーを取得します。

        Returns
        -------
        dict
        """
        latest = self.portfolio["latest"].copy()
        del latest["positions"]
        del latest["open_order_list"]
        del latest["complete_order_list"]
        return latest

    def positions(self):
        """ポジションを取得します。

        Returns
        -------
        pandas.DataFrame
        """
        latest = self.portfolio["latest"]
        columns = [
            "symbol",
            "total_buy_price",
            "value",
            "amount",
            "position_ratio",
            "buy_price",
            "sell_price",
            "max_returns",
            "returns",
            "portfolio_ratio",
            "total_sell_price",
            "pnl",
        ]

        data = []
        for symbol in sorted(latest["positions"].keys()):
            row = [symbol]
            d = latest["positions"][symbol]
            row.extend([d[c] for c in columns[1:]])
            data.append(row)
        df = pd.DataFrame(data, columns=columns)
        df = df.set_index(["symbol"])
        df = Util.convert_df(df, date_columns=[], number_columns=df.columns)
        return df

    def orders(self):
        """取引履歴を取得します。

        Returns
        -------
        pandas.DataFrame
        """
        latest = self.portfolio["latest"]
        columns = [
            "stock_name",
            "signal_date",
            "trade_date",
            "position_valuation",
            "pos",
            "neg",
            "comment",
        ]
        data = [o for o in reversed(latest["open_order_list"])]
        data.extend([o for o in reversed(latest["complete_order_list"])])
        df = pd.DataFrame(data, columns=columns)
        df = Util.convert_df(
            df,
            date_columns=["signal_date", "trade_date"],
            number_columns=["position_valuation", "pos", "neg"],
        )
        return df

    def trends(self):
        """トレンドを取得します。

        Returns
        -------
        pandas.DataFrame
        """
        dates = self.portfolio["dates"]
        columns = ["date", "portfolio_cumulative_return", "benchmark_cumulative_return"]
        data = []
        for i, v in enumerate(dates):
            data.append(
                [
                    v,
                    self.portfolio["portfolio_cumulative_returns"][i],
                    self.portfolio["benchmark_cumulative_returns"][i],
                ]
            )
        df = pd.DataFrame(data, columns=columns)
        df = Util.convert_df(
            df,
            date_columns=["date"],
            number_columns=[
                "portfolio_cumulative_return",
                "benchmark_cumulative_return",
            ],
        )
        df = df.set_index("date")
        return df
