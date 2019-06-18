#-*- coding:utf-8 -*-
import os
import sys
from PIL import Image

data = [
    [1242, 2208],
    [2208, 1242],
    [1242,2688],
    [2688, 1242],
    [2048, 2732],
    [2732, 2048],
]

def storeimg():
    dir = sys.argv[1]
    g = os.walk(r"" + dir + "")

    for path, dir_list, file_list in g:
        for file_name in file_list:
            filename = os.path.join(path, file_name)
            if ".png" not in filename:
                continue
            checkImageSize(os.path.join(path, file_name),file_name)

def checkImageSize(path,name):
    # Check image size
    img = Image.open(path)
    if [img.size[0],img.size[1]] not in data :
        print "Wrong size  "+ str(img.size) +"  ====== "+path+ name

    # Check if the image has a alpha area
    for item in img.getdata():
        if len(item) < 4:
            break
        if item[3] == 0:
            print "Image has alpha area ====== "+ name
            break


def main():
    storeimg()
if __name__ == '__main__':
    main()