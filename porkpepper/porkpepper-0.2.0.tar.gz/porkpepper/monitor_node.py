import asyncio
import aioredis
from .result import Result
from .websocket_session import WebsocketSession
from .design import WebsocketNode
from .redis_server import RedisServer


class MonitorRedisServer(RedisServer):
    MAX_DB_COUNT = 0

    def info_arguments(self):
        arguments = super(MonitorRedisServer, self).info_arguments()
        arguments.update(porkpepper_mode="monitor")
        return arguments

    async def info(self, session):
        info_arguments = self.info_arguments()
        info = self.INFO_TEMPLATE.render(info_arguments)
        return Result(info)


class SimpleMonitorNode(WebsocketNode):
    MONITOR_TASK_LIST = list()
    TIMER_INTERVAL = 5
    NODE_URL_LIST = list()

    def __init__(self, websocket_path="/monitor"):
        super(SimpleMonitorNode, self).__init__(
            session_class=WebsocketSession,
            websocket_path=websocket_path,
            redis_server=MonitorRedisServer
        )

    async def monitor_task(self, node_url):
        while True:
            connectivity = False
            conn = None
            info = None
            try:
                conn = await aioredis.create_redis(node_url, timeout=1)
                info = await conn.info()
                connectivity = True
            except asyncio.CancelledError:
                return
            except Exception as e:
                connectivity = False
            finally:
                if conn is not None:
                    conn.close()
            message = {
                    "type": "monitorNodeStatus",
                    "nodeUrl": node_url,
                    "connectivity": connectivity,
                    "info": info,
                }
            app = self._http_app
            if app is not None:
                all_sessions = self._http_app.all_sessions()
                send_list = [session.send(message) for session in all_sessions]
                if send_list:
                    asyncio.ensure_future(asyncio.gather(*send_list))
            await asyncio.sleep(self.TIMER_INTERVAL)

    def cancel_monitor_tasks(self):
        task_list = self.MONITOR_TASK_LIST
        for task in task_list:
            task.cancel()
        task_list.clear()

    async def on_start(self):
        self.cancel_monitor_tasks()
        monitor_tasks = [asyncio.create_task(self.monitor_task(node_url)) for node_url in self.NODE_URL_LIST]
        self.MONITOR_TASK_LIST.extend(monitor_tasks)

    async def on_shutdown(self):
        self.cancel_monitor_tasks()


__all__ = ["SimpleMonitorNode", ]
