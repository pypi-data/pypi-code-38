import dill
import numpy
import math
import itertools
import os
import inspect
import time
import sys
import typing
import subprocess
import pathos
import builtins
import argparse
import multiprocessing

from swutil.misc import split_list, random_string, chain, cmd_exists
from swutil.validation import In, Bool, Function, validate_args, Passed, NotPassed,Function,String
Pool = pathos.multiprocessing.ProcessingPool
class Locker:
    def __init__(self):
        self.mgr = multiprocessing.Manager()
    def get_lock(self):
        return self.mgr.Lock()

def wrap_mpi(f):
    info = argparse.Namespace()
    info.wrap_MPI = True
    def _lam(*args,**kwargs):
        return _MultiProcessorWrapper_call(args,kwargs,f,_MPI_processor,_MPI_finalizer,info)
    return _lam

@validate_args(warnings=False)
def EasyHPC(backend:In('MP', 'MPI')|Function='MP',
            n_tasks:In('implicitly many', 'many', 'one', 'count')='one',#Count is special case of implicitly many where it is already known how to split jobs 
            n_results:In('many', 'one')='one',
            aux_output:Bool=True,  # Parellelize only first entry of n_results is tuple
            reduce:Function=None,
            split_job=NotPassed,
            parallel = True,#If false, use the wrapper functionality of EasyHPC but don't actually use multiprocessing
            method = None,
            pool = None
            ):
        '''
        :param n_tasks: How many tasks does the decorated function handle? 
        :param n_results: If the decorated function handles many tasks at once, are the results reduced (n_results = 'one') or not (as many results as tasks)?
        :param reduce: Function that reduces multiple outputs to a single output
        :param splitjob: Function that converts an input (to the decorated function) that represents one large job to two smaller jobs

        NOTE: don't turn this into a class, you'll run into strange pickling errors
        '''
        self = argparse.Namespace()
        direct_call =  (~String&Function).valid(backend)
        if direct_call:
            f = backend
            backend = 'MP'
        if backend == 'MPI': 
            self.processor = _MPI_processor
            self.finalizer = _MPI_finalizer
        if backend == 'MP':
            self.processor = _MP_processor
            self.finalizer = None
        self.info = argparse.Namespace()
        self.info.n_tasks = n_tasks
        self.info.n_results = n_results
        self.info.parallel = parallel
        self.info.reduce = reduce
        self.info.wrap_MPI = False
        self.info.aux_output = aux_output 
        self.info.method = method
        self.info.pool = pool or Pool()
        self.info.split_job = split_job
        if self.info.n_tasks == 'implicitly many':
            if self.info.n_results == 'many':
                raise ValueError('Do not know how to handle functions that handle implicitly many tasks and return multiple results')
            if NotPassed(self.info.split_job):
                raise ValueError('Functions handling implicitly many tasks must specify how to split a job using `split_job`')
        if direct_call:
            def _lam(*args,**kwargs):
                return _MultiProcessorWrapper_call(args,kwargs,f,self.processor,self.finalizer,self.info)
            return _lam
        return lambda f: _easy_hpc_call(f,self)

def _easy_hpc_call(f,self):
    _easy_hpc_info = (f,self.processor,self.finalizer,self.info)
    def _lam(*args,**kwargs):
        return _MultiProcessorWrapper_call(args,kwargs,f,self.processor,self.finalizer,self.info)
    return _lam

def _MultiProcessorWrapper_call(args,kwargs,f,processor,finalizer,info):
        if info.method is None:
            info.method = hasattr(f,'__qualname__') and '.' in f.__qualname__ and '<locals>' not in f.__qualname__ and not inspect.ismethod(f)#the last check seems to be contradictory, however, the info.method refers to situations when the decorator is applied directly at the mehtod definition, not later on (e.g. in the __init__) and in these situations inspect.ismethod actually returns False
        if '__second_call' in kwargs:
            kwargs.pop('__second_call')
            return f(*args, **kwargs)
        if args:
            if info.method:
                M,args = args[1],args[0:1]+args[2:]
            else:
                M, args = args[0], args[1:]
        else:
            if not info.wrap_MPI:
                raise ValueError('Must specify task(s)')
            M, args = NotPassed, NotPassed               
        if info.n_tasks in ['many','one']:
            M = list(M)
            if len(M) == 1:
                return _reduce_first_output(info,[[f(args[0],M[0],*args[1:], **kwargs) if info.method else f(M[0],*args,**kwargs)]])#TODO this currently doesn't run parallel even if parallel is demanded, might cause debugging headaches
        f_path = inspect.getsourcefile(f)
        f_name = f.__name__
        ID = '.easyhpc_' + f_name + '_' + str(time.time()) + '_' + random_string(8)#TODO: use module tempfile
        r, ID = processor(args, kwargs, M, f, f_path, f_name, ID, info)
        out = _reduce_first_output(info, r)
        if finalizer:
            finalizer(ID)
        return out

