#!/usr/bin/env python2.7
#coding:utf-8


#import bpy
import os
import math
import random
from PIL import Image
import time

import codecs
import hjson

from bslideshow.photo import Photo

AVOID_OVERLAP = 0.0101

class Slideshow:
  def __init__ (self, name):
    self.name = name
    self.parentObj = None
    self.folder = None
    self.photos = []

  def getTopLeft (self):
    result = None

    #f = open("/home/jmramoss/guru99.txt","a+")
    #f.write("getTopLeft\n")

    result = [0.0, 0.0, 0.0]

    for photo in self.photos:
      #f.write(str(photo.obj.location) +"\n")
      if photo.obj.location[0] < result[0]:
        result[0] = photo.obj.location[0]
      if photo.obj.location[1] > result[1]:
        result[1] = photo.obj.location[1]
      if photo.obj.location[2] > result[2]:
        result[2] = photo.obj.location[2]

    #f.close()
    return result

  def getBottomRight (self):
    result = None

    #f = open("/home/jmramoss/guru99.txt","a+")
    #f.write("getBottomRight\n")

    result = [0.0, 0.0, 0.0]

    for photo in self.photos:
      #f.write(str(photo.obj.location) +"\n")
      if photo.obj.location[0] > result[0]:
        result[0] = photo.obj.location[0]
      if photo.obj.location[1] < result[1]:
        result[1] = photo.obj.location[1]
      if photo.obj.location[2] < result[2]:
        result[2] = photo.obj.location[2]
    #f.close()

    return result

  def getCenterPosition (self):
    result = None
    topLeft = self.getTopLeft()
    bottomRight = self.getBottomRight()

    result = [0, 0, 0]
    result[0] = (bottomRight[0] - topLeft[0])/2.0
    result[1] = (topLeft[1] - bottomRight[1])/2.0
    result[2] = (topLeft[2] - bottomRight[2])/2.0
    return result

  def getDimensions (self):
    result = None
    topLeft = self.getTopLeft()
    bottomRight = self.getBottomRight()

    #f = open("/home/jmramoss/guru99.txt","a+")
#    obj = hjson.OrderedDict()
#    obj['topLeft'] = topLeft
#    obj['bottomRight'] = bottomRight
#    fp = codecs.open("/home/jmramoss/blender.log", mode='w', encoding='utf-8')
#    hjson.dump(obj, fp)
    #f.write("topLeft\n")
    #f.write(str(topLeft))
    #f.write("bottomRight\n")
    #f.write(str(bottomRight))
    #f.close()

    result = [0, 0, 0]
    result[0] = bottomRight[0] - topLeft[0]
    result[1] = topLeft[1] - bottomRight[1]
    result[2] = topLeft[2] - bottomRight[2]
    return result


  def selectPhotos (self, path):
    files = os.listdir(path)
    for file in files:
      if file.lower().endswith('.jpg') or file.lower().endswith('.png'):
        fullpath = os.path.join(path, file)
        photo = Photo(fullpath)
        self.photos.append(photo)

  def shufflePhotos (self):
    #pass
    random.shuffle(self.photos)

  def shuffleTranslate (self, maxX = 0.1, maxY = 0.1):
    for photo in self.photos:
      incX = random.uniform(-maxX, maxX)
      incY = random.uniform(-maxY, maxY)
      photo.obj.location[0] += incX
      photo.obj.location[1] += incY

  def shuffleRotateZ (self, maxZ = 0.1):
    applyZ = min(maxZ, AVOID_OVERLAP/3.0)
    for photo in self.photos:
      rotZ = random.uniform(-applyZ, applyZ)
      photo.obj.rotation_euler[2] += rotZ

  def alignColumn (self, separator = 0.05):
    prev = None
    for photo in self.photos:
      if prev is not None:
        pivot = prev.get_topleft()
        photo.obj.location[0] = pivot[0] + (photo.obj.dimensions[0]/2)
        photo.obj.location[1] = pivot[1] + (photo.obj.dimensions[1]/2) + separator
      prev = photo

  def alignGrid (self, separator = 0.05):
    import bpy
    prev = None
    numPhotos = len(self.photos)
    gridSize = math.ceil(math.sqrt(numPhotos))
    gridPhotos = [None] * gridSize
    for i in range(gridSize):
      gridPhotos[i] = [None] * gridSize
    idx = 0
    for i in range(gridSize):
      for j in range(gridSize):
        toAdd = None
        if (idx < numPhotos):
          toAdd = self.photos[idx]
        else:
          refAdd = self.photos[(idx % numPhotos)]
          toAdd = Photo(refAdd.path)
          toAdd.draw()
          toAdd.set_name('pic' + str(idx + 1))
          toAdd.obj.parent = bpy.data.objects[self.name]
          self.parentObj = toAdd.obj.parent
          self.photos.append(toAdd)
        gridPhotos[i][j] = toAdd
        idx += 1
    for i in range(gridSize):
      for j in range(gridSize):
        photo = gridPhotos[i][j]
        if (not (i == 0 and j == 0)):
          if (j == 0):
            bigWidth = gridPhotos[i-1][0]
            for k in range(1, gridSize):
              itemWidth = gridPhotos[i-1][k]
              if (itemWidth.width > bigWidth.width):
                bigWidth = itemWidth
            pivot = bigWidth.get_rightcenter()
            photo.obj.location[0] = pivot[0] + (photo.obj.dimensions[0]/2) + separator
            photo.obj.location[1] = gridPhotos[i-1][0].get_rightcenter()[1]
          else:
            pivot = gridPhotos[i][j - 1].get_topleft()
            photo.obj.location[0] = pivot[0] + (photo.obj.dimensions[0]/2)
            photo.obj.location[1] = pivot[1] + (photo.obj.dimensions[1]/2) + separator
          photo.obj.location[2] += ((i+j) * AVOID_OVERLAP)

  def draw (self):
    import bpy
    prev = None
    idx = 1

    bpy.ops.object.empty_add(type='CUBE')
    parent = bpy.context.active_object
    parent.name = self.name
    self.parentObj = parent

    for photo in self.photos:
      photo.draw()
      photo.set_name('pic' + str(idx))
      #photo.obj.parent = bpy.data.objects[self.name]
      photo.obj.parent = parent
      idx += 1

if __name__ == '__main__':
  pass

