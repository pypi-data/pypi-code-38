import nengo

model = nengo.Network()
with model:
    stim_food = nengo.Node([0,0])
    
    food = nengo.Ensemble(n_neurons=200, dimensions=2)
    nengo.Connection(stim_food, food)
    
    
    motor = nengo.Ensemble(n_neurons=200, dimensions=2)
    
    #nengo.Connection(food, motor)
    
    pos = nengo.Ensemble(n_neurons=1000, dimensions=2)
    nengo.Connection(pos, pos, synapse=0.2)
    nengo.Connection(motor, pos, synapse=0.2, transform=0.2)
    
    stim_light = nengo.Node(0)
    
    light = nengo.Ensemble(n_neurons=100, dimensions=1)
    nengo.Connection(stim_light, light)
    
    do_food = nengo.Ensemble(n_neurons=500, dimensions=3)
    nengo.Connection(light, do_food[0])
    #nengo.Connection(food[0], do_food[1])
    #nengo.Connection(food[1], do_food[2])
    nengo.Connection(food, do_food[[1,2]])
    
    def func_food(x):
        light, food_x, food_y = x
        if light < 0:
            return food_x, food_y
        else:
            return 0, 0
    nengo.Connection(do_food, motor, function=func_food)
        
        
    do_home = nengo.Ensemble(n_neurons=500, dimensions=3)
    nengo.Connection(light, do_home[0])
    nengo.Connection(pos, do_home[[1,2]])
        
    def func_home(x):
        light, pos_x, pos_y = x
        if light < 0:
            return 0, 0
        else:
            return -pos_x, -pos_y
    nengo.Connection(do_home, motor, function=func_home)
    
    
    def read_from_sensor(t):
        #grab_data
        x = [0,0,0,0]
        return x
    stim = nengo.Node(read_from_sensor)
    
    
    def save_data(t, x):
        f = open('filename.txt', 'a')
        f.write(str(x))
        f.close()
    output = nengo.Node(save_data, size_in=4)
    nengo.Connection(stim, output)
    
    
    
    
    
    
    
    
    