def _MPI_processor(args, kwargs, M, f, f_path, f_name, ID, info):
    from mpi4py import MPI
    if info.wrap_MPI:
        child = MPI.COMM_SELF.Spawn(
            sys.executable,
            args=['-c', 'import swutil.hpc;swutil.hpc._MPI_worker(mpi_child=True)'],
            maxprocs=1)
        child.bcast((args, kwargs, M, f_path, f_name, info), root=MPI.ROOT)
        r = child.recv(source=MPI.ANY_SOURCE)
        child.Disconnect()
    elif MPI.COMM_WORLD.Get_size() == 1 and MPI.Comm.Get_parent() == MPI.COMM_NULL:
        if cmd_exists('srun'):
            mpi_executable = 'srun'
        else:
            mpi_executable = 'mpiexec'
        command = ' '.join((mpi_executable,sys.executable,'-c "import swutil.multiprocessing;swutil.multiprocessing._MPI_worker(ID=\'{}\')"'))
        command = command.format(ID)
        with open(ID + '_task', 'wb') as file:
            dill.dump((args, kwargs, M, f_path, f_name, info), file)
        subprocess.check_call(command, shell=True) 
        with open(ID + '_results', 'rb') as file:
            r = dill.load(file)
    else:
        r = _MPI_worker(pure_python=(args, kwargs, M, f_path, f_name, info))
    return r, ID

def _MP_processor(args, kwargs, M, f, f_path, f_name, ID, info):
    if info.parallel:
        if info.pool is not None:
            p = info.pool
        else:
            p = Pool()
        try:
            p.map(lambda:None,[])
        except ValueError:
            p.restart()
        N = p.ncpus
        map = p.map
    else:
        map = lambda f,x: [f(x) for x in x]
        N = 1
    #t = info.pool
    #del info.pool
    r = map(_MP_worker, [(f, args, kwargs, M, n, N, info) for n in range(N)])
    #info.pool = t
    return r, ID

def _MPI_worker(ID=None, pure_python=False, mpi_child=False):
    from mpi4py import MPI
    if mpi_child:
        parent = MPI.Comm.Get_parent()
        (args, kwargs, M, f_filename, f_name, info) = parent.bcast(None, root=0)
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        N = comm.Get_size()
    elif pure_python:
        (args, kwargs, M, f_filename, f_name, info) = pure_python
        N = 1
        rank = 0
    else:
        with open(ID + '_task', 'rb') as file:
            (args, kwargs, M, f_filename, f_name, info) = dill.load(file)
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        N = comm.Get_size()
    rr = _common_work(_load_f(f_filename,f_name), M, N, rank, args, kwargs, info)
    if mpi_child:
        r = comm.gather(rr, 0)
        if comm.Get_rank() == 0:
            parent.send(r, dest=0)
        parent.Disconnect()  
    elif pure_python:
        r = [rr]
        return r
    else:
        r = comm.gather(rr, 0)
        if comm.Get_rank() == 0:
            with open(ID + '_results', 'wb') as file:
                dill.dump(r, file)
        
def _MP_worker(arg):
    (f, args, kwargs, M, rank, N, info) = arg
    numpy.random.seed(rank)#TODO: replace by randomint+rank
    return _common_work(f, M, N, rank, args, kwargs, info) 

def _load_f(f_filename,f_name):           
    import importlib.util
    spec = importlib.util.spec_from_file_location("module.name", f_filename)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    return getattr(foo, f_name)

def _common_work(f,M, N, rank, args, kwargs, info):
    if info.wrap_MPI:
        jobs = [M] * N
    else:
        if info.n_tasks == 'count':
            jobs = [int(math.ceil(M / N))] * N
        elif info.n_tasks in ('many', 'one'):
            M = list(M)
            jobs = split_list(M, N)
        elif info.n_tasks == 'implicitly many':
            jobs = [M]
            while len(jobs) < N:
                if 2*len(jobs)<=N:
                    jobs = list(itertools.chain(*[info.split_job(job) for job in jobs]))
                else:
                    need=N-len(jobs)
                    jobs=list(itertools.chain(*([info.split_job(job) for job in jobs[:need]]+[jobs[need:]])))
    if hasattr(f,'__name__') and f.__name__ == '_MultiProcessorWrapper_call':
        kwargs['__second_call'] = True
    if not info.wrap_MPI and info.n_tasks == 'one':
        if Passed(M):
            return  [f(args[0],job,*args[1:], **kwargs) if info.method else f(job,*args,**kwargs) for job in jobs[rank]]
        else:
            return [f(**kwargs) for job in jobs[rank]]
    else:
        if Passed(M):
            out= f(jobs[rank], *args, **kwargs)
            return out
        else:
            return f(**kwargs)


def _reduce_first_output(info, r):
    aux_output = False if info.wrap_MPI else (info.aux_output and isinstance(r[0], tuple))
    numpy_mode = isinstance(r[0], numpy.ndarray) or aux_output and isinstance(r[0][0], numpy.ndarray)
    concatenate = numpy.concatenate if numpy_mode else lambda r: list(itertools.chain(*r))
    if info.reduce is None:
        info.reduce = lambda x:x
    if info.wrap_MPI:
        reduce = lambda r: r[0]
    else:
        if info.n_tasks == 'one' and info.n_results == 'one':  # Each entry of r is list
            reduce = chain(info.reduce, concatenate)
        if info.n_tasks in ('implicitly many', 'many', 'count') and info.n_results == 'one':  # Each entry of r is singleton. Need reduce
            reduce = info.reduce  # maybe f should be used as info.reduce by default if info.n_tasks is 'many'. 
                                # probably jobs should be passed to info.reduce if info.n_tasks is 'implicitly many'
        if info.n_tasks in ('implicitly many', 'many', 'count') and info.n_results == 'many':  # In future, first apply reduce to each element of r and then to resulting r
            reduce = chain(info.reduce, concatenate)
    if aux_output:
        return (reduce([rr[0] for rr in r]),) + r[0][1:]
    else:
        return reduce(r)

def _MPI_finalizer(ID): 
    try:
        os.remove(ID + '_results')
    except FileNotFoundError:
        pass
    try:
        os.remove(ID + '_task') 
    except FileNotFoundError:
        pass
