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

def plot_raw_imgs(file_paths, rows=4, cols= 4):
    pix= file_paths[0:rows*cols]
    fig= plt.figure(figsize= (cols*2, rows*2))
    for index in range(1, rows*cols +1):
        img= mpimg.imread(pix[index-1])
        fig.add_subplot(rows, cols, index) 
        plt.axis('off')
        plt.imshow(img) 
    plt.show()


def resize(file_paths, size=(150,150), silent=False):
    print("Resizing", end= "")
    out= []
    for path in file_paths:
        if(not silent):
            print(".", end="")
        img= load_img(path, target_size= size)
        out.append(img)
    print(" DONE")
    return out 

    
def to_numpy(out, silent=False):
    nps= []
    print("Converting to Numpy arary", end="")
    for outt in out:
        if(not silent):
            print(".", end="")
        nps.append(img_to_array(outt))
    print(" DONE")
    #return np.array([a for a in nps], dtype= np.int32)
    return np.array([a for a in nps])
        
    
def plot_np_imgs(arr, count= 4):
    arr= arr.astype('int32')
    n= math.ceil(math.sqrt(count))
    fig= plt.figure(figsize= (n*2, n*2))
    for index in range(1, count+1):
        img= arr[index-1]
        fig.add_subplot(n, n, index) 
        plt.axis('off')
        plt.imshow(img) 
    plt.show()

    
def load_dataset(folder_path, y_element, size= (150,150), count= -1, silent=True):
    file_paths, file_names= get_files(folder_path)
    if(count==-1 or count > len(file_paths)):
        count= len(file_paths)
    resized= resize(file_paths[:count], size= size, silent= silent)
    X= to_numpy(resized, silent= silent) 

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
