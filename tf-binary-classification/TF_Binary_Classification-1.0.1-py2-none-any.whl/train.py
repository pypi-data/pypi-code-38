import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
import time
from tensorflow.keras.callbacks import TensorBoard

from tqdm import tqdm
import tensorflow as tf
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
import pickle
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c1", "--cat1", help="catagory1", type=str, default="FALSE", nargs=1)
    parser.add_argument("-c2", "--cat2", help="catagory2", type=str, default="TRUE",nargs=1)
    parser.add_argument("-p", "--path", help="add train dataset folder path: [Train data] / [Folder1],[Folder2]", type=str, nargs=1)
    parser.add_argument("-e", "--epoch", help="number of epoches", type=int, default=3,nargs=1)

    args = parser.parse_args()

    DATADIR1 = args.path
    DATADIR=DATADIR1[0]
    CATEGORIES= []
    x=args.cat1
    CATEGORIES.append(x[0])
    x=args.cat2
    CATEGORIES.append(x[0])
    e=args.epoch
    m=e[0]
    for category in CATEGORIES:  
        path = os.path.join(DATADIR,category)  # create path to human and monkey dir
        for img in os.listdir(path):  # iterate over each image 
            img_array = cv2.imread(os.path.join(path,img) ,cv2.IMREAD_GRAYSCALE)  # convert to array
            break
        break


    IMG_SIZE = 64
    try:
        new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    except Exception as e:
        pass
    try:
        new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    except Exception as e:
        pass

    print("Training the data")
    training_data = []

    def create_training_data():
        for category in CATEGORIES:  

            path = os.path.join(DATADIR,category)  # create path 
            class_num = CATEGORIES.index(category)  # get the classification  (0 or a 1). 1= human

            for img in tqdm(os.listdir(path)):  # iterate over each image 
                try:
                    img_array = cv2.imread(os.path.join(path,img) ,cv2.IMREAD_GRAYSCALE)  # convert to array
                    new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))  # resize to normalize data size
                    training_data.append([new_array, class_num])  # add this to our training_data
                except Exception as e:  # in the interest in keeping the output clean...
                    pass
                #except OSError as e:
                #    print("OSErrroBad img most likely", e, os.path.join(path,img))
                #except Exception as e:
                #    print("general exception", e, os.path.join(path,img))
    create_training_data()


    ############################################


    X = []
    y = []


    for features,label in training_data:
        X.append(features)
        y.append(label)

    #print(X[0].reshape(-1, IMG_SIZE, IMG_SIZE, 1))

    X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, 1)


    pickle_out = open("X.pickle","wb")
    pickle.dump(X, pickle_out)
    pickle_out.close()

    pickle_out = open("y.pickle","wb")
    pickle.dump(y, pickle_out)
    pickle_out.close()

    X = X/255.0
    dense_layers = [0]
    layer_sizes = [64]
    conv_layers = [3]

    for dense_layer in dense_layers:
        for layer_size in layer_sizes:
            for conv_layer in conv_layers:
                NAME = "{}-conv-{}-nodes-{}-dense-{}".format(conv_layer, layer_size, dense_layer, int(time.time()))
                print(NAME)

                model = Sequential()

                model.add(Conv2D(layer_size, (3, 3), input_shape=X.shape[1:]))
                model.add(Activation('relu'))
                model.add(MaxPooling2D(pool_size=(2, 2)))

                for l in range(conv_layer-1):
                    model.add(Conv2D(layer_size, (3, 3)))
                    model.add(Activation('relu'))
                    model.add(MaxPooling2D(pool_size=(2, 2)))

                model.add(Flatten())

                for _ in range(dense_layer):
                    model.add(Dense(layer_size))
                    model.add(Activation('relu'))

                model.add(Dense(1))
                model.add(Activation('sigmoid'))

                tensorboard = TensorBoard(log_dir="logs/{}".format(NAME))

                model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'],)

                model.fit(X, y,batch_size=32,epochs=3,validation_split=0.3,callbacks=[tensorboard])

    model.save('64x3-CNN.model')

if __name__=="__main__":
    main()
