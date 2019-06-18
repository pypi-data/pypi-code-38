from logging import getLogger

from jinja2 import Template
from quantx_sdk.backtest import Backtest
from quantx_sdk.backtest_result import BacktestResult


class Project:
    """
    プロジェクトオブジェクト
    プロジェクトの情報取得・各種更新を管理します。
    """

    def __init__(self, qx, project_hash, ext={}):
        self.logger = getLogger(__name__)
        self.qx = qx
        self.project_hash = project_hash
        self.ext = ext
        self.projectInfo = None

    def _load_project(self):
        if not self.projectInfo:
            path = "/src/{}/get".format(self.project_hash)
            result = self.qx.api(path)
            res = result["result"]
            self.projectInfo = res
        return self.projectInfo

    def source(self):
        """ソースコードを取得します。

        Returns
        -------
        str
            ソースコード文字列
        """
        pi = self._load_project()
        return pi["src"]

    def upload_source(self, source):
        """ソースコードを更新します。

        プロジェクトのソースコードを引数の文字列で上書きします。

        Parameters
        ----------
        source : str
            ソースコード文字列
        """
        pi = self._load_project()
        return self._update(source, pi["bt"])

    def upload_source_file(self, file):
        """指定したファイル内容でソースコードを更新します。

        ファイル内容でプロジェクトのソースコードを上書きします。

        Parameters
        ----------
        file : str
            ソースコードファイル
        """
        return self.upload_source(open(file).read())

    def update_default_backtest_params(self, params):
        """デフォルトのバックテストパラメータを更新します。

        Parameters
        ----------
        params : dict

        Examples
        --------
        >>> project.update_default_backtest_params({
            "engine": "maron-0.0.1b", # エンジン
            "from_date": "2017-01-01", # バックテスト開始日
            "to_date": "2017-12-31", # バックテスト終了日
            "capital_base": 10000000 # 初期資金
        })
        """
        pi = self._load_project()
        return self._update(pi["src"], params)

    def current_backtest_params(self):
        """現在のバックテストパラメータを取得します。

        Returns
        -------
        dict
            現在設定されているバックテストパラメータ

        Examples
        --------
        >>> project.current_backtest_params()
        {
            "engine": "maron-0.0.1b", # エンジン
            "from_date": "2017-01-01", # バックテスト開始日
            "to_date": "2017-12-31", # バックテスト終了日
            "capital_base": 10000000 # 初期資金
        }
        """
        pi = self._load_project()
        return pi["bt"]

    def _update(self, source, bt):
        pi = self._load_project()
        path = "/user/project/{}/save".format(self.project_hash)
        bt = self._merge_bt(bt)
        result = self.qx.api(
            path,
            {
                "name": pi["algo_name"],
                "description": pi["algo_desc"],
                "features": pi["algo_features"],
                "features_detail": pi["algo_features_detail"],
                "src": source,
                "bt": bt,
                "share_status": pi["share_status"],
            },
        )
        self.projectInfo["src"] = source
        self.projectInfo["bt"] = bt
        return result

    def _merge_bt(self, params):
        bt = self.current_backtest_params().copy()
        bt.update(params)
        return bt

    def backtest(self, params={}, tpl_params={}):
        """バックテスト実行

        バックテストを実行します。
        バックテストは非同期で実行されます。
        戻り値はBacktestオブジェクトです。
        バックテスト完了を待つ場合、バックテストオブジェクトのjoin()メソッドを呼び出してください。

        Parameters
        ----------
        params : dict
            バックテストパラメータ。
            update_default_backtest_params()の引数、
            current_backtest_params()の戻り値と同じ形式で指定してください。
            この指定はこのバックテストでのみ有効です。
            プロジェクトの設定は変更されません。

        Returns
        -------
        quantx_sdk.Backtest
            バックテストオブジェクト

        Examples
        --------
        >>> backtest = project.backtest({"capital_base": 10000000})
        >>> res = bacttest.join()
        """
        src = self.source()

        if tpl_params:
            src = Template(src).render(tpl_params)
        
        bt = self._merge_bt(params)
        option = {"bt": bt, "lang": "python", "level": "full", "lng": "en", "src": src}
        return Backtest(self.qx, self.project_hash, option)

    def backtests(self):
        """過去に行ったバックテストの一覧を取得します。

        Returns
        -------
        list
            quantx_sdk.BacktestResultのリスト
        """
        result = self.qx.api("/user/project/" + self.project_hash + "/backtests")
        backtests = []
        for b in result["result"]:
            backtests.append(
                BacktestResult(self.qx, b["hash"], b["status"], b["updated_at"])
            )
        return backtests

    def to_dict(self):
        """プロジェクト情報をdictに変換します。

        Returns
        -------
        dict
        """
        if self.projectInfo:
            pi = self.projectInfo
            return {"name": pi["algo_name"], "hash": self.project_hash}
        else:
            return {"name": self.ext.get("name"), "hash": self.project_hash}
