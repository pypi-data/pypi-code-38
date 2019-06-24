import logging

from .apis import ApiMngr
from .base_util import BaseUtil as Util
from .exceptions import ApiError
from .exceptions import HaloException, HaloError
from .logs import log_json
from  .classes import AbsBaseClass
logger = logging.getLogger(__name__)

"""

https://github.com/flowpl/saga_py

We'll need a transaction log for the saga
this is our coordinator for the saga Functions
Because the compensating requests can also fail  we need to be able to retry them until success, which means they have to be idempotent.
we implements backward recovery only.
For forward recovery you also need to ensure the requests are imdempotent.
"""


class SagaException(HaloException):
    """
    Raised when an action failed and no compensation was found.
    """
    pass


class SagaRollBack(HaloException):
    """
    Raised when an action failed and the compensations complited.
    """
    pass

class SagaError(HaloError):
    """
    Raised when an action failed and at least one compensation also failed.
    """

    def __init__(self, exception, compensation_exceptions):
        """
        :param exception: BaseException the exception that caused this SagaException
        :param compensation_exceptions: list[BaseException] all exceptions that happened while executing compensations
        """
        self.action = exception
        self.compensations = compensation_exceptions


class Action(AbsBaseClass):
    """
    Groups an action with its corresponding compensation. For internal use.
    """

    def __init__(self, name, action_func, compensation, next, result_path):
        """

        :param action: Callable a function executed as the action
        :param compensation: Callable a function that reverses the effects of action
        """
        self.__kwargs = None
        self.__action = action_func
        self.__compensation = compensation
        self.__name = name
        self.__next = next
        self.__result_path = result_path

    def act(self, **kwargs):
        """
        Execute this action

        :param kwargs: dict If there was an action executed successfully before this action, then kwargs contains the
                            return values of the previous action
        :return: dict optional return value of this action
        """
        logger.debug("act " + self.__name)
        self.__kwargs = kwargs
        return self.__action(**kwargs)

    def compensate(self, error):
        """
        Execute the compensation.
        :return: None
        """
        for comp in self.__compensation:
            for error_code in comp["error"]:
                if error_code == "States.ALL" or error_code == error:
                    return comp["next"]
        raise SagaException("no compensation for : " + self.__name)

    def next(self):
        """

        :return:
        """
        return self.__next

    def result_path(self):
        """

        :return:
        """
        return self.__result_path


class SagaLog(AbsBaseClass):
    startSaga = "startSaga"
    endSaga = "endSaga"
    abortSaga = "abortSaga"
    errorSaga = "errorSaga"
    rollbackSaga = "rollbackSaga"
    commitSaga = "commitSaga"

    startTx = "startTx"
    endTx = "endTx"
    failTx = "failTx"

    def log(self, req_context, saga_stage, name, log_db=False):
        """

        :param req_context:
        :param saga_stage:
        :param name:
        :param log_db:
        """
        if log_db:
            # @TODO finish db log for saga
            # db_logeer(saga_stage + " " + name)
            logger.debug("db log")
        logger.info("SagaLog: " + saga_stage + " " + name,
                    extra=log_json(req_context))

