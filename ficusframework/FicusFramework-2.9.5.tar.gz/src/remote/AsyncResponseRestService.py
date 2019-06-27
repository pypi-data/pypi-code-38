import json
import logging
from threading import Thread

from flask import request
from munch import Munch

from api.exceptions import ServiceInnerException
from api.handler.IAsyncAble import IAsyncAble
from api.model.ResultVO import FAIL, FAIL_CODE, ResultVO
from client import ScheduleJobTaskLogClient, JobScheduleClient
from schedule import TaskThreadHolder, TaskHandlerContext
from schedule.TaskThread import TaskThread
from . import remote

log = logging.getLogger('Ficus')


def build_task_param(schedule_job_info, job_task_log, task_process_log_id_, ficus_param):
    """
    构造taskParam
    :param schedule_job_info:
    :param job_task_log:
    :param task_process_log_id_:
    :param ficus_param:
    :return:
    """
    global shardingArr
    shardingParam: str = job_task_log.shardingParam
    if shardingParam is not None:
        shardingArr = shardingParam.split("/")

    m = {
        "actorBlockStrategy": schedule_job_info.actorBlockStrategy,
        "actorName": schedule_job_info.actorName,
        "actorHandler": schedule_job_info.actorHandler,
        "actorParams": ficus_param,
        "jobId": schedule_job_info.id,
        "jobType": schedule_job_info.jobType,
        "limitTimes": schedule_job_info.limitTimes,
        "logId": job_task_log.id,
        "scriptJobRemark": schedule_job_info.scriptJobRemark,
        "scriptJobSource": schedule_job_info.scriptJobSource,
        "updateTime": "2018-02-04 10:35:39",
        "triggerTime": job_task_log.triggerTime,
        "retryLogId": job_task_log.retryLogId,
        "processLogId": task_process_log_id_,
        "retryTimes": job_task_log.retryTimes if "retryTimes" in job_task_log else None,
        "shardIndex": -1 if shardingParam is None else shardingArr[0],
        "shardTotal": -1 if shardingParam is None else shardingArr[1]
    }
    return Munch(m)


def async_do_finish(task_log_id, ficus_param: dict, headers: dict, async_service_response: Munch,
                    task_thread: TaskThread, task_handler: IAsyncAble,
                    task_param: Munch):
    """
    异步处理结果
    :param task_log_id:
    :param ficus_param:
    :param headers:
    :param async_service_response:
    :param task_thread:
    :param task_handler:
    :param task_param:
    :return:
    """
    if "taskStatus" in async_service_response and async_service_response["taskStatus"] == -1:
        headers["__error__"] = async_service_response["taskDesc"] if "taskDesc" in async_service_response else None

    try:
        executeResult = task_handler.do_finish(task_log_id, async_service_response.responseData, headers, ficus_param,
                                               async_service_response.taskState)
        if executeResult is None:
            executeResult = FAIL
    except Exception as e:
        executeResult = ResultVO(FAIL_CODE, str(e))

    try:
        task_thread.handle_execute_result(task_param, executeResult)
    except Exception as e:
        stopResult = ResultVO(FAIL_CODE, f" 处理logId:{task_log_id} 出现严重错误:{str(e)}")
        ScheduleJobTaskLogClient.update_task_status_to_finished(task_log_id, stopResult, True)


@remote.route('/async/response/<int:job_id>/<int:task_log_id>', methods=['POST'])
def do_finish(job_id: int, task_log_id: int):
    """
    用户接收消息的回调,不再ficus-core中写,而是在这写
    是因为避免返回的数据太大,不适合从ficus-core中再过一次
    :param job_id:
    :param task_log_id:
    :return:
    """

    log.info(f"接收到任务回调,jobId:{job_id} logId:{task_log_id}")

    job_task_log = ScheduleJobTaskLogClient.get_task_log_by_id(task_log_id)

    if job_task_log is None:
        raise ServiceInnerException(f"任务:{task_log_id}没有找到数据,无法回调")

    if 1 != job_task_log.executeStatus:
        raise ServiceInnerException(f"任务:{task_log_id}执行状态为{job_task_log.executeStatus},无法回调")

    ficus_param = json.loads(job_task_log.actorParam)

    ficus_param["__jobId__"] = job_id
    ficus_param["__logId__"] = task_log_id
    ficus_param["__triggerTime__"] = job_task_log.triggerTime

    taskProcessLogId_ = ficus_param["taskProcessLogId_"] if "taskProcessLogId_" in ficus_param else None

    if taskProcessLogId_ is not None:
        ficus_param["__processLogId__"] = str(taskProcessLogId_)

    schedule_job_info = JobScheduleClient.find_by_site_and_code(ficus_param["site_"], ficus_param["projectCode_"],
                                                                ficus_param["code_"])

    task_param = build_task_param(schedule_job_info, job_task_log, taskProcessLogId_, ficus_param)

    task_thread: TaskThread = TaskThreadHolder.load_task_thread(job_id)

    task_handler = task_thread.get_handler() if task_thread is not None else None

    if task_handler is None:
        # 需要重新实例化
        task_handler = TaskHandlerContext.load_task_handler(task_param.actorHandler)

    if task_thread is None:
        task_thread = TaskThreadHolder.registry_task_thread(job_id, task_handler, "异步任务构造taskThread")

    if not isinstance(task_handler, IAsyncAble):
        # 说明不是异步的任务,抛错
        raise ServiceInnerException(f"任务:{task_log_id}执行类型不是异步执行器,无法回调")

    data = request.get_data()
    async_service_response = Munch(json.loads(data.decode("utf-8"))) if data is not None else None

    # 异步执行结果回调
    t = Thread(target=async_do_finish, args=(
        task_log_id, ficus_param, request.headers, async_service_response, task_thread, task_handler, task_param))
    t.start()

    return "success"
