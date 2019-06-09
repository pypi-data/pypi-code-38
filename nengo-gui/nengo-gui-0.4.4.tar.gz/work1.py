import nengo

model = nengo.Network()
with model:
    a = nengo.Ensemble(n_neurons=100, dimensions=1,
                       neuron_type=nengo.LIF())
                       
                       
    stimulus = nengo.Node(0)
    
    nengo.Connection(stimulus, a)
    
    
