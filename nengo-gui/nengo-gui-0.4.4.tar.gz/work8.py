import nengo

model = nengo.Network()
with model:
    
    stim = nengo.Node(0)
    
    a = nengo.Ensemble(n_neurons=100, dimensions=1)
    b = nengo.Ensemble(n_neurons=100, dimensions=1)
    
    nengo.Connection(stim, a)
    
    
    tau = 0.2
    
    #def feedforward(x):
    #    return tau*x
    #nengo.Connection(a, b, function=feedforward, synapse=tau)
    nengo.Connection(a, b, transform=tau, synapse=tau)
    
    #def recurrent(x):
    #    return x
    #nengo.Connection(b, b, function=recurrent, synapse=tau)
    nengo.Connection(a, b, transform=1, synapse=tau)
