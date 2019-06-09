import nengo
import numpy as np

model = nengo.Network()
with model:
    a = nengo.Ensemble(n_neurons=40, dimensions=1)
    
    def stim_function(t):
        return np.sin(t*2*np.pi)
    stim = nengo.Node(stim_function)
    
    nengo.Connection(stim, a, synapse=None)
    
