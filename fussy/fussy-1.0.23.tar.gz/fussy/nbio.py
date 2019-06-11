"""Wraps subprocess with pipe semantics and generator based multiplexing

pipe = open( somefile, 'rb' ) | nbio.Process( ['grep','blue'] ) | nbio.Process( ['wc','-l'])

"""
import os, select, fcntl, time, sys, logging, subprocess, errno, collections
log = logging.getLogger( __name__ )
from ._shims import bytes, unicode, file_base, next, long

DEFAULT_READ_BLOCK = 1024*64

def set_non_blocking( fh ):
    """Set this file handle to non-blocking mode"""
    current = fcntl.fcntl( fh, fcntl.F_GETFL )
    fcntl.fcntl( fh, fcntl.F_SETFL, current | os.O_NONBLOCK )
    return fh

class _DidNothing( object ):
    """Returned when a subprocess didn't do anything"""
    def __bool__( self ):
        return False
    __nonzero__ = __bool__
DID_NOTHING = _DidNothing()

class NBIOError( RuntimeError ):
    """Base class for nbio errors"""
class ProcessError( NBIOError ):
    """Called process returned an error code
    
    Attributes:
    
        process -- the Process (if applicable) which raised the error
        exitcode -- exit code from the process if available
    """
    process = None
    exitcode = None
class Timeout( NBIOError ):
    """Called process did not complete within specified timeout
    
    Attributes:
    
        process -- the Process (if applicable) which raised the error
    
    """
    process = None

def pause( duration ):
    """Allow tests to override sleeping using globalsub"""
    time.sleep( duration )

