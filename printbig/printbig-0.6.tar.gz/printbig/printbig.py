import csv
import os 
def load_data():    
    print(os.getcwd())
    letters = []
    with open('data.csv') as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            letters.append(row)
    d = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25}
    return letters,d
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
    