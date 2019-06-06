import logging
import trraces
import time

l = logging.getLogger("archr.arsenal.symbolic_trrace_index")

from . import Bow
class SymbolicTrraceIndexBow(Bow):
    """
    Figures out which syscall first intrroduces symbolic data, using RR.
    """

    def fire(self, **kwargs): #pylint:disable=arguments-differ
        with RRTracerBow(self.target).fire_context() as flight:
            time.sleep(0.1)
            flight.default_channel.write(b'aRcHr'*0x1000)
            time.sleep(5)
            flight.default_channel.close()
            flight.process.terminate()

        with trraces.trrace.RRTrace(flight.result.trace_dir) as t:
            # skip to the next syscall
            i = 0
            while not t.match_syscall_exit() or t.lookup_syscall_frame_number(t.current_frame) not in {'read', 'recvfrom', 'readv', 'recvmsg'}: #pylint:disable=no-member
                i += 1
                t.pop_frame()

            if any("aRcHr" in w[-1] for w in t.current_frame.writes):
                return i

        return None

from .rr import RRTracerBow