class Pipe( object ):
    """Pipe of N processes which all need to process data in parallel"""
    pause_on_silence = 0.01
    started = False
    def __init__( self, *processes ):
        self.processes = []
        if processes:
            self.append( self.get_component(processes[0]) )
            for process in processes[1:]:
                self.__or__( process )
    def __repr__( self ):
        return '%s => %s'%( 
            self.__class__.__name__, ' | '.join( [str(p) for p in self.processes]) 
        )
    def __getitem__(self, index):
        """Retrieve a particular item in the pipe"""
        return self.processes[index]
    def __len__( self ):
        """Return the number of items in this pipe"""
        return len( self.processes )
        
    def __iter__( self, timeout=None ):
        """Iterate over the processes in the pipe
        
        If the stdout/stderr of the processes is not captured, then we will 
        yield the results in whatever chunk-size is yielded from the individual 
        processes.
        
        If all of the processes yield DID_NOTHING in a particular cycle, then the 
        pipe will do a pause() for self.pause_on_silence (normally passed into the 
        __call__) before the next iteration.
        """
        if timeout:
            until = time.time() + timeout
        try:
            self.started = True
            iterables = [ iter(process) for process in self.processes ]
            crashed = False
            while iterables and not crashed:
                exhausted = []
                something_happened = 0
                for iterable in iterables:
                    try:
                        child_result = next(iterable)
                        if child_result is DID_NOTHING:
                            # we did nothing during this iteration
                            pass
                        elif child_result:
                            something_happened += 1
                            yield child_result
                    except StopIteration:
                        exhausted.append( iterable )
                    except (KeyboardInterrupt,Exception):
                        # Have the *first* item that failed raise the error, 
                        # and only if they don't, raise this error...
                        for item in self.processes:
                            item.check_exit()
                        raise
                if not something_happened:
                    for item in self.processes:
                        if hasattr( item, 'poll' ):
                            item.poll()
                # check for a process/pipe/file failure...
                for done in exhausted:
                    while done in iterables:
                        iterables.remove( done )
                if not something_happened:
                    try:
                        pause( self.pause_on_silence )
                    except (KeyboardInterrupt,Exception) as err:
                        new_err = ProcessError( 
                            "Exception while paused: %s"%(err,)
                        )
                        new_err.process = self 
                        raise new_err
                if timeout:
                    if time.time() > until:
                        raise Timeout( self, timeout )
        finally:
            self.kill()
    def __call__( self, pause_on_silence=0.01, timeout=None ):
        """Iterate over this pipeline, returning combined results as a string
        """
        result = []
        self.pause_on_silence = pause_on_silence
        try:
            for item in self.__iter__( timeout=timeout ):
                if item:
                    result.append( item )
            return b"".join( result )
        except (KeyboardInterrupt,Exception) as err:
            err.output = result
            raise
    def append( self, process ):
        """Add the given PipeComponent to this pipe (note: does not connect stdin/stdout)"""
        assert isinstance( process, PipeComponent ), process
        self.processes.append( process )
    def prepend( self, process ):
        """Add the given PipeComponent to this pipe (note: does not connect stdin/stdout)"""
        assert isinstance( process, PipeComponent ), process
        self.processes.insert( 0, process )
    @property
    def first( self ):
        """Retrieves the first item in the pipe"""
        if self.processes:
            return self.processes[0]
        raise IndexError( "No processes yet in this pipeline" )
    @property
    def last( self ):
        """Retrieves the last item in the pipe"""
        if self.processes:
            return self.processes[-1]
        raise IndexError( "No processes yet in this pipeline" )

    def __or__( self, other ):
        """Pipe our output into a process, callable or list"""
        other = self.get_component( other )
        last = self.last 
        # special cases for piping process-to-process 
        both_processes = isinstance(last,Process) and isinstance( other, Process )
        both_processes = False
        if both_processes and not other.started and not last.started:
            log.info( 'Direct pipe %s -> %s', last, other )
            last.blocking_stdout()
            other.direct_pipe( last.stdout, 'stdin' )
        else:
            last.iterables.append(
                other.iter_write( self.last.iter_read() )
            )
        self.append( other )
        return self
    def __ror__( self, other ):
        """Pipe output of other into our first item"""
        other = self.get_component( other )
        self.first.iterables.append(
            self.first.iter_write( 
                other.iter_read()
            )
        )
        self.prepend( other )
        return self

    def __gt__( self, other ):
        """Pipe our output into a file
        """
        if isinstance( other, (bytes,unicode)):
            if other not in ('','-'):
                return self.__or__( open(other,'wb') )
            else:
                return self.__or__( other )
        else:
            return self.__or__( other )
    def __lt__( self, other ):
        """Pipe input from a named file"""
        if isinstance( other, (bytes,unicode)):
            if other not in ('','-'):
                return self.__ror__( open(other,'rb') )
            else:
                return self.__ror__( other )
        else:
            return self.__ror__( other )
    def get_component( self, other ):
        """Given a python object other, create a PipeComponent for it
        
        The purpose of this method is to allow for fairly "natural" 
        descriptions of tasks.  You can pipe to or from files, 
        to or from the string '-' (stdin/stdout), to the 
        string '' (collect stdout), or from a regular string (which is 
        treated as input).  You can pipe iterables into a pipe,
        you can pipe the result of pipes into callables.
        """
        if isinstance( other, PipeComponent ):
            pass 
        elif isinstance( other, file_base ):
            other = FileComponent( other )
        elif isinstance( other, (bytes,unicode)):
            if other == '-':
                other = FileComponent( sys.stdout, sys.stdin )
            elif other == '':
                other = IterComponent( )
            else:
                other = IterComponent( [other] )
        elif hasattr( other, '__iter__'):
            other = IterComponent( other )
        elif isinstance(callable, collections.Callable):
            other = FunctionComponent( other )
        if not isinstance( other, PipeComponent ):
            raise TypeError( """Require a PipeComponent-compatible object, got: %s"""%(other,) )
        return other 
    def kill( self ):
        for process in self.processes:
            if hasattr( process, 'kill' ):
                try:
                    process.kill()
                except (KeyboardInterrupt,Exception):
                    log.warning(
                        "Unable to kill process: %s", process,
                    )
    

class PipeComponent( object ):
    live = True
    def __init__( self ):
        self.iterables = []
    def __iter__( self ):
        iterables = [ iter(x) for x in self.iterables ]
        while iterables and self.live:
            something_happened = 0
            exhausted = []
            for iterable in iterables:
                try:
                    child_result = next(iterable)
                    if child_result is DID_NOTHING:
                        pass
                    elif child_result:
                        something_happened += 1
                        yield child_result
                except StopIteration as err:
                    exhausted.append( iterable )
                except (KeyboardInterrupt,Exception) as err:
                    err.args += (self,)
                    raise 
            for done in exhausted:
                while done in iterables:
                    iterables.remove( done )
            if not something_happened:
                yield DID_NOTHING
        self.check_exit()
    def check_exit( self ):
        pass
    def iter_read( self ):
        """Iterate reading from stdout"""
        raise TypeError( "Do not have an iter read for %s"%(self.__class__, ))
    def iter_write( self, source ):
        raise TypeError( "Do not have an iter write for %s"%(self.__class__, ))
    

class FileComponent( PipeComponent ):
    def __init__( self, filein,fileout=None ):
        self.stdin = filein
        self.stdout = fileout or filein 
        super( FileComponent, self ).__init__()
    def iter_read( self ):
        return reader( self.stdout, exit_on_finish=True )
    def iter_write( self, source ):
        return writeiter(
            source,
            self.stdin,
        )
    def __repr__( self ):
        if self.stdin != self.stdout:
            return '%s/%s'%( self.stdout, self.stdin )
        else:
            return 'file( %r, %r )'%( self.stdin.name, self.stdin.mode )
    
