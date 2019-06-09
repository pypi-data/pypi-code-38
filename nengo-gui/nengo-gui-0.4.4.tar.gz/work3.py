import nengo

model = nengo.Network()
with model:
    a = nengo.Ensemble(n_neurons=200, dimensions=2,
                       neuron_type=nengo.LIF(),
                       #intercepts=nengo.dists.Uniform(0.5,1.0),
                       max_rates=nengo.dists.Uniform(200,400),
                       radius=1,
                       )
                       
                       
    stimulus = nengo.Node([0,0])
    
    nengo.Connection(stimulus, a)
    
    
