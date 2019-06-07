# coding: UTF-8
"""
Simple load balancing with mpi4py, ported from pypar by Felix Richter <felix.richter2@uni-rostock.de>
June 4, 2019, Steve Spicklemire
"""
import sys
import time

import numpy
from mpi4py import MPI

MPI_WORKTAG = 1
MPI_DIETAG = 2

def mprint(txt):
    """
    Print message txt
    with indentation following the node's rank
    """
    myRank = MPI.COMM_WORLD.Get_rank()
    pre = " " * 8 * myRank
    if type(txt) != type('dummy'):
        txt = txt.__str__()
    pat = "-%d-"
    print (pre + (pat % myRank) + txt)

class MPIWork(object):
    """Abstract base class for ant work to be balanced"""

    def __init__(self):
        pass
    
    def uplink(self, balancer, myid, numprocs, node):
        self.balancer = balancer
        self.mpi_id = myid
        self.mpi_numprocs = numprocs
        self.mpi_node = node
    
    def getNumWorkItems(self):
        pass
    
    def handleWorkResult(self, result, status):
        pass
    
    def calcWorkResult(self, worknum):
        pass
    
    def masterBeforeWork(self):
        """Master node calls this before sending out the work"""
        pass

    def slaveBeforeWork(self):
        """Slave nodes call this before receiving work"""
        pass

    def masterAfterWork(self):
        """Master node calls this after receiving the last work result"""
        pass

    def slaveAfterWork(self):
        """Slave nodes call this after sending the last work result"""
        pass
    
    def msgprint(self, txt):
        pre = " " * 8 * self.mpi_id
        if type(txt) != type('dummy'):
            txt = txt.__str__()
        pat = "-%d-"
        print(pre + (pat % self.mpi_id) + txt)
        

class MPIBalancer(object):
    """The Load Balancer Class
    Initialize it with a MPIWork-derived class instance
    which describes the actual work to do.
    
    debug == True - more status messages
    """
    
    def __init__(self, work, debug = False):
        self.comm = MPI.COMM_WORLD
        self.numprocs = self.comm.Get_size()  # Number of processes as specified by mpirun
        self.myid = self.comm.Get_rank()      # Id of of this process (myid in [0, numproc-1]) 
        self.node = MPI.Get_processor_name()     # Host name on which current process is running
        self.debug= debug
        self.work = work
        self.status = MPI.Status()

        if self.numprocs < 2:
            msg = 'MPIBalancer must run on at least 2 processes'
            msg += ' for the Master Slave paradigm to make sense.'
            raise Exception(msg)

        
        self.work.uplink(self, self.myid, self.numprocs, self.node)
        
        self.numworks = self.work.getNumWorkItems()
        if self.debug:
            print("MPIBalancer initialised on proc %d of %d on node %s" %(self.myid, self.numprocs, self.node))

    def master(self):
        if self.debug: print('[MASTER %d]: I am processor %d of %d on node %s' % (self.myid, self.myid, self.numprocs, self.node))
        if self.debug: print('[MASTER %d]: About to distribute work', min(self.numprocs-1, self.numworks))

        numcompleted = 0
        #--- start slaves distributing the first work slot
        for i in range(0, min(self.numprocs-1, self.numworks)): 
            work = i
            slave= i+1
            self.comm.send(work, dest=slave, tag=MPI_WORKTAG) 
            if self.debug: print('[MASTER ]: sent first work "%s" to node %d' %(work, slave))
    
        if self.debug: print('[MASTER ]: Finished sending work')
        
        # dispatch the remaining work slots on dynamic load-balancing policy
        # the quicker to do the job, the more jobs it takes
        for work in range(self.numprocs-1, self.numworks):
            if self.debug: print('[MASTER ]: check for finished work')
            result = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPI_WORKTAG, status=self.status)
            if self.debug: print('[MASTER ]: received result from node %d' %(self.status.source,))

            numcompleted += 1
            self.comm.send(work, dest=self.status.source, tag=MPI_WORKTAG)
            if self.debug: print('[MASTER ]: sent work "%s" to node %d' %(work, self.status.source))
            
            self.work.handleWorkResult(result, self.status)
        
        # all works have been dispatched out
        if self.debug: print ('[MASTER ]: ToDo : %d' %self.numworks)
        if self.debug: print ('[MASTER ]: Done : %d' %numcompleted)
        
        # I've still to take into the remaining completions   
        while (numcompleted < self.numworks): 
            if self.debug: print ('[MASTER ]: waiting for results')
            result = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPI_WORKTAG, status=self.status) 
            if self.debug: print ('[MASTER ]: received (final) result from node %d' % (self.status.source, ))
            numcompleted += 1
            if self.debug: print ('[MASTER ]: %d completed' % numcompleted)
            
            self.work.handleWorkResult(result, self.status)
            
        if self.debug: print ('[MASTER ]: about to terminate slaves')
    
        # Tell slaves to stop working
        for i in range(1, self.numprocs): 
            self.comm.send('#', dest=i, tag=MPI_DIETAG) 
            if self.debug: print ('[MASTER ]: sent DIETAG to node %d' %(i,))

    def slave(self):
        if self.debug: print('[SLAVE %d]: I am processor %d of %d on node %s' % (self.myid, self.myid, self.numprocs, self.node))
        if self.debug: print('[SLAVE %d]: Entering work loop' % (self.myid,))
        while True:
            result = self.comm.recv(source=0, tag=MPI.ANY_TAG, status=self.status)
            if self.debug: print('[SLAVE %d]: received work'\
                      %(self.myid,))
           
            if (self.status.tag == MPI_DIETAG):
                if self.debug: print('[SLAVE %d]: received termination from node %d' % (self.myid, 0))
                return
            else:
                worknum = result
                if self.debug: print('[SLAVE %d]: work number is %s' % (self.myid, worknum))
                myresult = self.work.calcWorkResult(worknum)
                self.comm.send(myresult, dest=0, tag=MPI_WORKTAG)
                if self.debug: print('[SLAVE %d]: sent result %s to node %d' % (self.myid, str(myresult), 0))

    def run(self, finalRun=True):
        if self.myid == 0:
            self.work.masterBeforeWork()
            self.master()
            self.work.masterAfterWork()
        else:
            self.work.slaveBeforeWork()
            self.slave()
            self.work.slaveAfterWork()

class MPIDemoWork(MPIWork):
    """Example PyparWork implementation"""
    def __init__(self):
        import numpy
        self.worklist = numpy.arange(0.0,20.0)
        self.resultlist = numpy.zeros_like(self.worklist)
        
    def getNumWorkItems(self):
        return len(self.worklist)
    
    def calcWorkResult(self, worknum):
        return [worknum, self.worklist[worknum] + 1]

    def handleWorkResult(self, result, status):
        self.resultlist[result[0]] = result[1]
        
    def masterBeforeWork(self):
        print(self.worklist)

    def slaveBeforeWork(self):
        pass

    def masterAfterWork(self):
        print(self.resultlist)

    def slaveAfterWork(self):
        pass
        
if __name__ == "__main__":
    print("-----------------------")
    print("::: PyParBalancer TEST ")
    print("-----------------------")
    
    # create instance of work class
    mpiwork = MPIDemoWork()

    # create instance of balancer class,
    # initialize with work class
    balancer = MPIBalancer(mpiwork, True)
    
    # run it
    balancer.run()
