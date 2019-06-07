#pylint: disable=no-member,logging-format-interpolation
"""
*hynet* optimization server for distributed computation.
"""

import logging
import subprocess
import getpass
from multiprocessing import Queue, Value, Process
from multiprocessing.managers import SyncManager
from time import sleep

import numpy as np
import tqdm

import hynet.config as config
from hynet.scenario.representation import Scenario
from hynet.model.steady_state import SystemModel
from hynet.opf.calc import calc_opf
from hynet.qcqp.problem import QCQP

_log = logging.getLogger(__name__)


def start_optimization_server(port=None, authkey=None, local=False):
    """
    Create, start, and return a *hynet* optimization server.

    Parameters
    ----------
    port : int, optional
        TCP port on which the *hynet* optimization server shall be running.
    authkey : str, optional
        Authentication key that must be presented by *hynet* optimization
        clients to connect to the server.
    local : bool, optional
        If ``True`` (default is ``False``), the optimization server processes
        all jobs on the local machine and *connections of clients are not
        accepted*. In case that some code is designed to utilize distributed
        computation, but the the server cluster is not available, this local
        mode supports the computation on the local machine without the
        client management overhead.

    Returns
    -------
    server : OptimizationServer
        The *hynet* optimization server.
    """
    if port is None:
        port = config.DISTRIBUTED['default_port']
    if authkey is None:
        authkey = config.DISTRIBUTED['default_authkey']
    return OptimizationServer(port, authkey, local)


class OptimizationJob:
    """
    Represents a *hynet* optimization job.

    A *hynet* optimization job may be an OPF problem, specified via the
    scenario data or system model, or a QCQP problem. Furthermore, the solver
    or solver type for its solution may be specified.

    Parameters
    ----------
    problem : Scenario or SystemModel or QCQP
        Problem specification.
    solver : SolverInterface, optional
        Solver for the provided problem; the default selects an appropriate
        solver of those available. For QCQPs, the solver must be specified
        explicitly. Please make sure that the selected solver is installed on
        all client machines.
    solver_type : SolverType, optional
        Optional solver type for the problem. If passed, it restricts the
        automatic solver selection to this type. It is ignored if ``solver``
        is not ``None``.
    """

    def __init__(self, problem, solver=None, solver_type=None):
        if not isinstance(problem, (Scenario, SystemModel, QCQP)):
            raise ValueError("The provided problem specification is invalid.")

        if isinstance(problem, QCQP) and solver is None:
            raise ValueError("For QCQPs, the solver must be provided.")

        self.problem = problem
        self.solver = solver
        self.solver_type = solver_type
        self.id = None  # Used internally to sort the job results

    def process(self):
        """
        Process the optimization job and return the result (or exception).
        """
        try:
            if isinstance(self.problem, QCQP):
                result = self.solver.solve(self.problem)
            else:
                result = calc_opf(self.problem,
                                  solver=self.solver,
                                  solver_type=self.solver_type)
        except Exception as exception:
            _log.warning("Job {0} failed: {1}".format(self.id, str(exception)))
            result = exception
        return result


