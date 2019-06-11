import ipaddress
import os
import socket
import sys
import warnings
from multiprocessing import Queue, cpu_count, current_process

from schwimmbad import MultiPool as _MultiPool

from ._utils import is_writable, mute_stderr

try:
    from mpipool import Pool as _MPIPool
except ImportError:

    class _MPIPool(object):
        def __getattr__(self, name):
            raise ImportError("you must run 'pip install mpipool' first.")


if sys.version_info.major == 2:
    ModuleNotFoundError = None
    unicode = str


class UMultiPool(_MultiPool):

    def __str__(self):
        return "MultiPool"


class MPIPool(_MPIPool):

    def __str__(self):
        return "MPIPool"


def runs_on_euler_node():
    # ip ranges according to https://scicomp.ethz.ch/wiki/Cluster_IP_ranges#Euler
    try:
        ip4_text = ipaddress.IPv4Address(socket.gethostbyname(socket.gethostname()))
        return any(
            ip4_text in ipaddress.IPv4Network(network)
            for network in ("10.205.0.0/19", "10.205.96.0/19")
        )
    except Exception:
        ip4_text = ipaddress.IPv4Address(
            unicode(socket.gethostbyname(socket.gethostname()))
        )
        return any(
            ip4_text in ipaddress.IPv4Network(network)
            for network in (unicode("10.205.0.0/19"), unicode("10.205.96.0/19"))
        )


def runs_on_single_euler_node():
    resources = os.environ.get("LSB_EFFECTIVE_RSRCREQ", "")
    return "span[hosts=1]" in resources


def runs_with_mpi():
    return any(
        n.startswith(prefix)
        for n in os.environ.keys()
        for prefix in ("MPIEXEC_", "OMPI_COMM_WORLD_")
    )


def mpi_size():
    if runs_with_mpi():
        from mpi4py import MPI

        return MPI.COMM_WORLD.size
    return None


def _inject_rank_information(path, rank):
    if "{worker_id" in path:
        path = path.format(worker_id=rank)
    return path


def check_and_fix_path(path, rank):

    if rank is not None:
        path = _inject_rank_information(path, rank)

    path = os.path.abspath(path)
    folder = os.path.dirname(path)

    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    if os.path.exists(path):
        raise IOError("{} already exists".format(path))

    if not is_writable(path):
        raise IOError(
            "can not write to {}. please check if folder {} is writable".format(
                path, folder
            )
        )
    return path


def get_rank():
    if runs_with_mpi():
        from mpi4py import MPI

        return MPI.COMM_WORLD.rank

    return getattr(current_process(), "rank", 0)  # main process has no rank set


def core_count():
    lsb_cores = os.environ.get("LSB_MAX_NUM_PROCESSORS")
    if lsb_cores is None:
        return cpu_count()
    return int(lsb_cores)


def mpi_tasks():
    return _mpi_query("size", default=1)


def _mpi_query(attribute, default=None):

    if not runs_with_mpi():
        return None
    try:
        from mpi4py import MPI
    except ImportError as e:
        if ModuleNotFoundError is not None and isinstance(e, ModuleNotFoundError):
            warnings.warn("mpi4py is not installed.")
            return default
        warnings.warn("mpi4py is installed, but I can not import it: {}.".format(e))
        return default
    return getattr(MPI.COMM_WORLD, attribute)  # pragma: no cover


def mpi_rank():
    return _mpi_query("rank", default=1)


def check_if_walkers_number_of_cores_fit(n_walkers, n_workers):

    if n_workers == 1:
        warnings.warn("only one worker available. switch to serial mode.")
        return False

    if n_walkers < n_workers:
        msg = (
            "the number of walkers {n_walkers} is less than the number of workers "
            "{n_workers}.".format(n_walkers=n_walkers, n_workers=n_workers)
        )
        warnings.warn(msg)

    else:
        if n_walkers % n_workers:
            msg = (
                "uhammer runs with {n_workers} workers for {n_walkers} walkers. "
                "resource usage is best if the number walkers is a multiple of number "
                "of workers.".format(n_walkers=n_walkers, n_workers=n_workers)
            )
            warnings.warn(msg)
    return True


def get_pool_for(n_walkers):

    pool = _get_pool(n_walkers)
    check_pool(pool, n_walkers)
    return pool


def check_parallel(parallel):
    if not parallel and runs_with_mpi():
        warnings.warn(
            "looks like you use mpirun to run your code, but set parallel=False"
        )


def _set_rank(q):
    current_process().rank = q.get()


def _get_pool(n_walkers):

    tasks = mpi_tasks()

    if tasks is not None and tasks >= 2:  # at least one master and one worker
        return MPIPool()  # pragma: no cover

    n_workers = core_count() - 1

    # it does not make sense to use more cores than walkers
    n_cores = min(n_workers, n_walkers)

    # setup queue to assign rank attribut to all worker processes:
    q = Queue(n_cores)
    for rank in range(1, n_cores + 1):
        q.put(rank)

    with mute_stderr():
        # might cause MPI related error message, even without mpirun:
        pool = UMultiPool(n_cores, initializer=_set_rank, initargs=(q,))
        current_process().rank = 0

    return pool


def check_pool(pool, n_walkers):

    omp_threads = os.environ.get("OMP_NUM_THREADS", 1)
    try:
        omp_threads = int(omp_threads)
    except ValueError:
        raise RuntimeError(
            "OMP_NUM_THREADS has value {} which is not an integer".format(omp_threads)
        )
    if omp_threads > 1:
        warnings.warn(
            "you set OMP_NUM_THREADS to {}. this could cause very slow execution "
            "due to oversubscription. to fix this set OMP_NUM_THREADS to 1".format(
                omp_threads
            )
        )

    check_passed = check_if_walkers_number_of_cores_fit(n_walkers, pool.size)
    if not check_passed:
        return None

    if isinstance(pool, MPIPool):
        return  # pragma: no cover

    if runs_on_euler_node():

        if pool.size > 35:
            warnings.warn(
                "on euler best use -n 24 or -n 36 for scalability. "
                "larger numbers don't increase performance."
            )
        if not runs_on_single_euler_node():
            warnings.warn(
                "better run the job with '-R fullnode' to benefit "
                "from multicore parallelisation."
            )
