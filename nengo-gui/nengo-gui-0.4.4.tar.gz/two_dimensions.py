import nengo
import numpy as np

model = nengo.Network(seed=0)
with model:
    a = nengo.Ensemble(n_neurons=400, dimensions=2)
    
    def stim_func(t):
        return np.cos(t), np.sin(t)
    
    stim = nengo.Node(stim_func)
    
    nengo.Connection(stim, a, synapse=None)
    