class Process( PipeComponent ):
    """A particular process in a Pipe
    
    Processes are the most common entry point when using nbio, you 
    create processes and pipe data into or out of them as appropriate
    to create Pipes.
    
    Under the covers the Process runs subprocess.Popen, and it accepts most of 
    the fields subprocess.Popen does.  By default it captures stdout and pipes 
    data into stdin.  If nothing is connected to stdin then stdin is closed on 
    the first iteration of the pipe.  If nothing is connected to stdout or 
    stderr (if stderr is captured) then the results will be returned to the 
    caller joined together with ''
    
    The implication is that if you do not want to store all of the results 
    in RAM, you need to "sink" the results into a process or file, or *not*
    capture the results (pass False for stdout or stderr).
    """
    stdin_needed = False
    stdout_needed = False 
    stderr_needed = False
    STDOUT = -1
    by_line = False
    def __init__( self, command, stderr=False, stdout=True, stdin = True,**named ):
        """Initialize the Process 
        
        command -- subprocess.Popen command string or list
                   if a string, and "shell" is not explicitly set, 
                   then will set "shell=True"
                   
        stdin -- whether to provide stdin writing 
        
        stdout -- whether to capture stdout 
        
        stderr -- whether to capture stderr, if -1, then combine stdout and stderr 
        
        good_exit -- if provided, iterable which provides the set of good exit codes 
                     which will not raise ProcessError when encountered
                     
        by_line -- if provided, will cause the output to be line-buffered so that 
                   only full lines will be reported, the '\\n' character will be used to 
                   split the output, so there will be no '\\n' character at the end of each 
                   line.
                   
        named -- passed to the subprocess.Popen() command 
        
        """
        if isinstance( command, (bytes,unicode)):
            if not 'shell' in named:
                named['shell'] = True 
        self.command = command 
        if 'good_exit' in named:
            self.good_exit = named.pop( 'good_exit' )
        else:
            self.good_exit = [0]
        if 'by_line' in named:
            self.by_line = named.pop( 'by_line' )
        named['stdin'],named['stdout'],named['stderr'] = stdin,stdout,stderr
        self.named_args = named
        try:
            self.no_descendent_kill = named.pop( 'no_descendent_kill' )
        except KeyError:
            self.no_descendent_kill = False
        super( Process, self ).__init__( )
    def __unicode__( self ):
        return u'%s( %r )'%( self.__class__.__name__, self.command )
    __repr__ = __unicode__
    
    @property
    def stderr( self ):
        return self.pipe.stderr
    @stderr.setter
    def stderr( self, new ):
        if self._pipe:
            raise ProcessError( 'Cannot set stderr after pipe start' )
        self.named_args['stderr'] = new 
    @property
    def stdout( self ):
        return self.pipe.stdout
    @stdout.setter
    def stdout( self, new ):
        if self._pipe:
            raise ProcessError( 'Cannot set stdout after pipe start' )
        self.named_args['stdout'] = new 
    @property
    def stdin( self ):
        return self.pipe.stdin
    @stdin.setter
    def stdin( self, new ):
        if self._pipe:
            raise ProcessError( 'Cannot set stdin after pipe start' )
        self.named_args['stdin'] = new 

    use_blocking_stdout = False
    def blocking_stdout( self ):
        self.use_blocking_stdout = True
    def direct_pipe( self, file, key='stdout' ):
        """Directly pipe stdout/stderr/stdin to/from the file"""
        setattr( self, key, file )
        setattr( self, '%s_wanted'%(key,), True )
        self.iterables.append( self.iter_wait() )
        return file
    
    @property 
    def pid( self ):
        return self.pipe.pid
    @property 
    def started( self ):
        return self._pipe is not None
    _pipe = None
    @property 
    def pipe( self ):
        if self._pipe is None:
            self._pipe = self._start_pipe( 
                **self.named_args 
            )
        return self._pipe
    def start(self):
        """Trigger to start the process immediately"""
        # yes, side-effects are ick...
        self.pipe
        return self
    
    def _start_pipe( self, **named ):
        """Start the captive process (internal operation)"""
        for key in ('stdin','stdout','stderr'):
            value = named.get(key)
            if value == -1:
                value = subprocess.STDOUT
            elif hasattr( value, 'fileno' ):
                log.info( 'Using existing file: %s', value )
                value = value
            else:
                value = [None,subprocess.PIPE][bool(value)]
            named[key] = value 
        
        pipe = subprocess.Popen(
            self.command, 
            **named
        )
        for key in ('stdin','stdout','stderr'):
            if not hasattr(named[key],'fileno'):
                if key == 'stdout' and self.use_blocking_stdout:
                    log.info( 'Using blocking %s', key )
                    continue 
                    #pass
                fh = getattr( pipe, key, None )
                if fh is not None:
                    set_non_blocking( fh )
            else:
                log.info( 'Using blocking %s', key )
        return pipe
    def __iter__( self ):
        """Iterate over the results of the process (normally done by the Pipe)"""
        if not self.stdout_needed:
            # nothing has been hooked to stdout
            if self.stdout:
                # but stdout was captured, so we need to consume it to prevent deadlocks
                self.iterables.append(
                    self.iter_read()
                )
        if not self.stderr_needed:
            # nothing has been hooked to stderr
            if self.stderr:
                self.iterables.append(
                    self.iter_read_err( )
                )
        if not self.stdin_needed:
            # nothing is being sent in, so input is finished...
            close( self.stdin )
        return super( Process, self ).__iter__()
    
    def __or__( self, other ):
        """Pipe our output into a process, callable or list
        
        pipe = Pipe( Process( 'cat test.txt' ) | Process( 'grep blue' ) | [] )
        pipe()
        """
        self.stdout_needed = True 
        if isinstance( other, Pipe ):
            # Pipe our output into the pipe, add ourselves to the start of pipe...
            return other.__nor__( self )
        else:
            pipe = Pipe( self )
            return pipe.__or__( other )
        
    def __ror__( self, other ):
        """Pipe other into self"""
        self.stdin_needed = True 
        if isinstance( other, Pipe ):
            return other.__or__( self )
        else:
            pipe = Pipe( self )
            return pipe.__ror__( other )
    def __gt__( self, other ):
        """Pipe our output into a filename"""
        pipe = Pipe( self )
        return pipe.__gt__( other )
    def __lt__( self, other ):
        """Pipe our input from a filename"""
        pipe = Pipe( self )
        return pipe.__lt__( other )
    def __call__( self, *args, **named ):
        """Create a Pipe and run it with just this item as its children"""
        pipe = Pipe( self )
        return pipe( *args, **named )
        
    def poll( self ):
        return self.pipe.poll()
    
    def check_exit( self ):
        """Check our exit code"""
        if self.pipe.returncode is None:
            exitcode = self.pipe.poll()
        else:
            exitcode = self.pipe.returncode
        if exitcode is None or exitcode < 0:
            try:
                if not self.no_descendent_kill:
                    from fussy.processcontrol import kill_children
                    kill_children( self.pipe.pid )
                else:
                    self.kill()
                    
            except OSError as err:
                if err.errno == errno.ESRCH:
                    # we exited...
                    pass 
                else:
                    raise
            exitcode = self.pipe.poll()
        if exitcode is None:
            log.error(
                "Process %s appears not to have exited properly", self 
            )
        elif exitcode not in self.good_exit:
            err = ProcessError( 
                "Process %s returned error code %s"%( self.command, exitcode, ),
            )
            err.process = self 
            err.exitcode = exitcode
            raise err

    def iter_read( self ):
        """Create the thing which iterates our read operation"""
        self.stdout_needed = True
        output = reader( self.stdout )
        if self.by_line:
            output = by_line( output )
        return output
    def iter_read_err( self ):
        self.stderr_needed = True 
        output = reader( self.stderr )
        if self.by_line:
            output = by_line( output )
        return output
    def iter_write( self, source ):
        """Create a thing which will read from source and write to us"""
        self.stdin_needed = True
        return writeiter(
            source,
            self.stdin,
        )
    def iter_wait( self ):
        while self.pipe.poll() == None:
            yield DID_NOTHING
    def kill( self ):
        """Kill our underlying subprocess.Popen"""
        try:
            return self.pipe.kill( )
        except OSError:
            # we've already died/closed...
            pass 
    
