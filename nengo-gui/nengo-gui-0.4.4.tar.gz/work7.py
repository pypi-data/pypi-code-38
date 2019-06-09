import nengo

model = nengo.Network()
with model:
    
    stim_a = nengo.Node(0)
    stim_b = nengo.Node(0)
    
    a = nengo.Ensemble(n_neurons=100, dimensions=1)
    b = nengo.Ensemble(n_neurons=100, dimensions=1)
    
    c = nengo.Ensemble(n_neurons=500, dimensions=2, radius=2)
    
    nengo.Connection(stim_a, a)
    nengo.Connection(stim_b, b)
    
    
    #def func1(a):
    #    return a, 0
    #nengo.Connection(a, c, function=func1)
    #def func2(b):
    #    return 0, b
    #nengo.Connection(b, c, function=func2)
    
    nengo.Connection(a, c[0])
    nengo.Connection(b, c[1])
    
    d = nengo.Ensemble(n_neurons=100, dimensions=1)
    
    def product(x):
        return x[0]*x[1]
    nengo.Connection(c, d, function=product)
    