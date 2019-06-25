from abc import abstractmethod

from api.model.ResultVO import ResultVO


class IAsyncAble:

    @abstractmethod
    def do_finish(self, task_log_id: int, response, header: dict, ficus_param: dict, task_status: int) -> ResultVO:
        pass
