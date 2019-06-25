from abc import abstractmethod
from queue import Queue, Empty

from api.handler.outputer.IBaseOutputer import IBaseOutputer
from client import ServiceInnerException
from factdatasource import FactDatasourceProxyService
from schedule.utils.log import FrameworkHandlerLogger


class IBatchOutputer(IBaseOutputer):

    @abstractmethod
    def get_batch_size(self) -> int:
        """
        获取一次批量任务数量
        :return:
        """

    def batch_output(self, code, output_fd_codes, is_finished, output_stream: Queue):
        """
        批量发送任务出去
        :param code:
        :param output_fd_codes:
        :param is_finished:
        :param output_stream:
        :return:
        """
        insert_cache = {}
        update_cache = {}
        upsert_cache = {}

        while not is_finished[0] or not output_stream.empty():

            if self.is_killed():
                FrameworkHandlerLogger.log_warn(f"{code} 任务被强制停止,取消数据输出")
                return

            try:
                poll = output_stream.get(timeout=1)
            except Empty:
                # 表示这个任务为null,不处理
                continue

            output_fd = self.find_output_fd(output_fd_codes, poll.index())
            # 把输出放入缓存中
            self.put_in_cache(code, insert_cache, update_cache, upsert_cache, output_fd, poll)

            # 清空批量任务
            try:
                serializables = insert_cache.get(output_fd)
                if serializables is not None and len(serializables) >= self.get_batch_size():
                    FactDatasourceProxyService.fd_client_proxy().inserts(output_fd, serializables)
                    serializables.clear()

                serializables = update_cache.get(output_fd)
                if serializables is not None and len(serializables) >= self.get_batch_size():
                    FactDatasourceProxyService.fd_client_proxy().updates(output_fd, serializables)
                    serializables.clear()

                serializables = upsert_cache.get(output_fd)
                if serializables is not None and len(serializables) >= self.get_batch_size():
                    FactDatasourceProxyService.fd_client_proxy().save_or_updates(output_fd, serializables)
                    serializables.clear()
            except Exception as e:
                raise ServiceInnerException(f"执行失败,Code: {code}的执行器,保存数据发生错误:{str(e)}")

        # 把剩余的任务清空了
        self.flush_cache(code, insert_cache, update_cache, upsert_cache)
        # 到这来了 就表示是完成了
        return
