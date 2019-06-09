import nengo

model = nengo.Network()
with model:
    
    stim_a = nengo.Node(0)
    stim_b = nengo.Node(0)
    
    a = nengo.Ensemble(n_neurons=100, dimensions=1)
    b = nengo.Ensemble(n_neurons=100, dimensions=1)
    
    c = nengo.Ensemble(n_neurons=100, dimensions=1, radius=2)
    
    nengo.Connection(stim_a, a)
    nengo.Connection(stim_b, b)
    
    
    nengo.Connection(a, c)
    nengo.Connection(b, c)