class FunctionComponent( PipeComponent ):
    def __init__( self, function ):
        self.function = function 
        super( FunctionComponent, self ).__init__()
    def iter_read( self ):
        yield self.function()
    def iter_write( self, source ):
        return caller( source, self.function )
    def __str__( self ):
        return str( self.function )

class IterComponent( PipeComponent ):
    def __init__( self, iterable=None  ):
        self.iterable = iterable 
        super( IterComponent, self ).__init__()
    def iter_read( self ):
        return self.iterable
    def iter_write( self, other ):
        return other 
    def __repr__( self ):
        if self.iterable:
            return str( self.iterable )
        else:
            return '<str>'

def collector( iterable, target ):
    return caller( iterable, target.append )
def caller( iterable, target ):
    for item in iter(iterable):
        if item:
            target( item )
        yield item

#def pipeline( *commands ):
#    pipe = []
#    previous_stdout = subprocess.PIPE
#    for command in commands:
#        pipe.append( subprocess.Popen( command, stdin=previous_stdout, stdout=subprocess.PIPE ))
#        previous_stdout = pipe[-1].stdout 
#    return pipe

def writeiter( iterator, fh ):
    """Write content from iterator to fh
    
    To write a file from a read file:
    
    .. code-block:: python
    
        writeiter(
            reader( open( filename )),
            fh 
        )
    
    To write a request.response object into a tar pipe iteratively:
    
    .. code-block:: python
    
        writeiter( 
            response.iter_content( DEFAULT_READ_BLOCK, decode_unicode=False ),
            pipe 
        )
    """
    total_written = 0
    assert hasattr( iterator, '__iter__'), iterator
    for content in iterator:
        if content and isinstance( content, (bytes,unicode)):
            for block_written in writer( content, fh ):
                if block_written is DID_NOTHING:
                    yield block_written
                else:
                    total_written += block_written
                    yield None
        else:
            yield DID_NOTHING
    #log.debug( 'Closing %s after %s bytes', fh, total_written )
    close( fh )

