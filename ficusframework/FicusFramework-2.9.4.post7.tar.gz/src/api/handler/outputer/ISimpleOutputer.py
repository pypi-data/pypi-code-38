from api.handler.outputer.IBaseOutputer import IBaseOutputer


class ISimpleOutputer(IBaseOutputer):

    def send_output_result(self, code, result_list, output_fd_codes):
        """
        发送任务到FD
        :param code:
        :param result_list:
        :param output_fd_codes:
        :return:
        """

        insert_cache = {}
        update_cache = {}
        upsert_cache = {}

        # 把任务放入缓存
        for serializable_output_wrapper in result_list:
            output_fd = self.find_output_fd(output_fd_codes, serializable_output_wrapper.index())
            self.put_in_cache(code, insert_cache, update_cache, upsert_cache, output_fd, serializable_output_wrapper)

        # 清理缓存中的任务
        self.flush_cache(code, insert_cache, update_cache, upsert_cache)