class OptimizationServer:
    """
    *hynet* optimization server for distributed computation.

    This server manages the distributed computation of a set of *hynet*
    optimization problems (OPF or QCQPs) on *hynet* optimization clients.
    """

    def __init__(self, port, authkey, local):
        """
        Create a *hynet* optimization server.
        """
        self._port = port
        self._authkey = authkey
        self._local = local

        if not local:
            self._manager = _create_server_manager(port, authkey.encode('utf-8'))
            self._job_queue = self._manager.get_job_queue()
            self._result_queue = self._manager.get_result_queue()
        else:
            self._manager = self._job_queue = self._result_queue = None

    @staticmethod
    def _enumerate_jobs(job_list, solver):
        """Create and return an enumerated job list."""
        job_enumeration = []
        for i, job in enumerate(job_list):
            if not isinstance(job, OptimizationJob):
                job = OptimizationJob(job, solver=solver)
            job.id = i + 1
            job_enumeration.append(job)
        return job_enumeration

    def calc_jobs(self, job_list, solver=None, show_progress=True):
        """
        Calculate the list of *hynet* optimization jobs and return the results.

        The provided list of jobs is processed by distributing them to the
        connected *hynet* optimization clients, collecting the results, and
        returning an array of results that corresponds with the provided array
        of jobs. Note that if there are no clients connected, this method will
        wait until a client is connected to process the jobs.

        Parameters
        ----------
        job_list : array-like
            List of *hynet* optimization jobs (``OptimizationJob``) or problem
            specifications (``Scenario``, ``SystemModel``, or ``QCQP``).
        solver : SolverInterface, optional
            If provided, this solver is used for problem specifications
            (``Scenario``, ``SystemModel``, or ``QCQP``). It is ignored for job
            specifications (``OptimizationJob``).
        show_progress : bool, optional
            If True (default), the progress is reported to the standard output.

        Returns
        -------
        results : numpy.ndarray
            Array containing the optimization results.
        """
        job_list = self._enumerate_jobs(job_list, solver)
        results = np.empty(len(job_list), dtype=object)

        # Are we in local mode? If so, process here...
        if self._local:
            for i, job in enumerate(tqdm.tqdm(job_list,
                                              unit="job",
                                              disable=not show_progress)):
                results[job.id - 1] = job.process()
            return results

        # ...otherwise, put them in the queue and let the clients process them.
        for job in job_list:
            self._job_queue.put(job)

        num_results = Value('I', 0, lock=False)  # Unsigned int shared mem. var.

        if show_progress:
            progress_bar = Process(target=_progress_bar,
                                   args=(num_results, len(job_list)))
            progress_bar.start()

        while num_results.value < len(job_list):
            result_dict = self._result_queue.get()
            for (job_id, result) in result_dict.items():
                results[job_id - 1] = result
            num_results.value += len(result_dict)

        if show_progress:  # Wait for the progress bar to finish
            progress_bar.join()

        return results

    def shutdown(self):
        """Stop the *hynet* optimization server and all connected clients."""
        if self._manager is not None:
            self._manager.shutdown()

    def start_clients(self, client_list, server_ip, ssh_user=None,
                      ssh_port=None, num_workers=None, log_file=None,
                      suppress_output=True):
        """
        Automated start of *hynet* optimization clients.

        This method provides an automatic start of *hynet* optimization clients
        via SSH if the server can connect to the clients via ``ssh [client]``
        (e.g. by configuring SSH keys; please be aware of the related aspects
        of system security). *hynet* must be properly installed on all client
        machines.

        This function uses SSH to run the *hynet* package with the sub-command
        ``client`` and corresponding command line arguments (``python -m hynet
        client ...``) on every client machine. To customize the SSH and Python
        command, see ``hynet.config``.

        Parameters
        ----------
        client_list : array-like
            List of strings containing the host names or IP addresses of the
            client machines.
        server_ip : str
            IP address the *hynet* optimization server.
        ssh_user : str, optional
            The user name for the SSH login on the client machines. By default,
            this is set to the current user name (``getpass.getuser()``).
        ssh_port : int, optional
            Port on which SSH is running on the client machines.
        num_workers : int, optional
            Number of worker processes that should run in parallel on every
            client machine.
        log_file : str, optional
            Log file on the client machines to capture the output.
        suppress_output : bool, optional
            If ``True`` (default), the activity output of the optimization
            clients is suppressed.
        """
        if self._local:
            _log.warning("The server is in local mode. "
                         "Skipping the start of clients.")
            return

        if ssh_user is None:
            ssh_user = getpass.getuser()

        command_pre = config.DISTRIBUTED['ssh_command'] + " -f "
        if ssh_port is not None:
            command_pre += "-p {0:d} ".format(ssh_port)
        command_pre += ssh_user + "@"

        command_post = ' "' + config.DISTRIBUTED['python_command']
        command_post += " -m hynet client "
        command_post += server_ip
        command_post += " -p {0:d}".format(self._port)
        command_post += " -a " + self._authkey
        if num_workers is not None:
            command_post += " -n {0:d}".format(num_workers)
        if log_file is not None:
            command_post += " &> " + log_file
        command_post += '"'

        if suppress_output:
            output_stream = subprocess.DEVNULL
        else:
            output_stream = None  # Stay with the default

        for client in client_list:
            try:
                subprocess.run(command_pre + client + command_post,
                               shell=True, check=True, stdout=output_stream)
            except subprocess.CalledProcessError as exception:
                _log.error("Failed to start client on '{0}': {1}"
                           .format(client, str(exception)))


def _create_server_manager(port, authkey):
    """
    Return a (started) manager for a *hynet* optimization server.

    Parameters
    ----------
    port : int
        TCP port on which the *hynet* optimization server shall be running.
    authkey : str
        Authentication key that must be presented by *hynet* optimization
        clients to connect to the server.

    Returns
    -------
    manager : ServerManager
        Manager object for a *hynet* optimization server.
    """
    job_queue = Queue()
    result_queue = Queue()

    class ServerManager(SyncManager):
        """This class manages the synchronization of the queues."""
        pass

    ServerManager.register('get_job_queue', callable=lambda: job_queue)
    ServerManager.register('get_result_queue', callable=lambda: result_queue)

    manager = ServerManager(address=('', port), authkey=authkey)
    manager.start()
    _log.info('Started server on port {0}'.format(port))
    return manager


def _progress_bar(counter, num_total):
    """
    Show a progress bar on the standard output.

    Parameters
    ----------
    counter : multiprocessing.Value
        Counter for the number of processed jobs as a shared memory object.
    num_total : int
        Total number of jobs.
    """
    num_progress = 0
    with tqdm.tqdm(total=num_total, unit="job") as progress_bar:
        while True:
            num_done = counter.value
            if num_done != num_progress:
                progress_bar.update(num_done - num_progress)
                num_progress = num_done
            else:
                progress_bar.refresh()
            if num_done == num_total:
                return
            sleep(0.25)
