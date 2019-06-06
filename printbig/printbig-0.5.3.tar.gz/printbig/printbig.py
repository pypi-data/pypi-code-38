import numpy as np
import string
import pickle

def load_data():    
    with open("characters", 'rb') as f:
        my_list = pickle.load(f)
    np_data = np.array(my_list)
    w = np_data.reshape(26,6)
    #create a map between the letters and 
    d = dict(zip(list(string.ascii_lowercase),range(0,27)))
    return w,d
def printbig(st):
    w,d = load_data()
    inp=st
    res=""
    for i in range(5):
        for char in list(inp):
            if (char == " "):
                res+= "\t"
            else:
                res += w[d.get(char)][i]
        res+="\n"
    print(res)
    