#************************
# DeepM6A 
# Fei Tan
# tanfei2007@gmail.com
#************************

#import modules 
import os
import sys
sys.setrecursionlimit(15000)
import numpy as np
import h5py
from sklearn.metrics import roc_auc_score, matthews_corrcoef, precision_recall_fscore_support
from pandas import DataFrame

from keras.preprocessing import sequence
from keras.optimizers import SGD
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution1D, MaxPooling1D, AveragePooling1D
from keras.layers.pooling import AveragePooling1D
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.models import load_model
from keras.layers.advanced_activations import LeakyReLU, PReLU

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class DeepM6A():
    
    def __init__(self, data_dir, epochs=5, tl_model=None):
        self.data_dir = data_dir
        self.epochs = epochs
        self.tl_model = tl_model # transfer learning model
       
    def fit(self, train_name, valid_name):
        #load data
        np.random.seed(1337) # for reproducibility
        trainmat = h5py.File(self.data_dir + '/' + train_name, 'r')
        validmat = h5py.File(self.data_dir + '/' + valid_name, 'r')
        
        X_train = np.transpose(np.array(trainmat['x_train']),axes=(0,2, 1))
        y_train = np.array(trainmat['y_train'])
        X_valid = np.transpose(np.array(validmat['x_train']),axes=(0,2, 1))
        y_valid = np.array(validmat['y_train'])
        
        print(X_train.shape)
        print('train_label: count', np.unique(y_train,  return_counts=True))
        print('valid_label: count', np.unique(y_valid,  return_counts=True))
        
        #build model
        print('building model...............')
        model = Sequential()

        #1st convolutional layer
        NUM_FILTER1 = 80
        model.add(Convolution1D(input_dim=4,
                                input_length=X_train.shape[1],
                                nb_filter=NUM_FILTER1,
                                filter_length=4,
                                border_mode="valid",
                    activation="linear",
                                subsample_length=1,
                    #W_regularizer = l2(0.01),
                    init='he_normal',
                    name = "conv1"))

        model.add(LeakyReLU(alpha=.001))
        model.add(Dropout(0.2))

        #2nd convolutional layer
        model.add(Convolution1D(nb_filter=80,
                                filter_length=2,
                                border_mode="valid",
                    activation="linear",
                                subsample_length=1, init='he_normal',
                    name = "conv2"))

        model.add(LeakyReLU(alpha=.001))
        model.add(Dropout(0.2))

        #3rd convolutional layer
        model.add(Convolution1D(nb_filter=80,
                                filter_length=4,
                                border_mode="valid",
                                activation="linear",
                                subsample_length=1, init='he_normal',
                    name="conv3"))

        model.add(LeakyReLU(alpha=.001))
        model.add(Dropout(0.2))

        #4th convolutional layer
        model.add(Convolution1D(nb_filter=80,
                                filter_length=4,
                                border_mode="valid",
                                activation="linear",
                                subsample_length=1, init='he_normal',
                    name = "conv4"))

        model.add(LeakyReLU(alpha=.001))
        model.add(Dropout(0.2))


        #5th convolutional layer
        model.add(Convolution1D(nb_filter=80,
                                filter_length=4,
                                padding="valid",
                                activation="linear",
                                subsample_length=1, init='he_normal',
                    name = "conv5"))

        model.add(LeakyReLU(alpha=.001))
        model.add(Dropout(0.5))

        model.add(Flatten())

        #FC1
        model.add(Dense(units=100, kernel_initializer='he_normal'))
        model.add(LeakyReLU(alpha=.001))
        model.add(Dropout(0.5))

        model.add(Dense(units=1))
        model.add(Activation('sigmoid'))

        #model training
        model.summary()
        print('compiling and fitting model...........')
        
        
        # use pretrained weights
        if self.tl_model != None:
            model_old = load_model(self.tl_model)
            layer_dict = dict([(layer.name, layer) for layer in model_old.layers])
            for i in layer_dict.keys():
                 try:
                    weight_old = layer_dict[i].get_weights()
                    model.get_layer(i).set_weights(weight_old)
                 except:
                    pass
                 print(i)
            del model_old
        
        bestmodel = self.data_dir + 'DeepM6A.hdf5'

        sgd = SGD(lr=0.01, momentum=0.9, decay=1e-6, nesterov=True)
        checkpointer = ModelCheckpoint(filepath = bestmodel, verbose=1, save_best_only=True)
        earlystopper = EarlyStopping(monitor='val_loss', patience=50, verbose=1)

        model.compile(loss='binary_crossentropy', optimizer=sgd, metrics=['accuracy'])

        Hist = model.fit(X_train, y_train, batch_size=256, epochs=self.epochs, shuffle=True, verbose=2, 
              validation_data=(X_valid, y_valid), callbacks=[checkpointer,earlystopper])
        
        # plot both training and validation loss
        k = 0
        loss = Hist.history['loss']
        val_loss = Hist.history['val_loss']
        epoch = range(1,len(loss)+1)
        plt.plot(epoch[k:], loss[k:])
        plt.plot(epoch[k:], val_loss[k:])
        plt.legend(['train_loss', 'valid_loss'], loc = 'upper right')
        plt.xlabel('epoch')
        plt.ylabel('loss')
        plt.savefig('monitor.png')

        print('training done!')
        
        self.model = model
        

    def predict(self, test_name, rslt_name, bestmodel=None):
        
        # prediction on validation and test data
        if bestmodel != None:
            #f = h5py.File(bestmodel, 'r+')
            #del f['optimizer_weights']
            #f.close()
            model = load_model(bestmodel)
        else:
            model = self.model
            
        model.summary()
        
        testmat = h5py.File(self.data_dir + '/' + test_name, 'r')
        X_test = np.transpose(np.array(testmat['x_train']),axes=(0,2, 1))
        y_test = np.array(testmat['y_train'])
        print('test_label: count', np.unique(y_test,  return_counts=True))
        
        print('**************prediction results on test dataset************')
        keras_eval_test = model.evaluate(X_test, y_test)
        print(keras_eval_test)

        pred_prob_test = model.predict(X_test, verbose=1)
        pred_class_test = model.predict_classes(X_test, verbose=1)


        auc_test = roc_auc_score(y_test, pred_prob_test)
        mcc_test = matthews_corrcoef(y_test, pred_class_test)
        prfs_test = precision_recall_fscore_support(y_test, pred_class_test)

        print('************************')
        print('auc:', auc_test)
        print('mcc:', mcc_test)
        print ('precision:' + str(prfs_test[0][1]), 'recall:' + str(prfs_test[1][1]), 
               'f1score:' + str(prfs_test[2][1]), 'support:' + str(prfs_test[3][1]))
        print('************************')
        
        # save test results
        df = DataFrame({'true':y_test.flatten().tolist(),  'pred' :pred_prob_test.flatten().tolist()}, 
                index = range(len(y_test.flatten().tolist())))
        df.to_csv(self.data_dir + rslt_name, index = False)
