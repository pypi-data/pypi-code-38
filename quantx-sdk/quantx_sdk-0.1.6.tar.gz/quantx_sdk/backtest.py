
import websocket
import threading
import time
import json
import datetime
import pytz
from logging import getLogger
from quantx_sdk.backtest_result import BacktestResult


class Backtest:
    """
    バックテストオブジェクト
    バックテスト結果へのアクセスを管理します。
    """

    def __init__(self, qx, project_hash, option):
        self.logger = getLogger(__name__)
        self.qx = qx
        self.option = option
        self.project_hash = project_hash
        self.backtestid = None
        self.backtest_status = None
        self.outputHandler = None
        self.thread = threading.Thread(target=self._start)
        self.stop_event = threading.Event()
        self.backtest_error = None
        self.thread.start()

    def _run(self):
        path = "/src/{}/run".format(self.project_hash)
        result = self.qx.api(path, param=self.option)
        return result["result"]

    def _start(self):
        bt = self._run()
        self.backtestid = bt["hash"]
        self.backtest_status = bt["status"]
        if int(bt["status"]) < 100:
            self._connect_websocket(self.backtestid)

    def join(self, handler=None):
        """バックテスト完了を待ちます。

        戻り値は、BacktestResultインスタンスです。
        handlerは、バックテスト進行ログの受け取り関数です。
        バックテストの進行ログがリアルタイムで受け取れます。
        引数は2つで第1引数は、ログ出力日付、第2引数はメッセージです。

        >>> backtest.join(lambda date, message: print(date, message))

        バックテスト実行が正常に終了したかどうかは、

        >>> backtest.completed()

        で取得が可能です。
        また、バックテストが失敗した場合、エラー内容は

        >>> backtest.get_error()

        で取得が可能です。


        Parameters
        ----------
        handler: func
            ログ出力用関数

        Returns
        -------
        quantx_sdk.BacktestResult

        Example
        -------
        >>> res = backtest.join(lambda date, message: print(date, message))
        >>> if not backtest.completed():
        >>>    print(backtest.get_error())
        >>>    return
        >>> print(res.summary())
        """
        self.outputHandler = handler
        self.thread.join()
        return BacktestResult(self.qx, self.backtestid, self.backtest_status, None)

    def _connect_websocket(self, backtestid, timeout=30):
        def now():
            n = datetime.datetime.now(pytz.utc)
            n = n - datetime.timedelta(microseconds=n.microsecond)
            return n.isoformat()

        def debug(message):
            self.logger.debug(message)

        def info(date, message):
            self.logger.info(message)
            if self.outputHandler:
                self.outputHandler(date, message)

        def error(message):
            self.logger.error(message)
            if self.outputHandler:
                self.outputHandler(now(), message)

        def on_open(ws):
            debug("websocket open")

            def run():
                for i in range(0, timeout):
                    if self.stop_event.is_set():
                        return
                    time.sleep(1)
                info(now(), "timeout websocket")
                self.backtest_error = "timeout"
                ws.close()

            threading.Thread(target=run).start()

        def on_message(ws, message):
            debug("websocket message: {}".format(message))
            obj = json.loads(message)
            type = obj["type"]

            if type == "error":
                self.backtest_error = obj["ename"]
                error(
                    "websocket error message: {} {}".format(obj["ename"], obj["evalue"])
                )
                if len(obj["stack"]["raw"]):
                    error("\n".join(obj["stack"]["raw"]))
                self.stop_event.set()
                ws.close()
            else:
                info(obj["date"], obj["msg"])
                if type == "status":
                    status = int(obj["status"])
                    self.backtest_status = status
                    if status >= 100:
                        self.stop_event.set()
                        ws.close()

        def on_error(ws, error):
            error("websocket error: {}".format(error))
            self.backtest_error = error

        def on_close(ws):
            debug("close websocket")

        url = self.qx.WEBSOCKET_ENTRY_POINT + "/backtest/" + backtestid
        debug("connect websocket: " + url)
        ws = websocket.WebSocketApp(
            url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever()

    def completed(self):
        """バックテストが正常終了したかを取得します。

        Returns
        -------
        bool
        """
        return self.backtest_error == None

    def get_error(self):
        """バックテストのエラーメッセージを取得します。

        バックテストが正常に終了した場合、None返ります。

        Returns
        -------
        str
        """
        return self.backtest_error
