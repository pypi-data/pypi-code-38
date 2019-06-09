from .imagedatabunch import *

from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import tensorflow.keras.applications as models
from tensorflow.keras import backend as K
import scipy

class Learner:

    def __init__(self, data:ImageDataBunch, model:'model name'=models.resnet50.ResNet50):
        ''' Learner class to create ConvNet models
        convNet(): takes image databunch and model name to create a CNN model
        '''
        
        self.model = model
        self.data = data
        self.train_data = data.train  #train data generator
        self.val_data = data.val      # validation data generator
        self.output_activation = None
        self.input_shape = data.train.image_shape
                
        
    def convNet(self):
        "create a ConvNet model with input and output shape detected from ImageDataBunch provided in argument"

        num_out = self.data.num_classes

        if num_out<2:
            self.output_activation = 'sigmoid'
        else:
            self.output_activation = 'softmax'

        base_model = self.model(weights='imagenet', include_top=False, input_shape=self.input_shape)
        base_model.trainable = False

        self.model = self.createModel(base_model, num_out, self.output_activation)
        
        return self.model

    def createModel(self, base_model, num_out, output_activation='softmax', optimizer='adam'):
        '''
        convNet helper function
        '''
        
        self.model = tf.keras.Sequential([
          base_model,
          tf.keras.layers.GlobalAveragePooling2D(),
          tf.keras.layers.Dense(num_out, activation=output_activation)
        ])

        if num_out<2:
            loss_fn = tf.keras.losses.binary_crossentropy 
        else:
            loss_fn = tf.keras.losses.sparse_categorical_crossentropy

        self.model.compile(optimizer=optimizer, loss = loss_fn, metrics=['accuracy'])
        
        return self.model
    

    def fit(self, lr:float=0.01, epochs:int=50):
        '''fit_generator(generator, steps_per_epoch=None,
        epochs=1, verbose=1, callbacks=None, validation_data=None,
        validation_steps=None, validation_freq=1, class_weight=None,
        max_queue_size=10, workers=1, use_multiprocessing=False,
        shuffle=True, initial_epoch=0)
        '''
        #train_steps_per_epoch = self.data.train_size // self.data.batch_size
        #val_steps_per_epoch = self.data.val_size // self.data.batch_size
        
        if self.data.val_size > 0:
            
            self.model.fit_generator(
                self.data.train,
                steps_per_epoch=None,
                epochs=epochs,
                validation_data=self.val_data,
                validation_steps=None)
            
            
        else:    # to do : in case validation data is not there
            pass
    
    
    
'''    model.fit_generator(datagen.flow(x_train, y_train, batch_size=32),
                    steps_per_epoch=len(x_train) / 32, epochs=epochs)
    
    
'''
def cnn_learner(data:ImageDataBunch, model:'model name'=models.resnet50.ResNet50):
    "Creates a Learner object"
    
    learn = Learner(data, model)
    learn.convNet()
    return learn