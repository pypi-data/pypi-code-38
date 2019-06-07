#pylint: disable=no-member,logging-format-interpolation
"""
*hynet* optimization client for distributed computation.
"""

import logging
from multiprocessing import Process
from multiprocessing.managers import SyncManager
import queue
import time
import socket

import hynet.config as config

_log = logging.getLogger(__name__)


def start_optimization_client(server_ip, port=None, authkey=None,
                              num_workers=None, verbose=True):
    """
    Create, connect, and start a *hynet* optimization client.

    Note that this call is blocking until the *hynet* optimization server, to
    which the client is connected, is shut down.

    Parameters
    ----------
    server_ip : str
        IP address of the *hynet* optimization server.
    port : int, optional
        TCP port of the *hynet* optimization server.
    authkey : str, optional
        Authentication key for the *hynet* optimization server.
    num_workers : int, optional
        Number of worker processes that should run in parallel. If more than
        one worker is started, it is recommended to disable the internal
        parallel processing, see ``parallelize`` in ``hynet.config``.
    verbose : bool, optional
        If True (default), some information on activity of the client is
        printed to the standard output.
    """
    if port is None:
        port = config.DISTRIBUTED['default_port']
    if authkey is None:
        authkey = config.DISTRIBUTED['default_authkey']
    if num_workers is None:
        num_workers = config.DISTRIBUTED['default_num_workers']

    manager = _create_client_manager(server_ip, port, authkey.encode('utf-8'))

    workers = []
    for i in range(num_workers):
        workers.append(Process(target=_optimization_worker,
                               args=(i + 1,
                                     manager.get_job_queue(),
                                     manager.get_result_queue(),
                                     verbose)
                               )
                       )
        workers[-1].start()

    if verbose:
        print("Connected client '" + socket.gethostname() +
              "' with {0} worker(s) to the hynet server {1}:{2}"
              .format(num_workers, server_ip, port))

    for worker in workers:
        worker.join()


def _create_client_manager(server_ip, port, authkey):
    """
    Return a (connected) manager for a *hynet* optimization client.

    Parameters
    ----------
    server_ip : str
        IP address of the *hynet* optimization server.
    port : int
        TCP port of the *hynet* optimization server.
    authkey : str
        Authentication key for the *hynet* optimization server.

    Returns
    -------
    manager : ClientManager
        Manager object for a *hynet* optimization client.
    """
    class ClientManager(SyncManager):
        """This class manages the synchronization of the queues."""
        pass

    ClientManager.register('get_job_queue')
    ClientManager.register('get_result_queue')

    manager = ClientManager(address=(server_ip, port), authkey=authkey)
    manager.connect()
    _log.debug("Connected client to the hynet optimization server {0}:{1}."
               .format(server_ip, port))
    return manager


def _optimization_worker(worker_id, job_queue, result_queue, verbose):
    """
    Run a worker process for *hynet* optimization jobs.

    This worker process repeatedly reads a job from the job queue, performs
    the optimization, and stores the result to the result queue.

    Parameters
    ----------
    worker_id : int
        ID of this worker process.
    job_queue : queue.Queue
        Queue with pending *hynet* optimization jobs.
    result_queue : queue.Queue
        Queue that receives the optimization results.
    verbose : bool
        If ``True``, some information on activity of the worker is printed to
        the standard output.
    """
    if verbose:
        def show_info(message):
            """Print a message with the current time stamp."""
            print(time.strftime("%Y-%m-%d %H:%M:%S") + " @ " +
                  socket.gethostname() + " | " + message)
    else:
        show_info = _log.debug

    while True:
        try:
            _log.debug("Worker {0}: Waiting for optimization jobs."
                       .format(worker_id))
            job = job_queue.get(block=True, timeout=None)

            show_info("Worker {0}: Received optimization job {1}"
                      .format(worker_id, job.id))
            result_queue.put({job.id: job.process()})
            show_info("Worker {0}: Processed optimization job {1}"
                      .format(worker_id, job.id))
        except queue.Empty:
            _log.debug("Worker {0}: Queue was empty. Resume listening."
                       .format(worker_id))
        except EOFError:
            show_info("Worker {0}: Server was shut down. Exiting..."
                      .format(worker_id))
            return
        except KeyboardInterrupt:
            show_info("Worker {0}: Terminated by the user. Exiting..."
                      .format(worker_id))
            return
        except Exception as exception:
            show_info("Worker {0}: Terminated unexpectedly: {1}"
                      .format(worker_id, str(exception)))
            return
