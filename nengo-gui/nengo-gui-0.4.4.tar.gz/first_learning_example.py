import nengo
import numpy as np

model = nengo.Network()
with model:
    a = nengo.Ensemble(n_neurons=100, dimensions=1)
    
    def stim_function(t):
        return np.sin(t*2*np.pi)
    stim = nengo.Node(stim_function)
    
    nengo.Connection(stim, a, synapse=None)
    
    output = nengo.Node(None, size_in=1)
    
    conn = nengo.Connection(a, output, function=lambda x:0,
                     learning_rule_type=nengo.PES(learning_rate=1e-4))

    def error_function(t, x):
        s = stim_function(t)
        diff = x - s
        return diff

    error = nengo.Node(error_function, size_in=1)
    nengo.Connection(output, error, synapse=None)
    nengo.Connection(error, conn.learning_rule, synapse=0)
