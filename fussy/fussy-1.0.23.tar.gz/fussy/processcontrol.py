import os,threading,time,logging,signal,errno
from fussy import nbio
log = logging.getLogger( __name__ )

__all__ = [
    'alive',
    'descendants',
    'running_pids',
    'unmanaged',
    
    'kill_kill_kill',
    'kill_children',
    'kill_unmanaged',
    'kill_by_name',
    
    'daemon_thread',
    'wait',
    'current_time',
]

def alive( pid ):
    """Is the given PID responding to signals?"""
    try:
        os.kill( pid, 0 )
    except OverflowError:
        raise ValueError( pid, "Is too large for a pid value")
    except OSError as err:
        if err.args[0] == errno.ESRCH: # no such process
            return False
        elif err.args[0] == errno.EPERM: # likely owned by someone else
            log.warning( "Attempted to send signal to process we cannot signal" )
            return False 
        log.debug( 'Unexpected return code: %s', err )
        return False 
    else:
        return True

def _pgrep_pids( pids ):
    """Cleans up PID listing from pgrep output"""
    return [int(x) for x in pids.strip().splitlines()]    

def descendants( pid=None ):
    """Get all descendants of the current PID
    
    Note: this is a *recursive* calling of a pgrep operation, it is 
    *not* intended for use with extremely deep trees
    
    yields children, then parent
    """
    pid = pid or os.getpid()
    parents, children = proc_map()
    return list(_depth_first(children, pid))

def _depth_first(map, start):
    for child in map.get(start, ()):
        yield child 
        for descendant in _depth_first(map, child):
            yield descendant

def proc_map():
    """Pull out a process map of all processes on the system"""
    procs = [
        x for x in os.listdir('/proc') if x.isdigit()
    ]
    children = {}
    parent = {}
    for proc in procs:
        try:
            fh = open(os.path.join('/proc', proc, 'status'))
        except Exception:
            pass 
        else:
            try:
                for line in fh:
                    if line.startswith('PPid:'):
                        proc, ppid = int(proc, 10), int(line.split(':')[1].strip(), 10)
                        parent[proc] = ppid 
                        children.setdefault(ppid, []).append(proc)
            finally:
                fh.close()
    return parent, children


def kill_children( pid=None ):
    """Kill all children of this process
    
    pid -- if not specified, this process (which isn't very useful, as it 
        will kill the code running this operation)
    
    kill_kill_kill's for each descendants( pid ) and then kill_kill_kill( pid )
    """
    for child in list(descendants( pid )):
        try:
            kill_kill_kill( child )
        except (IOError,OSError):
            # race condition where the child has already exited...
            pass 
    kill_kill_kill( pid )

def describe( pid ):
    """Produce a short description of the PID for use in log messages"""
    try:
        return nbio.Process( ['ps','f','--pid', str(pid)])().decode('utf-8').strip().splitlines()[1]
    except (IndexError,nbio.ProcessError):
        return u'Process #%s'%(pid,)
    
def kill_kill_kill( pid ):
    """Kill pid (with prejudice)
    
    Attempts three times to kill the process with three signals (INT, TERM, KILL)
    for a total of 9 kill attempts.  Exits as soon as alive( pid ) is False.
    
    Waits .1* 2**(attempt) between each signal.
    
    Used when you absolutely *must* be sure that those processes are gone.
    """
    if alive( pid ):
        for attempt in range( 3 ):
            for sig in [signal.SIGINT,signal.SIGTERM,signal.SIGKILL]:
                try:
                    os.kill( pid, sig )
                except OSError as err:
                    if err.args[0] == errno.ESRCH:
                        # yay, it's gone!
                        return True 
                    elif err.args[0] == errno.EPERM:
                        # we can't send signals, no point retrying...
                        return False 
                    else:
                        log.info(
                            "Kill returned unexpected failure: %s", err 
                        )
                wait( 0.1* (2**attempt) )
                if not alive( pid ):
                    return True 
                log.debug( 'PID %s still alive after attempted kill with %s', pid, sig )
    return False

def running_pids( name ):
    """Return pids of all instances of processes named (precisely) name
    
    Uses an exact match on the name
    """
    pids = nbio.Process([
        'pgrep', '-x', name,
    ], good_exit = [0,1])()
    return _pgrep_pids( pids )
def kill_by_name( name ):
    """Kill every process in running_pids( name )"""
    for pid in running_pids( name ):
        log.info( "Killing %s instance %s", name, pid )
        kill_kill_kill( pid )
def unmanaged( name ):
    """Return pids of all instances of processes named name which do not have parents
    
    More precisely, those instances where the process is a child of PID 1.  
    This is used to kill off processes that should normally be run under 
    supervisor or another management/scheduling daemon, but which have now 
    "escaped" due to the death of the parent process.
    
    Matching is by partial match against the whole command line, so 
    'thunder' would match 'thunderbird' and python script names are visible
    """
    pids = nbio.Process([
        'pgrep', '-P','1', '-f', name
    ], good_exit=(0,1))()
    return _pgrep_pids( pids )
def kill_unmanaged( name ):
    """Kill all unmanaged instances of the given process name (and their descendants)
    
    kill_children(pid) for pid in unmanaged( name )
    """
    for pid in unmanaged( name ):
        log.info( "Killing unmanaged %s instance and its children: %s", name, pid )
        kill_children( pid )

def daemon_thread( target, **named ):
    """Create a daemon thread from the named parameters"""
    if 'name' not in named:
        # by default, give the threads names that match the target...
        try:
            named['name'] = getattr(target,'__name__')
        except Exception:
            pass
    thread = threading.Thread( target=target, **named )
    thread.daemon = True 
    assert thread.daemon
    log.info( 'Starting background thread for %s', getattr(target,'__name__',target))
    thread.start()
    assert thread is not None
    return thread 

def wait( duration ):
    """Wait a given duration for some event (for testing, allows us to simulate time)"""
    return time.sleep( duration )
    
def current_time():
    """Time retrieval point (for testing, allows us to simulate time)"""
    return time.time()

