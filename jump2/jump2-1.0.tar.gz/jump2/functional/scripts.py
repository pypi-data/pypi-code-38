inputf="""\
#!/usr/bin/env python

from jump2.functional import Factory 
from jump2.utils.read import Read
from jump2.pool import Pool
import os 

#functional to prepare the input for calculation % 
def jump_input():
    func = Factory.factory('{0}')
    
    #the basic params you used and tasks you would do%
    func.energy = 1e-5         # the energy thread %
    func.force  = 1e-2         # the force thread if you relax cell %
    func.task   = 'scf' 
    #func.task   = 'cell volume ions scf band optics' 
                               # any tasks you want to do, 
                               # default is 'scf'.
    #func.vdw = 'b86'
    
    #the initial structure you consider % 
    # you can use the for/while loop to do;
    #here is a simple for loop.
    
    # init the pool % 
    pool = Pool()

    pool.functional = func

    for d in os.walk('./test').next()[2]: 
        structure =Read('test/'+d, ftype='vasp').getStructure()
        pool.structure =structure
        job = pool / d
    
    # save data % 
    pool.save()
"""
