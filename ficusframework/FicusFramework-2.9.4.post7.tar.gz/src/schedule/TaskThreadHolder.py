from schedule.TaskThread import TaskThread

__actor_port = 8011
__task_thread_cache = dict()


def registry_task_thread(task_id: int, handler, remove_old_reason: str):
    """
       注册一个任务线程
    :param task_id:
    :param handler: ITaskHandler
    :param remove_old_reason:
    :return:
    """
    # 实例化一个线程
    new_task_thread = TaskThread(handler, __actor_port)
    new_task_thread.start()  # 开启线程

    old_task_thread: TaskThread = __task_thread_cache.get(task_id)
    __task_thread_cache[task_id] = new_task_thread

    if old_task_thread is not None:
        old_task_thread.stop(remove_old_reason)

    return new_task_thread


def remove_task_thread(job_id: int, remove_old_reason: str):
    """
    删除一个任务线程
    :param job_id:
    :param remove_old_reason:
    :return:
    """
    old_task_thread: TaskThread = __task_thread_cache.pop(job_id)

    if old_task_thread is not None:
        old_task_thread.stop(remove_old_reason)
        # 还需要调用 interrupt()

def cancel_task_thread(job_id:int,task_id:int,is_executing:bool):
    """
    停止某一个任务
    :param job_id:
    :param task_id:
    :param is_executing:
    :return:
    """
    task_thread:TaskThread = __task_thread_cache.get(job_id)

    if  task_thread is not None:
        if is_executing :
            # 说明任务已经开始做了,不杀掉整个Job的Thread
            task_thread.kill_doing_task()
        else:
            # 说明任务还没真正开始做,还在队列里面.
            task_thread.remove_trigger_queue(task_id)


def load_task_thread(task_id: int):
    """
    返回一个任务线程
    :param task_id:
    :return:
    """
    return __task_thread_cache.get(task_id)