class Saga(AbsBaseClass):
    """
    Executes a series of Actions.
    If one of the actions raises, the compensation for the failed action and for all previous actions
    are executed in reverse order.
    Each action can return a dict, that is then passed as kwargs to the next action.
    While executing compensations possible Exceptions are recorded and raised wrapped in a SagaException once all
    compensations have been executed.
    """

    def __init__(self, name, actions, start):
        """
        :param actions: list[Action]
        """
        self.name = name
        self.actions = actions
        self.start = start
        self.slog = SagaLog()

    def execute(self, req_context, payloads, apis):
        """
        Execute this Saga.
        :param req_context:
        :param payloads:
        :param apis:
        :return: None
        """

        self.slog.log(req_context, SagaLog.startSaga, self.name)
        tname = self.start
        results = {}
        kwargs = {'results': results}
        rollback = None
        for action_index in range(len(self.actions)):
            try:
                logger.debug("execute=" + tname)
                kwargs['req_context'] = req_context
                kwargs['payload'] = payloads[tname]
                kwargs['exec_api'] = apis[tname]
                self.slog.log(req_context, SagaLog.startTx, tname)
                ret = self.__get_action(tname).act(**kwargs) or {}
                self.slog.log(req_context, SagaLog.endTx, tname)
                results.update(ret)
                kwargs = {'results': results}
                logger.debug("kwargs=" + str(kwargs))
                tname = self.__get_action(tname).next()
                if tname is True:
                    logger.debug("finished")
                    break
            except ApiError as e:
                self.slog.log(req_context, SagaLog.failTx, tname)
                self.slog.log(req_context, SagaLog.abortSaga, self.name)
                logger.debug("ApiError=" + str(e))
                if rollback is None:
                    rollback = e
                    tname = self.__get_action(tname).compensate(e.status_code)
                else:
                    raise SagaError(rollback, [e])
            except BaseException as e:
                self.slog.log(req_context, SagaLog.failTx, tname)
                logger.debug("e=" + str(e))
                self.slog.log(req_context, SagaLog.errorSaga, self.name)
                raise SagaError(e, [])


            if type(kwargs) is not dict:
                raise TypeError('action return type should be dict or None but is {}'.format(type(kwargs)))

        if rollback:
            self.slog.log(req_context, SagaLog.rollbackSaga, self.name)
            raise SagaRollBack(rollback)

        self.slog.log(req_context, SagaLog.commitSaga, self.name)
        return results

    def __get_action(self, name):
        """
        Returns an action by index.

        :param index: int
        :return: Action
        """
        return self.actions[name]



class SagaBuilder(AbsBaseClass):
    """
    Build a Saga.
    """

    def __init__(self, name):
        self.name = name
        self.actions = {}

    @staticmethod
    def create(name):
        """

        :param name:
        :return:
        """
        return SagaBuilder(name)

    def action(self, name, action_func, compensation, next, result_path):
        """
        Add an action and a corresponding compensation.

        :param action: Callable an action to be executed
        :param compensation: Callable an action that reverses the effects of action
        :return: SagaBuilder
        """
        action = Action(name, action_func, compensation, next, result_path)
        self.actions[name] = action
        return self

    def build(self, start):
        """
        Returns a new Saga ready to execute all actions passed to the builder.
        :return: Saga
        """
        return Saga(self.name, self.actions, start)


def load_saga(name, jsonx, schema):
    """

    :param name:
    :param jsonx:
    :return:
    """
    # validate saga json
    if schema:
        Util.assert_valid_schema(jsonx, schema)
    # process saga
    try:
        if "StartAt" in jsonx:
            start = jsonx["StartAt"]
        else:
            raise HaloError("can not build saga. No StartAt")
        saga = SagaBuilder.create(name)
        for state in jsonx["States"]:
            logger.debug(str(state))
            if jsonx["States"][state]["Type"] == "Task":
                api_name = jsonx["States"][state]["Resource"]
                logger.debug("api_name=" + api_name)
                api_instance_name = ApiMngr.get_api(api_name)
                logger.debug("api_instance_name=" + str(api_instance_name))
                result_path = jsonx["States"][state]["ResultPath"]
                # action = lambda req_context, payload, api=api_instance_name: ApiMngr(req_context).get_api_instance(api).post(payload)
                do_run = lambda key, x: {key: x}
                action = lambda req_context, payload, exec_api, results, result_path=result_path, api=api_instance_name: \
                    do_run(result_path, exec_api(ApiMngr(req_context).get_api_instance(api), results, payload))
                comps = []
                if "Catch" in jsonx["States"][state]:
                    for item in jsonx["States"][state]["Catch"]:
                        comp = {"error": item["ErrorEquals"], "next": item["Next"]}
                        comps.append(comp)
                if "Next" in jsonx["States"][state]:
                    next = jsonx["States"][state]["Next"]
                else:
                    next = jsonx["States"][state]["End"]
                saga.action(state, action, comps, next, result_path)
        return saga.build(start)
    except BaseException as e:
        raise HaloError("can not build saga", e)

