from api.exceptions import IllegalArgumentException, ServiceInnerException
from api.model import OutputWrapper
from factdatasource import FactDatasourceProxyService
from schedule.utils.log import FrameworkHandlerLogger


class IBaseOutputer:

    def put_in_cache(self, code, insert_cache: dict, update_cache, upsert_cache, output_fd, poll: OutputWrapper):
        """
        把数据放入缓存中
        :param code:
        :param insert_cache:
        :param update_cache:
        :param upsert_cache:
        :param output_fd:
        :param poll:
        :return:
        """
        from api.model.OutputWrapper import OperationEnum
        if poll.operation() == OperationEnum.INSERT:
            insert_cache[output_fd] = insert_cache.get(output_fd, [])
            insert_cache[output_fd].append(poll.content())

        elif poll.operation() == OperationEnum.UPDATE:
            update_cache[output_fd] = update_cache.get(output_fd, [])
            update_cache[output_fd].append(poll.content())

        elif poll.operation() == OperationEnum.UPSERT:
            upsert_cache[output_fd] = upsert_cache.get(output_fd, [])
            upsert_cache[output_fd].append(poll.content())

        elif poll.operation() == OperationEnum.CLEAN:
            try:
                FactDatasourceProxyService.fd_client_proxy().delete_all(output_fd)
            except Exception as e:
                raise ServiceInnerException(f"执行失败,Code: {code}的执行器,清空数据发生错误:{str(e)}")

        elif poll.operation() == OperationEnum.DELETE:
            try:
                FactDatasourceProxyService.fd_client_proxy().delete(output_fd, poll.content())
            except Exception as e:
                raise ServiceInnerException(f"执行失败,Code: {code}的执行器,删除数据发生错误:{str(e)}")

    def flush_cache(self, code, insert_cache, update_cache, upsert_cache):
        """
        把缓存中的数据 发送到FD中
        :param code:
        :param insert_cache:
        :param update_cache:
        :param upsert_cache:
        :return:
        """
        try:
            for key, value in insert_cache.items():
                if self.is_killed():
                    FrameworkHandlerLogger.log_warn("任务被强制停止,停止变更数据")
                    return

                if len(value) > 0:
                    FactDatasourceProxyService.fd_client_proxy().inserts(key, value)
                    value.clear()

            for key, value in update_cache.items():
                if self.is_killed():
                    FrameworkHandlerLogger.log_warn("任务被强制停止,停止变更数据")
                    return

                if len(value) > 0:
                    FactDatasourceProxyService.fd_client_proxy().updates(key, value)
                    value.clear()

            for key, value in upsert_cache.items():
                if self.is_killed():
                    FrameworkHandlerLogger.log_warn("任务被强制停止,停止变更数据")
                    return

                if len(value) > 0:
                    FactDatasourceProxyService.fd_client_proxy().save_or_updates(key, value)
                    value.clear()
        except Exception as e:
            raise ServiceInnerException(f"执行失败,Code: {code}的执行器,保存数据发生错误:{str(e)}")

    def find_output_fd(self, output_fds: list, index: int):
        """
        从多个fd中,找到需要的那个fd
        :param output_fds:
        :param index:
        :return:
        """
        if len(output_fds) == 0:
            raise IllegalArgumentException("获取输出FD失败,输出为空")

        if len(output_fds) <= index:
            raise IllegalArgumentException(f"获取输出FD失败,可选输出个数:{len(output_fds)} 期望输出:{index}")

        return output_fds[index]

    def is_killed(self):
        """
        判断是否已经被杀掉了
        :return:
        """
        return False