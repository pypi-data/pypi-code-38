import logging
import threading
import time
from collections import deque
from datetime import datetime
from queue import Queue, Empty

import client
from api.exceptions import IllegalArgumentException
from api.model.ResultVO import *
from schedule.utils.log import TaskLogFileAppender, FrameworkHandlerLogger

log = logging.getLogger('Ficus')

class BlockingQueue(Queue):
    """
    允许删除的阻塞队列
    """
    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.popleft()

    def remove(self,item):
        self.queue.remove(item)

class TaskThread(threading.Thread):
    """
    真正开始执行任务的线程
    """

    def __init__(self, handler, actor_port):
        """
        执行器线程的构造函数
        :param handler: ITaskHandler
        :param actor_port:
        """
        threading.Thread.__init__(self, name="任务线程")

        if handler is None:
            raise IllegalArgumentException("创建TaskThread失败,传入的ITaskHandler为空,无法执行")
        self.handler = handler
        self.actor_port = actor_port
        self.to_stop = False
        self.stop_reason = None
        self.running = False
        self.trigger_queue: BlockingQueue = BlockingQueue()  # 使用了Python中的队列
        self.trigger_log_id_set = set()  # TODO ConcurrentHashSet

    def get_handler(self):
        """
        获取handler
        :return:
        """
        return self.handler

    def push_trigger_queue(self, trigger_param):
        """
        把任务放入 任务队列中去
        :param trigger_param:
        :return:
        """
        if trigger_param.logId in self.trigger_log_id_set:
            return ResultVO(code=FAIL_CODE, msg=f"任务已重复,LogId:{trigger_param.log_id}")

        # 放入队列中
        self.trigger_log_id_set.add(trigger_param.logId)
        self.trigger_queue.put_nowait(trigger_param)
        return SUCCESS

    def stop(self, stop_reason):
        """
        强制杀掉任务
        :param stop_reason:
        :return:
        """
        log.info(f"任务TaskThread终止,原因:{stop_reason}")
        self.to_stop = True
        self.stop_reason = stop_reason

        if self.handler is not None:
            try:
                self.handler.kill()
                self.handler.task_logger = None
            except Exception as e:
                FrameworkHandlerLogger.log_warn(f"kill Handler 失败,",e)

    def remove_trigger_queue(self, log_id):
        """
        从等待队列中删除任务
        :param log_id:
        :return:
        """
        if log_id in self.trigger_log_id_set:
            # 说明任务确实在这里面
            for next in list(self.trigger_queue.queue):
                if log_id == next.logId :
                    # 说明找到任务了
                    self.trigger_queue.remove(next)
                    self.trigger_log_id_set.remove(log_id)
                    # 需要修改任务的状态,
                    self.__update_task_status_to_finished(log_id,ResultVO(FAIL_CODE, "任务在等待队列被手动强制停止"),True,1)
                    return True

        return False

    def kill_doing_task(self):
        """
        强制杀掉handler,也就是当前的任务
        :return:
        """
        FrameworkHandlerLogger.log_info(f"任务TaskThread 强制杀掉当前执行的任务")
        # 停的时候也需要把handler里面的东西清理了
        if self.handler is not None:
            try:
                self.handler.kill()
                self.handler.task_logger = None
            except Exception as e:
                FrameworkHandlerLogger.log_warn(f"kill Handler 失败,",e)

    def is_running_or_has_queue(self):
        """
        判断任务线程的情况
        :return:
        """
        return self.running or not self.trigger_queue.empty()

    def run(self):
        """
        周期执行的东西
        :return:
        """

        log_id = None
        while not self.to_stop:
            self.running = False
            try:
                # 3秒等待一个任务
                task_param = None
                try:
                    task_param = self.trigger_queue.get(timeout=3)
                except Empty:
                    pass

                if task_param is None:
                    # 没有任务
                    continue

                log_id = task_param.logId

                FrameworkHandlerLogger.log_info(f"开始处理logId:{log_id}的任务")

                # 有任务, 修改状态
                self.running = True
                self.trigger_log_id_set.remove(log_id)

                if task_param.actorParams is None:
                    task_param.actorParams = {}

                task_param.actorParams["__logId__"] = log_id
                task_param.actorParams["__triggerTime__"] = task_param.triggerTime
                task_param.actorParams["__processLogId__"] = task_param.processLogId

                # 更新任务状态到正在执行
                import config
                self.__update_task_status_to_execute(log_id,
                                                     f"{config.server_ip or config.find_host_ip()}:{config.server_port or 5000}", 1)

                from schedule import ShardContext
                try:
                    from schedule.ShardContext import Sharding
                    ShardContext.set_sharding(Sharding(task_param.shardIndex,task_param.shardTotal))
                    TaskLogFileAppender.prepare_to_log(datetime.strptime(task_param.triggerTime,"%Y-%m-%d %H:%M:%S"),task_param.logId)
                    from schedule.utils.log.TaskLogger import TaskLogger
                    self.handler.task_logger = TaskLogger(TaskLogFileAppender.get_log_file_path(datetime.strptime(task_param.triggerTime,"%Y-%m-%d %H:%M:%S"),task_param.logId))
                    execute_result = self.handler.execute(task_param.actorParams)
                    if execute_result is None:
                        execute_result = FAIL
                except Exception as e:
                    FrameworkHandlerLogger.log_error(f"处理logId:{log_id}出现错误:",e)
                    if self.to_stop:
                        FrameworkHandlerLogger.log_error(f"任务线程强制停止:",e)
                        try:
                            self.handler.kill()
                        except:
                            pass
                    execute_result = ResultVO(FAIL_CODE, str(e))
                finally:
                    ShardContext.reset()
                    TaskLogFileAppender.end_log()
                    self.handler.task_logger=None

                if not self.to_stop:

                    if execute_result.code==FAIL_CODE and task_param.retryTimes is not None and task_param.retryTimes > 0 :
                        # region 如果是失败的,并且有重试次数的,那么就需要做重试的判断
                        if task_param.retryLogId is None:
                            # 说明是第一次重试
                            currentRetryTimes = 0
                        else:
                            # 计算失败的任务次数,就知道重试了几次了
                            currentRetryTimes = client.ScheduleJobTaskLogClient.count_failed_task_log_by_retry_log_id(task_param.retryLogId)

                        if currentRetryTimes<task_param.retryTimes:
                            # 执行完成,回调写入 执行结果
                            self.__update_task_status_to_finished(log_id, execute_result,False, 1)

                            # 小于设定的重试次数,那么就需要重试
                            # 重试的操作就是类似于手动触发一次调度

                            # 把原来的参数还原回去
                            param = task_param.actorParams
                            param["retryLogId"] = task_param.retryLogId or task_param.logId
                            if -1!=task_param.shardIndex and -1!=task_param.shardTotal:
                                param["shardingParam"] = f"{task_param.shardIndex}/{task_param.shardTotal}"

                            if client.JobScheduleClient.trigger_job(task_param.jobId,param):
                                # 重新触发成功
                                FrameworkHandlerLogger.log_info(f"处理jobId:{task_param.jobId}的任务实例:{task_param.retryLogId}  成功触发重试,当前重试次数:{currentRetryTimes}/{task_param.retryTimes}")
                            else:
                                FrameworkHandlerLogger.log_error(
                                    f"处理jobId:{task_param.jobId}的任务实例:{task_param.retryLogId}  触发重试失败,当前重试次数:{currentRetryTimes}/{task_param.retryTimes}")
                        else:
                            # 执行完成,回调写入 执行结果
                            self.__update_task_status_to_finished(log_id, execute_result, True, 1)
                            # 等于大于了重试次数,那么就不重试了.
                            FrameworkHandlerLogger.log_warn(
                                f"处理jobId:{task_param.jobId}的任务实例:{task_param.retryLogId}  已超过最大重试次数:{task_param.retryTimes} 不继续进行重试")
                        # endregion
                    else:
                        # 执行完成,回调写入 执行结果
                        self.__update_task_status_to_finished(log_id, execute_result, True, 1)

                    # 这里判断执行次数,如果判断到已经到达执行次数的上限,就要把这个cron调度给停止了
                    if task_param.limitTimes is not None and task_param.limitTimes > 0:
                        # 说明这个任务是只执行有限次数的任务. 那么就需要查询这个Job已经执行成功了的任务的次数
                        success_times = client.ScheduleJobTaskLogClient.count_success_task_log_by_job(task_param.jobId,
                                                                                                      task_param.updateTime)
                        if success_times >= task_param.limitTimes:
                            # 说明已经到达了执行次数的限制.那么就需要停止这个调度
                            if client.JobScheduleClient.stop(task_param.jobId):
                                self.stop("达到任务执行次数上限,完成job")
                else:
                    # 执行强制停止,回调写入 失败信息
                    self.__update_task_status_to_finished(log_id,
                                                          ResultVO(FAIL_CODE, f"{self.stop_reason} 业务运行中,被强制终止"),True, 1)
            except Exception as e:
                if log_id is not None:
                    FrameworkHandlerLogger.log_error(f"处理logId:{log_id}出现严重错误", e)
                    self.__update_task_status_to_finished(log_id,
                                                          ResultVO(FAIL_CODE,
                                                                   f"{self.stop_reason}  处理logId:{log_id} 出现严重错误:"),True,
                                                          1)

        while self.trigger_queue is not None and not self.trigger_queue.empty():
            try:
                task_param = self.trigger_queue.get_nowait()
            except Empty:
                return
            if task_param is not None:
                self.__update_task_status_to_finished(task_param.logId,
                                                      ResultVO(FAIL_CODE,
                                                               f"{self.stop_reason}  处理logId:{log_id} 任务尚未执行,在调度队列中被终止:"),True,
                                                      1)

    # region 私有方法
    def __update_task_status_to_execute(self, log_id, instance_address, deep):
        """
        更新任务的状态到正在执行中
        :param log_id:
        :param instance_address:
        :param deep:
        :return:
        """
        if deep > 3:
            # 重试3次还不行, 直接退出
            FrameworkHandlerLogger.log_error(f"更新logId:{log_id} 的状态,重试3次仍然无法连接到ficus,无法更新任务状态到正在执行.")
            return False

        try:
            # 把任务状态设置为执行中
            client.ScheduleJobTaskLogClient.update_task_status_to_execute(log_id, instance_address)
        except Exception:
            FrameworkHandlerLogger.log_error(f"更新logId:{log_id} 的状态,连接到ficus,无法更新任务状态到正在执行.次数:{deep}")
            time.sleep(3)
            deep += 1
            return self.__update_task_status_to_execute(log_id, instance_address, deep)

    def __update_task_status_to_finished(self, log_id, execute_result,triggerProcess, deep):
        """
        更新任务的状态到结束
        :param log_id:
        :param execute_result:
        :param deep:
        :return:
        """
        if deep > 3:
            # 重试3次还不行, 直接退出
            FrameworkHandlerLogger.log_error(f"更新logId:{log_id} 的状态,重试3次仍然无法连接到ficus,无法更新任务状态到完成.")
            return False

        try:
            # 把任务状态设置为执行中
            client.ScheduleJobTaskLogClient.update_task_status_to_finished(log_id, execute_result.to_dict(),triggerProcess)
        except Exception:
            FrameworkHandlerLogger.log_error(f"更新logId:{log_id} 的状态,连接到ficus,无法更新任务状态到到完成.次数:{deep}")
            time.sleep(3)
            deep += 1
            return self.__update_task_status_to_finished(log_id, execute_result,triggerProcess, deep)
    # endregion