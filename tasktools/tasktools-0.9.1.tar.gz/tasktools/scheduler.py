# standar library
import asyncio
import functools

# contrib
from networktools.library import my_random_string
from networktools.colorprint import gprint, bprint, rprint

# same module
from .taskloop import coromask, renew, simple_fargs, simple_fargs_out


class TaskScheduler:
    """
    This class is a generic tasks scheduler that uses
    asyncio and multiprocessing
    For every new process activate M idle coro tasks
    until when are assigned by a function that send
    an id

    :param args: an unpacked list
    :param kwargs: an unpacked dictionary with at least {*ipt* dict, *ico* dict, *assigned_task* dict, *nproc* int, *sta_init* dict}, all in shared memory manager

    """

    def __init__(self, *args, **kwargs):
        """
        Is a generic init method, the inputs required are
        """
        if 'ipt' in kwargs.keys():
            self.ipt = kwargs.get('ipt')
        if 'ico' in kwargs.keys():
            self.ico = kwargs.get('ico')
        if 'assigned_tasks' in kwargs.keys():
            self.assigned_tasks = kwargs.get('assigned_tasks')
        if 'nproc' in kwargs.keys():
            self.lnproc = kwargs.get('nproc', 3)
        if 'sta_init' in kwargs.keys():
            # dict
            self.sta_init = kwargs.get("sta_init", {})

    def set_ipt(self, uin=4):
        """
        Defines a new id for relation process-collect_task, check if exists

        :param uin: is an optional int to define the length of the keys for ipt dict

        :returns: a new key from ipt
        """
        ipt = my_random_string(uin)
        while True:
            if ipt not in self.ipt:
                self.ipt.append(ipt)
                break
            else:
                ipt = my_random_string(uin)
        return ipt

    def set_ico(self, uin=4):
        """
        Defines a new id for task related to collect data
        inside a worker, check if exists

        :param uin: is an optional int to define the length of the keys for ico dict

        :returns: a new key from ico
        """
        ico = my_random_string(uin)
        while True:
            if ico not in self.ico:
                self.ico.append(ico)
                break
            else:
                ico = my_random_string(uin)
        return ico

    async def run_task(self, *args):
        """
        A default coroutine that await .1 secs every time

        :param args: a unpacked list

        :returns: the same list
        """
        print("There are no new *run_task* coroutine assigned")
        await asyncio.sleep(.1)
        return args

    def set_new_run_task(self, **coros_callback):
        """
        Is a function that you have to call to define the corutines which you need
        to execute on the wheel (gear)

        Is recomended the use at the end of the __init__ method on your new class.

        :param coros_callback: is a dictionary with the corutines, that depends of what you need:

        - A unidirectional machine: you have to set only the *run_task* key
        - A bidirectional machine: you ahve to set also *net2service* and *service2net* keys
        """
        run_task = coros_callback.get('run_task', None)
        net2service_task = coros_callback.get('net2service', {})
        service2net_task = coros_callback.get('service2net', {})
        bprint("*"*30)
        bprint("*"*30)
        bprint("*"*30)
        rprint(coros_callback)
        bprint("*"*30)
        bprint("*"*30)
        bprint("*"*30)

        self.n2s = None
        self.s2n = None
        self.run_task = None

        if asyncio.iscoroutinefunction(run_task):
            self.run_task = run_task
        else:
            print("The callback run_task is not a coroutine")

        if asyncio.iscoroutinefunction(net2service_task.get('coro')):
            self.n2s = net2service_task
        else:
            print("The callback net2service is not a coroutine")

        if asyncio.iscoroutinefunction(service2net_task.get('coro')):
            self.s2n = service2net_task
        else:
            print("The callback service2net is not a coroutine")

        gprint("="*60)
        bprint("SET TASKS TO....")
        rprint(self.run_task)
        rprint(self.n2s)
        rprint(self.s2n)
        gprint("="*60)

    async def process_sta_task(self, ipt, ico, *args):
        """
        Process gather data for ids station

        This coroutine is executed for both cases: unidirectional and bidirectional

        :param ipt: is an ipt value to work with the *ipt* process
        :param ico: is an ico value to work with the *ico* object
        :param args: an unpacked list to execute the *run_task*

        :returns: the first two inputs and the unpacked result
        """
        #bprint("Pre RUN_TASK")
        # rprint(self.run_task)
        # bprint(self.assigned_tasks)
        assigned_task = None
        if ico in self.assigned_tasks[ipt].keys():
            assigned_task = self.assigned_tasks[ipt][ico]
            # assigned task -> ids
            # That is an ids code
        result = None
        #bprint("Assigned task %s" %assigned_task)
        if assigned_task:
            #bprint("RUNTASK assigned")
            # change
            # print("ST Station %s assigned to task %s on process %s"
            # %(assigned_task, ico, ipt), flush=True)
            # print("ST args", flush=True)
            # print(args)
            #print("St INIT %s" %self.sta_init[assigned_task])
            if not self.sta_init.get(assigned_task):
                args = self.set_pst(assigned_task, args)
                # print("ST ARGS to gather...._> %s"
                # %args, flush=True)
            #rprint("SCHEDULER_PROCESS_STA_TASK On task, pre call gather_data")
            result = await self.run_task(*args)
            #gprint("SCHEDULER_PROCESS_STA_TASK On task, post call gather_data %s" %result)

        else:
            # Every N secs check if there are new station to add
            # gprint("Process data avoid \n")
            await asyncio.sleep(1)
            result = args
        #rprint("To next iteration %s" %[ipt, ico, *result])
        return [ipt, ico, *result]

    async def process_sta_task_n2s(self, ipt, ico, *args):
        """
        Process channel network to service data for ids station

        This coroutine is executed for bidirectional case, on network to service direction

        :param ipt: is an ipt value to work with the *ipt* process
        :param ico: is an ico value to work with the *ico* object
        :param args: an unpacked list to execute the *run_task*

        :returns: the first two inputs and the unpacked result
        """

        #rprint("Generating PROCESS STA TASK N2S")
        #bprint("Tasks avalaibles %s" %self.assigned_tasks[ipt] )
        assigned_task = None
        if ico in self.assigned_tasks[ipt].keys():
            assigned_task = self.assigned_tasks[ipt][ico]
            # assigned task -> ids
            # That is an ids code
        result = None
        #bprint("Assigned task %s" %assigned_task)
        if assigned_task:
            # change
            # print("ST Station %s assigned to task %s on process %s"
            # %(assigned_task, ico, ipt), flush=True)
            # print("ST args", flush=True)
            # print(args)
            #print("St INIT %s" %self.sta_init[assigned_task])
            if not self.sta_init.get(assigned_task):
                args = self.set_pst_n2s(assigned_task, args)
                # print("ST ARGS to gather...._> %s"
                # %args, flush=True)
            #rprint("SCHEDULER_PROCESS_STA_TASK On task, pre call gather_data")
            result = await self.n2s_coro(*args)
            #gprint("SCHEDULER_PROCESS_STA_TASK On task, post call gather_data %s" %result)

        else:
            # Every N secs check if there are new station to add
            # gprint("Process data avoid \n")
            await asyncio.sleep(1)
            result = args
        #rprint("To next iteration %s" %[ipt, ico, *result])
        return [ipt, ico, *result]

    async def process_sta_task_s2n(self, ipt, ico, *args):
        """
        Process channel service 2 network for ids station

        This coroutine is executed for bidirectional case, on service to network direction

        :param ipt: is an ipt value to work with the *ipt* process
        :param ico: is an ico value to work with the *ico* object
        :param args: an unpacked list to execute the *run_task*

        :returns: the first two inputs and the unpacked result
        """
        #rprint("Generating PROCESS STA TASK S2N")
        #bprint("Tasks avalaibles %s" %self.assigned_tasks[ipt] )
        assigned_task = None
        if ico in self.assigned_tasks[ipt].keys():
            assigned_task = self.assigned_tasks[ipt][ico]
            # assigned task -> ids
            # That is an ids code
        result = None
        #bprint("Assigned task %s" %assigned_task)
        if assigned_task:
            # change
            # print("ST Station %s assigned to task %s on process %s"
            # %(assigned_task, ico, ipt), flush=True)
            # print("ST args", flush=True)
            # print(args)
            #print("St INIT %s" %self.sta_init[assigned_task])
            if not self.sta_init[assigned_task]:
                args = self.set_pst_s2n(assigned_task, args)
                # print("ST ARGS to gather...._> %s"
                # %args, flush=True)
            #rprint("SCHEDULER_PROCESS_STA_TASK On task, pre call gather_data")
            result = await self.s2n_coro(*args)
            #gprint("SCHEDULER_PROCESS_STA_TASK On task, post call gather_data %s" %result)

        else:
            # Every N secs check if there are new station to add
            # gprint("Process data avoid \n")
            await asyncio.sleep(1)
            result = args
        #rprint("To next iteration %s" %[ipt, ico, *result])
        return [ipt, ico, *result]

    async def process_sta_manager(self, ipt):
        """
        Manage asignation of station to task inside ipt process

        :param ipt: the key of the process

        :returns: a list object with ipt value
        """
        #
        ids_list = self.proc_tasks[ipt]
        ass_tasks = self.assigned_tasks[ipt]
        # gprint("IDS LIST::::::: MANAGER::::%s" %ids_list)
        for ids in ids_list:
            # gprint("ids %s on assg tasks  %s"
            # %(ids, self.assigned_tasks[ipt].values()))
            if not ids in self.assigned_tasks[ipt].values():
                # bprint("Keys on ass tasks %s" %self.assigned_tasks[ipt].keys())
                for ico in self.assigned_tasks[ipt].keys():
                    value = self.assigned_tasks[ipt][ico]
                    if value is None:
                        # rprint("In process %s, task %s,  station %s" %(ipt,ico, ids))
                        ass_tasks.update({ico: ids})
                        break
        self.assigned_tasks[ipt] = ass_tasks
        #ids, loop, sta

        await asyncio.sleep(1)
        #print("sta manager out %s" %ipt)
        return [ipt]

    def set_pst(self, ids, args):
        """
        Set the factory for the wheel's array

        In your class you have to rewrite this.

        :param ids: key of the source
        :param args: list of arguments

        :returns: a different list of future arguments
        """
        #print("Basic pst")
        return [ids, args[1], args[2]]

    def set_init_args(self):
        """
        Set the initial list of arguments

        In your class you have to rewrite this.

        :returns: a list of initial arguments
        """
        #print("Basic init args")
        return [None, None, None, None]

    def add_task(self, ids, ipt):
        """
        Add an *ids* task to some *ipt* process

        :param ids: the key of a source
        :param ipt: the key or identifier of a process
        """
        self.proc_tasks[ipt] += [ids]

    def manage_tasks(self, ipt):
        """
        A method to manage the tasks assigned to *ipt* process

        Initialize an event loop, and assign idle tasks for this process

        Create the tasks for every source assigned to this process.
        Check the cases unidirectional and bidirectional.

        :param ipt: the key or identifier of a process
        """
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # print("WS Gather data ok for %s" %ipt)
        v = 1
        tasks = []
        # bprint("Collect task ipt: %s" %ipt)
        # create signal manager <- GatherSignal
        #
        self.assigned_tasks[ipt] = {}
        new_dict = {}
        # TODO: check if lnproc is ok
        for i in range(self.lnproc):
            ico = self.set_ico()
            nd = {ico: None}
            #bprint("Ico generated %s" %nd)
            new_dict.update(nd)
        self.assigned_tasks[ipt] = new_dict
        # rprint("Assigned tasks: %s"%self.assigned_tasks[ipt])
        for ico in self.assigned_tasks.get(ipt):
            # Over limited tasks on process<=lnproc
            stax = self.set_init_args()
            sargs = [None, stax]
            # gprint("Code process: %s" %ipt)
            if self.run_task:
                try:
                    args = [ipt, ico, *sargs]
                    task = loop.create_task(
                        coromask(
                            self.process_sta_task,
                            args,
                            simple_fargs_out)
                    )
                    task.add_done_callback(
                        functools.partial(renew,
                                          task,
                                          self.process_sta_task,
                                          simple_fargs_out)
                    )
                    tasks.append(task)
                except Exception as exec:
                    print(
                        "Error en collect_task, gather stations, process_sta(task) %s, error %s"
                        % (ipt, exec))
                    print(exec)
                    raise exec

            # add if exists the other tasks
            try:
                if self.n2s:
                    # estructura:
                    # diccionario: coro, args
                    self.n2s_coro = self.n2s.get('coro')
                    n2s_args = self.n2s.get('args')
                    args = [ipt, ico, *n2s_args]
                    task = loop.create_task(
                        coromask(
                            self.process_sta_task_n2s,
                            args,
                            simple_fargs_out)
                    )
                    task.add_done_callback(
                        functools.partial(renew,
                                          task,
                                          self.process_sta_task_n2s,
                                          simple_fargs_out)
                    )
                    tasks.append(task)
            except Exception as exec:
                print(
                    "Error en collect_task, gather stations, net2service(task) %s, error %s"
                    % (ipt, exec))
                print(exec)
                raise exec

            try:
                if self.s2n:
                    self.s2n_coro = self.s2n.get('coro')
                    s2n_args = self.s2n.get('args')
                    args = [ipt, ico, *s2n_args]
                    task = loop.create_task(
                        coromask(
                            self.process_sta_task_s2n,
                            args,
                            simple_fargs_out)
                    )
                    task.add_done_callback(
                        functools.partial(renew,
                                          task,
                                          self.process_sta_task_s2n,
                                          simple_fargs_out)
                    )
                    tasks.append(task)
            except Exception as exec:
                print(
                    "Error en collect_task, gather stations, service2net(task) %s, error %s"
                    % (ipt, exec))
                print(exec)
                raise exec

        # Task manager
        try:
            args = [ipt]
            #bprint("Args to sta manager %s" %args)
            task = loop.create_task(
                coromask(
                    self.process_sta_manager,
                    args,
                    simple_fargs_out)
            )
            task.add_done_callback(
                functools.partial(renew,
                                  task,
                                  self.process_sta_manager,
                                  simple_fargs_out)
            )
            tasks.append(task)
        except Exception as exec:
            print("Error en collect_task, manager %s, error %s" % (ipt, exec))
            print(exec)
            raise exec
        bprint("Loop is running yet?")
        rprint(loop.is_running())
        if not loop.is_running():
            #gprint("Starting running this loop")
            #bprint("Printing all tasks")
            #[rprint(task) for task in asyncio.Task.all_tasks()]
            # loop.run_until_complete(asyncio.gahter(*tasks))
            loop.run_forever()
