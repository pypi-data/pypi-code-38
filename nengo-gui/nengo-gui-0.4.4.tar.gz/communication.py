import nengo
import numpy as np

model = nengo.Network()
with model:
    a = nengo.Ensemble(n_neurons=100, dimensions=1,
                       neuron_type=nengo.LIF(tau_rc=0.02, tau_ref=0.002))
    stim = nengo.Node(0)
    nengo.Connection(stim, a)
    
    output = nengo.Node(None, size_in=1)
    
    def my_function(x):
        if x<0:
            return -1
        else:
            return 1

    nengo.Connection(a, output, synapse=0.005,
                     function=my_function)
    
    
