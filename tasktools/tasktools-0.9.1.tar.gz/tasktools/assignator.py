import asyncio
import functools

from networktools.colorprint import gprint, bprint, rprint

from .taskloop import coromask, renew, simple_fargs, simple_fargs_out


class TaskAssignator:
    """
    Manage the tasks assigned to a TaskScheduler instance

    :param scheduler: A TaskScheduler instance
    :param queue_tasks: a queue
    :param sta_assigned: a dict managed for multiprocessing
    :param dt_status: a string that select the kind of group {GROUP, ALL}
    :param dt_group: a list of the group selected
    :param args: some extra args
    :param kwargs: some extra keyword args

    """

    def __init__(self, scheduler: "Scheduler",
                 queue_tasks: "Shared dict",
                 sta_assigned: list,
                 dt_status,
                 dt_group,
                 *args, **kwargs):
        self.scheduler = scheduler
        self.queue_tasks = queue_tasks
        self.sta_assigned = sta_assigned
        self.dt_status = dt_status
        self.dt_group = dt_group
        self.ts = 10
        self.code_filter = kwargs.get('code_filter', 'code')
        if 'ts' in kwargs:
            self.ts = kwargs.get('ts', 3)

    async def new_process(self, queue_tasks):
        """
        This coroutine activate a process with new station task
        Check every \ts\ seconds the queue_tasks if there are new
        stations or tasksto add.

        Works on a async wheel

        :param queue_tasks: a queue to put task ids

        """
        await asyncio.sleep(self.ts)
        # gprint("0=0"*10)
        #bprint("New process task")
        #rprint("Queue with data? %s" % (not queue_tasks.empty()))
        # gprint("0=0"*10)
        scheduler = self.scheduler
        sta_assigned = self.sta_assigned
        dt_status = self.dt_status
        dt_group = self.dt_group
        msg_in = []

        try:
            tasks = []
            W = 0
            """
            bprint("ASSIGNATOR [] Checking list of tasks %s" %
                   (queue_tasks.qsize()))
            rprint(queue_tasks)
            gprint(list(scheduler.stations.keys()))
            rprint("IPTS:>%s" % list(scheduler.proc_tasks.keys()))
            """
            if not queue_tasks.empty():
                for i in range(queue_tasks.qsize()):
                    ids = queue_tasks.get()
                    #rprint("Recover ids:::%s" % ids)
                    scheduler.status_tasks[ids] = True
                    scheduler.sta_init[ids] = True
                    if ids in scheduler.stations.keys():
                        q = 0
                        for ipt in scheduler.proc_tasks.keys():
                            q += 1
                            if len(scheduler.proc_tasks.get(ipt)) < \
                               scheduler.lnproc and \
                               ids not in sta_assigned:
                                if dt_status == 'GROUP':
                                    if scheduler.stations.get(ids).get(self.code_filter) in dt_group:
                                        scheduler.add_task(ids, ipt)
                                        scheduler.set_init(ids)
                                        sta_assigned.append(ids)
                                        ans = "TASK %s ADDED TO %s" % (
                                            ids, ipt)
                                elif dt_status == 'ALL':
                                    scheduler.add_task(ids, ipt)
                                    scheduler.set_init(ids)
                                    sta_assigned.append(ids)
                                    ans = "TASK %s ADDED TO %s" % (ids, ipt)
                queue_tasks.task_done()
        except Exception as exec:
            bprint("Error en asignación de tareas a procesador: %s" % exec)
            raise exec

    def new_process_task(self):
        """
        This function allows the system to call the coroutine that add
        a new_process in an asynchronous loop *the wheel*
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            args = [self.queue_tasks]
            #bprint("New process task")
            task = loop.create_task(
                coromask(
                    self.new_process,
                    args,
                    simple_fargs)
            )
            #
            task.add_done_callback(
                functools.partial(
                    renew,
                    task,
                    self.new_process,
                    simple_fargs)
            )
        except Exception as exec:
            rprint("Error en levantar corrutina %s" % exec)
            raise exec
        if not loop.is_running():
            loop.run_forever()
