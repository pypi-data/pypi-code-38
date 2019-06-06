import numpy as np
from tensorflow.keras.models import Sequential

class REPTILE(object):
    def __init__(self, model, XTrain, YTrain, XTest, YTest, batch_size=3, epochs=100, num_samples=300, num_iterations=10, mini_batch=10):
        
        #model
        self.model = model

        #XTrain
        self.XTrain = XTrain

        #YTrain
        self.YTtrain = YTrain

        #XTest
        self.XTest = XTest

        #YTest
        self.YTest = YTest

        #initialize number of tasks i.e number of tasks we need in each batch of tasks
        self.num_tasks = batch_size

        #number of samples i.e number of shots -number of data points (k) we need to have in each task
        self.num_samples = num_samples

        #number of epochs i.e training iterations
        self.epochs = epochs

        #hyperparameter for the inner loop (inner gradient update)
        self.alpha = 0.0001

        #hyperparameter for the outer loop (outer gradient update) i.e meta optimization
        self.beta = 0.0001

        #number of times we want to perform optimization
        self.num_iterations = num_iterations


        #mini btach size
        self.mini_batch = mini_batch
        
        #train start
        self.train_start = 0

        #test start
        self.test_start = 0
    
    def shuffle_array(self, X, Y):
        indices = np.arange(len(X[0]))
        np.random.shuffle(indices)
        Xout = []
        Yout = []
        for x in X:
            Xout.append(x[indices])
        for y in Y:
            Yout.append(y[indices])
        return Xout, Yout

    def sample_points(self, X, Y, start, num_samples):
        X, Y = self.shuffle_array(X, Y)
        Xout = []
        Yout = []
        for x in X:
            Xout.append(x[start: start+num_samples])
        for y in Y:
            Yout.append(y[start: start+num_samples])
        return Xout, Yout

    def mini_batch_data(self, X, Y, index):
        #sample mini batch of examples 
        X_minibatch = []
        Y_minibatch = []

        for x in X:
            X_minibatch.append(x[index:index+self.mini_batch])
        
        for y in Y:
            Y_minibatch.append(y[index:index+self.mini_batch])
        
        if (len(X_minibatch) == 1):
            X_minibatch = X_minibatch[0]
        
        if (len(Y_minibatch) == 1):
            Y_minibatch = Y_minibatch[0]

        return X_minibatch, Y_minibatch
    
    def test_data_convert (self, X, Y):
        if (len(X) == 1):
            X = X[0]
        if (len(Y) == 1):
            Y = Y[0]
        return X, Y

    #now let's get to the interesting part i.e training 
    def train(self):
        for e in range(self.epochs):
            #for each task in batch of tasks
            for task in range(self.num_tasks):
                
                #get the initial parameters of the model
                old_weights = self.model.get_weights()
                
                #sample x and y
                x_sample, y_sample = self.sample_points(self.XTrain, self.YTtrain, self.train_start, self.num_samples)

                #for some k number of iterations perform optimization on the task
                for k in range(self.num_iterations):

                    #get the minibatch x and y
                    for i in range(0, self.num_samples, self.mini_batch):

                        #sample mini batch of examples 
                        x_minibatch, y_minibatch = self.mini_batch_data(x_sample, y_sample, i)
                        self.model.train_on_batch(x_minibatch, y_minibatch)
                
                #get the updated model parameters after several iterations of optimization
                new_weights = self.model.get_weights()

                #Now we perform meta update

                #i.e theta = theta + epsilon * (theta_star - theta)

                epsilon = 0.01
                
                updated_weights = []
                for i in range(len(old_weights)):
                    updated_weight = old_weights[i] + epsilon * (new_weights[i] - old_weights[i])
                    updated_weights.append(updated_weight)
                
                for i in range(len(updated_weights)):
                    self.model.weights[i] = updated_weight[i]

                self.train_start += 1
                if (self.train_start + self.num_samples > len(self.XTrain)):
                    self.train_start = 0

            loss = self.model.train_on_batch(x_sample, y_sample)
            x_test, y_test = self.test_data_convert(self.XTest, self.YTest)
            score = self.model.evaluate(x_test, y_test, verbose=0)
            print ("Epoch {}: Loss {}\n".format(e,loss))
            print ("Epoch {}: score {}\n".format(e, score))
            print ('Updated Model Parameter Theta\n')
            print ('Sampling Next Batch of Tasks \n')
            print ('---------------------------------\n')
        x_test, y_test = self.test_data_convert(self.XTest, self.YTest)
        return self.model.evaluate(x_test, y_test, verbose=0)