def writer( content,fh, encoding='utf8', block_size=4096 ):
    """Continue writing content (string) to fh until content is consumed
    
    Used by writeiter to writing individual bits of content to the fh
    """
    if hasattr( fh, 'raw' ):
        fh = fh.raw
    fp = fileno( fh )
    if isinstance( content, unicode ):
        content = content.encode( encoding )
    assert isinstance( content, bytes ), """Can only write byte values: %r"""%(content)
    for block in string_blocks( content, block_size=block_size ):
        while block:
            written = 0
            try:
                written = os.write( fp, block )
            except OSError as err:
                if err.errno == errno.EWOULDBLOCK:
                    yield DID_NOTHING 
                else:
                    log.warning( "OS Error writing: %s", err )
                    return
            except (IOError,ValueError) as err:
                log.warning( "Error while writing: %s", err )
                return
            if not written:
                #log.debug( 'Unable to write' )
                yield DID_NOTHING
            else:
                #log.debug( 'Wrote: %s', written )
                block = block[written:]
                yield written
        
def reader( fh, blocksize = DEFAULT_READ_BLOCK, exit_on_finish=False ):
    """Produce content blocks from fh without blocking
    """
    if hasattr( fh, 'raw' ):
        fh = fh.raw
    try:
        fd = fileno( fh )
    except ValueError as err:
        return 
    while not fh.closed:
        try:
            rr,rw,re = select.select([fh],[],[],0)
            if rr:
                result = os.read(fd, blocksize )
                if result == b'':
                    if exit_on_finish:
                        close(fh)
                        return
                    break
            else:
                result = DID_NOTHING
        except ValueError as err:
            break 
        except (IOError,OSError) as err:
            if err.args[0] in ( errno.EWOULDBLOCK,):
                if fh.closed:
                    break
                yield DID_NOTHING
            else:
                raise 
        else:
            yield result 
    close( fh )

def fileno( fh ):
    "Determine the fileno for the file-like thing"
    if hasattr( fh, 'raw' ):
        fh = fh.raw
    if hasattr( fh, 'fileno' ):
        return fh.fileno()
    return fh
def close( fh ):
    """Close the file/socket/closable thing"""
    if fh is sys.stdout or fh is sys.stderr:
        return
    if hasattr( fh, 'close'):
        errcode = fh.close()
    else:
        fn = fileno( fh )
        if fn and isinstance( fn, (int,long)):
            errcode = os.close( fileno(fh) )
        else:
            errcode = 0
    if errcode:
        raise RuntimeError( "Child process returned error code", errcode )
def by_line( iterable ):
    """Buffer iterable yielding individual lines"""
    buffer = b""
    for item in iterable:
        if not item:
            yield item 
        else:
            buffer += item 
            if b'\n' not in item:
                # We did something, but we're not ready to yield a real value...
                yield None
            else:
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n',1)
                    yield line 
    if buffer:
        yield buffer 

def string_blocks( content, block_size=4096 ):
    """Yield blocks from content only producing one block at a time"""
    current = 0
    length = len(content)
    if len(content) < block_size:
        # no point copying it...
        yield content 
    else:
        while current < length:
            new = current + block_size
            yield content[current:new]
            current = new
