import os
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import math
import numpy as np 


def get_files(folder_path):
    file_names= os.listdir(folder_path) 
    count= len(file_names)
    file_paths= [os.path.join(folder_path, fname) for fname in file_names]
    print("Total {} image files found".format(count))
    return file_paths, file_names
    # os.path.splitext(file_name)[0]

def get_pure_name(file_names):
    return [os.path.splitext(fname)[0] for fname in file_names]


def resize(file_paths, size=(150,150), silent=False):
    #print("Resizing", end= "")
    out= []
    for path in file_paths:
        if(not silent):
            print(".", end="")
        img= load_img(path, target_size= size)
        out.append(img)
    #print(" DONE")
    return out 

    
def to_numpy(out, silent=False):
    nps= []
    #print("Converting to Numpy arary", end="")
    for outt in out:
        if(not silent):
            print(".", end="")
        nps.append(img_to_array(outt))
    #print(" DONE")
    #return np.array([a for a in nps], dtype= np.int32)
    return np.array([a for a in nps])
        
def load(path, size= None):
    if(size is None):
        img= load_img(path)
    else:
        img= load_img(path, target_size= size)
    return img_to_array(img)
    
def load_dataset(folder_path, y_element= -9999, size= (150,150), count= -1, silent=True):
    file_paths, file_names= get_files(folder_path)
    if(count==-1 or count > len(file_paths)):
        count= len(file_paths)
    print("Processing, Please wait.....", end= "")
    resized= resize(file_paths[:count], size= size, silent= silent)
    X= to_numpy(resized, silent= silent) 
    print("Done")
    if(y_element==-9999):
        return X
    if(y_element==-1):
        y= [int(os.path.splitext(fname)[0]) for fname in file_names]
        y= np.array(y)
        y= y.reshape((len(y), 1))
    else:
        y= np.ones((X.shape[0], 1)) * y_element
    return (X, y)    
        
def concat(data):
    X, y= data[0]
    for i in range(1,len(data)):
        XX, yy= data[i]
        X= np.concatenate([X, XX], axis= 0)
        y= np.concatenate([y, yy], axis= 0)
    p= np.random.permutation(len(y))
    return (X[p],y[p])

def load_all_datasets(folder_paths, y_elements, size= (150,150), silent=False):
    datasets= []
    for folder_path, y_element in zip(folder_paths, y_elements):
        datasets.append(load_dataset(folder_path, y_element, size= size, silent= silent))
    return concat(datasets)



def plot(data, count= 4, rows=4, cols= 4, scale= 1.0):
    if(type(data)== np.ndarray):
        data= data.astype('int32')
        if(data.ndim== 2):
            plt.xticks([])
            plt.yticks([])
            plt.imshow(data, cmap= 'gray')
        if(data.ndim== 3):
            plt.xticks([])
            plt.yticks([])
            plt.imshow(data)
        elif(data.ndim== 4):
            if(count == -1 or count> data.shape[0]):
                count= data.shape[0]
            n= math.ceil(math.sqrt(count))
            fig= plt.figure(figsize= (n*2*scale, n*2*scale))
            for index in range(1, count+1):
                img= data[index-1]
                fig.add_subplot(n, n, index) 
                plt.axis('off')
                plt.imshow(img) 
            plt.show()
    elif(type(data)==str):
        plt.xticks([])
        plt.yticks([])
        img= mpimg.imread(data)
        plt.imshow(img) 
    elif(type(data)==list):
        if(count == -1 or count> len(data)):
            count= len(data)
        if(len(data)< rows*cols):
            pix= data[0:count]
        else:
            pix= data[0:rows*cols]
        fig= plt.figure(figsize= (cols*2*scale, rows*2*scale))


        for index in range(1, count+1):
            if(type(pix[index-1])==np.ndarray):
                img= pix[index-1]
                img= img.astype('int32')
            else:
                img= mpimg.imread(pix[index-1])
            fig.add_subplot(rows, cols, index) 
            plt.axis('off')
            if(img.ndim==2):
                plt.imshow(img, cmap= 'gray')
            else:
                plt.imshow(img) 
        plt.show()


def save(data, file_name):
    return np.save(file_name, data) 

def restore(file_name):
    if('.' not in file_name):
        file_name= file_name+ ".npy"
    return np.load(file_name)



def rgb2gray(img):
    img= img.sum(axis= 2)
    img= img/ 3.0
    return img


def apply_filter(img, filter, step=1, threshold= .7):
    if(img.ndim==3):
        img= rgb2gray(img) 
    x, y= img.shape
    n= filter.shape[0]
    ox= math.floor((x-n-1)/step)
    oy= math.floor((y-n-1)/step)
    out= np.zeros([ox, oy])
    for xx in range(ox):
        for yy in range(oy):
            part= img[xx*step:xx*step+n, yy*step:yy*step+n]
            out[xx][yy]= sum(sum(part*filter))
    out= out> threshold*255.0
    return out  


def apply_filters(img, filters, threshold= .7, step=1):
    if(img.ndim==3):
        img= rgb2gray(img) 
    out= apply_filter(img, filters[0], step=step, threshold= threshold)
    for filter in filters[1:]:
        fimg= apply_filter(img, filter, step=step, threshold= threshold)
        out= np.logical_or(out, fimg)
    return out 


class filter:
    LEFT_EDGE= np.array([
        [1, 0, -1],
        [1, 0, -1],
        [1, 0, -1]
    ])


    RIGHT_EDGE= np.array([
        [-1, 0, 1],
        [-1, 0, 1],
        [-1, 0, 1]
    ])

    TOP_EDGE= np.array([
        [1, 1, 1],
        [0, 0, 0],
        [-1, -1, -1]
    ])

    BOTTOM_EDGE= np.array([
        [-1, -1, -1],
        [0, 0, 0],
        [1, 1, 1]
    ])

    def make(arr):
        out= np.zeros((len(arr), len(arr)))
        out[:,:]= arr
        return out      