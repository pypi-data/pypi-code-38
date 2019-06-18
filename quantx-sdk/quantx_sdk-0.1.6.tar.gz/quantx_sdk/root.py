from quantx_sdk.project import Project
from quantx_sdk.algorithm import Algorithm
from quantx_sdk.backtest_result import BacktestResult


class Root:
    def __init__(self, qx):
        self.qx = qx

    def current_rate_limit(self):
        """レートリミット取得

        現在のレートリミット情報を取得します。

        Returns
        -------
        dict

        Examples
        --------
        >>> ret = api.current_rate_limit()
        >>> limit = ret["limit"] # リミット値
        >>> remaining = ret["remaining"] # 残り呼び出し回数

        """
        return self.qx.current_rate_limit()

    def projects(self, option={}):
        """プロジェクト一覧取得

        自分が開発中のプロジェクトの一覧を取得します。

        Parameters
        ----------
        option : dict
            将来の拡張用です。

        Returns
        -------
        list
            quantx_sdk.Projectのリストです。
        """
        result = self.qx.api("/user/project/list", option)
        projects = result["result"]["projects"]
        return [Project(self.qx, p["hash"], p) for p in projects]

    def new_project(self, name):
        """新規プロジェクト作成

        新しいプロジェクトを作成します。

        Parameters
        ----------
        name : str
            プロジェクト名

        Returns
        -------
        quantx_sdk.Project
        """
        result = self.qx.api("/user/project/create", {"name": name})
        project_hash = result["result"]["hash"]
        return Project(self.qx, project_hash, {"name": name})

    def project(self, project_hash):
        """プロジェクト取得

        指定したhashのプロジェクトを取得します。

        Parameters
        ----------
        project_hash: str
            プロジェクトハッシュ

        Returns
        -------
        quantx_sdk.Project
        """
        return Project(self.qx, project_hash)

    def algorithms(self, option={}):
        """アルゴリズム一覧取得

        自分で作ったアルゴリズムでLIVE状態のもの、
        購読中・トライアル中のアルゴリズムを一覧で返します。

        Parameters
        ----------
        option: dict
            将来の拡張用です。

        Returns
        -------
        list
            quantx_sdk.Algorithmのリストです。
        """
        result = self.qx.api("/user/live/list", option)
        algorithms = []
        for a in result["result"]:
            algorithms.append(
                Algorithm(self.qx, a["name"], a["origin"], a["owner"], a["live_hash"])
            )
        return algorithms

    def algorithm(self, live_hash):
        """Liveアルゴリズム取得

        指定されたlive_hashのアルゴリズムオブジェクトを取得します。

        Parameters
        ----------
        live_hash: str
            アルゴリズムのハッシュ値

        Returns
        -------
        quantx_sdk.Algorithm
            アルゴリズムオブジェクト
        """
        return Algorithm(self.qx, "", "", "", live_hash)

    def backtest_result(self, backtestid):
        """バックテスト結果取得

        指定されたbacktestidのバックテスト結果オブジェクトを取得します。

        Parameters
        ----------
        backtestid: str
            バックテストID

        Returns
        -------
        quantx_sdk.BacktestResult
            バックテスト結果オブジェクト
        """
        return BacktestResult(self.qx, backtestid, 0, "")
