import nengo

model = nengo.Network()
#model.config[nengo.Connection].synapse=None
with model:
    a = nengo.Ensemble(n_neurons=2000, dimensions=1,
                       neuron_type=nengo.LIF(tau_rc=0.02, tau_ref=0.002),
                       #intercepts=nengo.dists.Uniform(0.5,1.0),
                       max_rates=nengo.dists.Uniform(200,400),
                       radius=1,
                       )
                       
                       
    stimulus = nengo.Node([0])
    
    nengo.Connection(stimulus, a, synapse=0.005)
    
    
    b = nengo.Ensemble(n_neurons=100, dimensions=1)
    
    
    def my_function(x):
        if x < 0:
            return -1
        else:
            return 1

    
    y = nengo.Node(None, size_in=1)
    
    nengo.Connection(a, y, function=my_function, synapse=None)
    nengo.Connection(y, b, synapse=0.1)
    
    
    
    
