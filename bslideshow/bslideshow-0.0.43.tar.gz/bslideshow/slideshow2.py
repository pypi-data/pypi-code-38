#!/usr/bin/env python2.7
#coding:utf-8


import bpy
import os
import math
import random
from PIL import Image
import time

import codecs
import hjson

AVOID_OVERLAP = 0.0001

class Slideshow:
  def __init__ (self, name):
    self.name = name
    self.parentObj = None
    self.folder = None
    self.photos = []

  def getTopLeft (self):
    result = None
    
    f = open("/home/jmramoss/guru99.txt","a+")
    f.write("getTopLeft\n")

    result = [0.0, 0.0, 0.0]

    for photo in self.photos:
      f.write(str(photo.obj.location) +"\n")
      if photo.obj.location[0] < result[0]:
        result[0] = photo.obj.location[0]
      if photo.obj.location[1] > result[1]:
        result[1] = photo.obj.location[1]
      if photo.obj.location[2] > result[2]:
        result[2] = photo.obj.location[2]

    f.close()
    return result

  def getBottomRight (self):
    result = None

    f = open("/home/jmramoss/guru99.txt","a+")
    f.write("getBottomRight\n")
    
    result = [0.0, 0.0, 0.0]

    for photo in self.photos:
      f.write(str(photo.obj.location) +"\n")
      if photo.obj.location[0] > result[0]:
        result[0] = photo.obj.location[0]
      if photo.obj.location[1] < result[1]:
        result[1] = photo.obj.location[1]
      if photo.obj.location[2] < result[2]:
        result[2] = photo.obj.location[2]
    f.close()

    return result

  def getDimensions (self):
    result = None
    topLeft = self.getTopLeft()
    bottomRight = self.getBottomRight()

    f = open("/home/jmramoss/guru99.txt","a+")
#    obj = hjson.OrderedDict()
#    obj['topLeft'] = topLeft
#    obj['bottomRight'] = bottomRight
#    fp = codecs.open("/home/jmramoss/blender.log", mode='w', encoding='utf-8')
#    hjson.dump(obj, fp)
    f.write("topLeft\n")
    f.write(str(topLeft))
    f.write("bottomRight\n")
    f.write(str(bottomRight))
    f.close()

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
    random.shuffle(self.photos)

  def shuffleTranslate (self, maxX = 0.1, maxY = 0.1):
    for photo in self.photos:
      incX = random.uniform(-maxX, maxX)
      incY = random.uniform(-maxY, maxY)
      photo.obj.location[0] += incX
      photo.obj.location[1] += incY

  def shuffleRotateZ (self, maxZ = 0.1):
    for photo in self.photos:
      rotZ = random.uniform(-maxZ, maxZ)
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
  
class Photo:
  def __init__ (self, path):
    self.obj = None
    self.path = os.path.abspath(path)
    self.width = None
    self.height = None
    im = Image.open(self.path)
    self.width, self.height = im.size
    im.close()

  def get_size (self):
    return self.obj.dimensions

  def get_location (self):
    return self.obj.location

  def get_corner (self, top, left):
    result = None
    loc = self.get_location()
    size = self.get_size()
    locY = loc[1] + top*(size[1]/2)
    locX = loc[0] + left*(size[0]/2)
    result = (locX, locY, loc[2])
    return result

  def get_name(self):
    return self.obj.name

  def set_name(self, newValue):
    self.obj.name = newValue

  def get_topleft (self):
    return self.get_corner(1, -1)

  def get_topcenter (self):
    return self.get_corner(1, 0)

  def get_topright (self):
    return self.get_corner(1, 1)

  def get_bottomleft (self):
    return self.get_corner(-1, -1)

  def get_bottomcenter (self):
    return self.get_corner(-1, 0)

  def get_bottomright (self):
    return self.get_corner(-1, 1)

  def get_side (self, left):
    result = None
    loc = self.get_location()
    size = self.get_size()
    locX = loc[0] + left*(size[0]/2)
    result = (locX, loc[1], loc[2])
    return result

  def get_leftcenter (self, left):
    return self.get_side(-1)

  def get_center (self):
    return self.get_location()

  def get_rightcenter (self):
    return self.get_side(1)


  def draw (self):
    ratio = self.width / self.height
    bpy.ops.import_image.to_plane(
      files=[{'name': os.path.basename(self.path)}],
      directory=os.path.dirname(self.path),
      relative=False
    )
    self.obj = bpy.context.active_object
    #self.obj.name = 'aleluya' + str(idx)
    #self.obj.name = 'aleluya'
    #ratio = 1.50470
    self.obj.rotation_euler = (0, 0, 0)
    #Size
    self.obj.dimensions = (ratio, 1, 0)
    #Location
    locY = 0
    #if idx > 1:
    #  prevObj = objects['aleluya' + str(idx - 1)]
    #  locY += prevObj.location[1] + (prevObj.dimensions[1]/2) + (self.obj.dimensions[1]/2)
    #locY = idx * (ratio + 0.1)
    self.obj.location = (1, locY, 1)


class Director:

  def __init__ (self):
    self.slideshow = None
    self.frame = 0.0
    pass

  def buildSlideshow (self, i):
    slideshow = Slideshow('background' + str(i))
    #slideshow.selectPhotos("/media/jmramoss/ALMACEN/slideshow/grid_frames/")
    slideshow.selectPhotos("/media/jmramoss/ALMACEN/unai_colegio_primaria/Tutoria_1A_2017_2018/01_21dic17_bailamos/.bak2")
    slideshow.shufflePhotos()
    slideshow.draw()
    #slideshow.alignColumn()
    slideshow.alignGrid()
    slideshow.shuffleTranslate()
    slideshow.shuffleRotateZ()
    return slideshow

  def buildScene (self):
    #for i in range(1, 10):
    #  add_image("/media/jmramoss/ALMACEN/slideshow/ramsau-3564068_960_720.jpg", i)
    slideshow = self.buildSlideshow(0)
    slideshow.parentObj.location[0] += 0.0
    slideshow.parentObj.location[1] += 0.0
    slideshow.parentObj.location[2] += 0.0
    self.slideshow = slideshow

    slideshow = self.buildSlideshow(1)
    slideshow.parentObj.location[0] += (random.uniform(-0.3, 0.3) * 1)
    slideshow.parentObj.location[1] += (random.uniform(-0.3, 0.3) * 1)
    slideshow.parentObj.location[2] += (-0.1 * 1)

    slideshow = self.buildSlideshow(2)
    slideshow.parentObj.location[0] += -self.slideshow.getDimensions()[0]
    slideshow.parentObj.location[1] += 0
    slideshow.parentObj.location[2] += (-0.1 * 1)

    slideshow = self.buildSlideshow(3)
    slideshow.parentObj.location[0] += self.slideshow.getDimensions()[0]
    slideshow.parentObj.location[1] += 0
    slideshow.parentObj.location[2] += (-0.1 * 1)

    slideshow = self.buildSlideshow(4)
    slideshow.parentObj.location[0] += 0
    slideshow.parentObj.location[1] += self.slideshow.getDimensions()[1]
    slideshow.parentObj.location[2] += (-0.1 * 1)

    slideshow = self.buildSlideshow(5)
    slideshow.parentObj.location[0] += 0
    slideshow.parentObj.location[1] += -self.slideshow.getDimensions()[1]
    slideshow.parentObj.location[2] += (-0.1 * 1)






    slideshow = self.buildSlideshow(6)
    slideshow.parentObj.location[0] += -self.slideshow.getDimensions()[0]
    slideshow.parentObj.location[1] += -self.slideshow.getDimensions()[1]
    slideshow.parentObj.location[2] += (-0.1 * 1)

    slideshow = self.buildSlideshow(7)
    slideshow.parentObj.location[0] += self.slideshow.getDimensions()[0]
    slideshow.parentObj.location[1] += self.slideshow.getDimensions()[1]
    slideshow.parentObj.location[2] += (-0.1 * 1)

    slideshow = self.buildSlideshow(8)
    slideshow.parentObj.location[0] += -self.slideshow.getDimensions()[0]
    slideshow.parentObj.location[1] += self.slideshow.getDimensions()[1]
    slideshow.parentObj.location[2] += (-0.1 * 1)

    slideshow = self.buildSlideshow(9)
    slideshow.parentObj.location[0] += self.slideshow.getDimensions()[0]
    slideshow.parentObj.location[1] += -self.slideshow.getDimensions()[1]
    slideshow.parentObj.location[2] += (-0.1 * 1)



  '''
    for i in range(2):
      slideshow = Slideshow('background' + str(i))
      #slideshow.selectPhotos("/media/jmramoss/ALMACEN/slideshow/grid_frames/")
      slideshow.selectPhotos("/media/jmramoss/ALMACEN/unai_colegio_primaria/Tutoria_1A_2017_2018/01_21dic17_bailamos/.bak2")
      slideshow.shufflePhotos()
      slideshow.draw()
      #slideshow.alignColumn()
      slideshow.alignGrid()
      slideshow.shuffleTranslate()
      slideshow.shuffleRotateZ()
      slideshow.parentObj.location[0] += (random.uniform(-0.3, 0.3) * i)
      slideshow.parentObj.location[1] += (random.uniform(-0.3, 0.3) * i)
      slideshow.parentObj.location[2] += (-0.1 * i)
      if i == 0:
        self.slideshow = slideshow
  '''

  '''
	#obj_camera = bpy.context.scene.camera

	# Set camera translation
	#scene.camera.location.x = 0.0
	#scene.camera.location.y = 0.0
	#scene.camera.location.z = 80.0


	#fov = 50.0
	#pi = 3.14159265
	# Set camera fov in degrees
	#scene.camera.data.angle = fov*(pi/180.0)
  '''
  def camLookAt (self):
    if(len(bpy.data.cameras) == 1):
      obj = bpy.data.objects['Camera'] # bpy.types.Camera
      obj.location.x = 10.0
      obj.location.y = -5.0
      obj.location.z = 5.0
    pass

  '''
	# Set camera rotation in euler angles
        #rx = 0.0
        #ry = 0.0
        #rz = 0.0
	#scene.camera.rotation_mode = 'XYZ'
	#scene.camera.rotation_euler[0] = rx*(pi/180.0)
	#scene.camera.rotation_euler[1] = ry*(pi/180.0)
	#scene.camera.rotation_euler[2] = rz*(pi/180.0)
  '''
  def camRotate (self, rx, ry, rz):
    if(len(bpy.data.cameras) == 1):
      obj = bpy.data.objects['Camera'] # bpy.types.Camera
      obj.rotation_mode = 'XYZ'
      obj.rotation_euler[0] = rx*(math.pi/180.0)
      obj.rotation_euler[1] = ry*(math.pi/180.0)
      obj.rotation_euler[2] = rz*(math.pi/180.0)
    pass

  def showPicture (self, picName):
    pic = bpy.data.objects[picName]
    obj = bpy.data.objects['Camera'] # bpy.types.Camera
    obj.rotation_mode = 'XYZ'
    obj.location.x = pic.location.x
    obj.location.y = pic.location.y
    obj.location.z = pic.location.z + 4.0
    rx = 0
    ry = 0
    rz = 0
    obj.rotation_euler[0] = rx*(math.pi/180.0)
    obj.rotation_euler[1] = ry*(math.pi/180.0)
    obj.rotation_euler[2] = rz*(math.pi/180.0)

  ''' Animation
      #if(len(bpy.data.cameras) == 1):
      #    obj = bpy.data.objects['Camera'] # bpy.types.Camera
      #    obj.location.x = 0.0
      #    obj.location.y = -10.0
      #    obj.location.z = 10.0
      #    obj.keyframe_insert(data_path="location", frame=10.0)
      #    obj.location.x = 10.0
      #    obj.location.y = 0.0
      #    obj.location.z = 5.0
      #    obj.keyframe_insert(data_path="location", frame=20.0)
  '''
  def showSlideshow2 (self, numPhotos, maxFrames):
    incFrames = math.ceil(maxFrames / numPhotos)
    for i in range(numPhotos):
      idx = i + 1
      picName = 'pic' + str(idx)
      self.showPicture(picName)
      frame = i * incFrames
      cam = bpy.data.objects['Camera'] # bpy.types.Camera
      if i == 0:
        cam.keyframe_insert(data_path="location", frame=frame+(2*24))
      else:
        cam.keyframe_insert(data_path="location", frame=frame-(2*24))
      cam.keyframe_insert(data_path="location", frame=frame)

  def showSlideshow3 (self, numPhotos, maxFrames):
    incFrames = math.ceil(maxFrames / numPhotos)

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z
    
    for i in range(numPhotos):
      idx = i + 1
      picName = 'pic' + str(idx)
      self.showPicture(picName)
      frame = i * incFrames

      incZ = random.uniform(-3.0, 3.0)
      cam.location.z = startCamLocationZ + incZ

      rx = 3.0 if i % 2 == 0 else 0.0
      ry = 0.0 if i % 2 == 0 else 6.0
      rz = 0.0 if i % 2 == 0 else 15.0
      cam.rotation_euler[1] = rx*(math.pi/180.0)
      cam.rotation_euler[1] = ry*(math.pi/180.0)
      cam.rotation_euler[2] = rz*(math.pi/180.0)
      
      if i == 0:
        cam.keyframe_insert(data_path="location", frame=frame+(2*24))
        cam.keyframe_insert(data_path="rotation_euler", frame=frame+(2*24))
      else:
        cam.keyframe_insert(data_path="location", frame=frame-(2*24))
        cam.keyframe_insert(data_path="rotation_euler", frame=frame-(2*24))
      cam.keyframe_insert(data_path="location", frame=frame)
      cam.keyframe_insert(data_path="rotation_euler", frame=frame)

  def showSlideshow (self, numPhotos, maxFrames):
    incFrames = math.ceil(maxFrames / numPhotos)

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z
    
    idx = random.randint(1, numPhotos)
    picName = 'pic' + str(idx)
    pic = bpy.data.objects[picName]

    cam.rotation_mode = 'XYZ'
    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + random.uniform(3.5, 5.0)
    cam.rotation_euler[0] = random.uniform(0.0, 6.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 6.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)

    cam.location.x += random.uniform(-0.01, 0.01)
    cam.location.y += random.uniform(-0.01, 0.01)
    cam.location.z -= random.uniform(1.0, 2.5)
    cam.rotation_euler[0] = random.uniform(0.0, 15.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 15.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + incFrames)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + incFrames)

    self.frame = self.frame + incFrames + 12.0


  def showRowColumn (self, numPhotos, maxFrames):
    incFrames = math.ceil(maxFrames / numPhotos)

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z
    
    startIdx = random.randint(1, numPhotos)
    picName = 'pic' + str(startIdx)
    pic = bpy.data.objects[picName]

    cam.rotation_mode = 'XYZ'
    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + random.uniform(3.5, 5.0)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)

    endIdx = random.randint(1, numPhotos)
    picName = 'pic' + str(endIdx)
    pic = bpy.data.objects[picName]

    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + random.uniform(3.5, 5.0)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + incFrames)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + incFrames)

    self.frame = self.frame + incFrames + 12.0



  def showZoomInOut (self, numPhotos, maxFrames):
    incFrames = math.ceil(maxFrames / numPhotos)

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z
    
    startIdx = random.randint(1, numPhotos)
    picName = 'pic' + str(startIdx)
    pic = bpy.data.objects[picName]


    startZ = random.uniform(2.0, 5.0)

    cam.rotation_mode = 'XYZ'
    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + 1.0 + startZ
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)

    endZ = startZ - 3.0 if startZ > 3.0 else startZ + 2.0

    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + 1.0 + endZ
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + incFrames)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + incFrames)

    self.frame = self.frame + incFrames + 12.0


  def showDeleite (self, numPhotos, maxFrames):
    incFrames = math.ceil(maxFrames / numPhotos)
    mitad1Frames = incFrames/2

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z
    
    startIdx = random.randint(1, numPhotos)
    picName = 'pic' + str(startIdx)
    pic = bpy.data.objects[picName]

    initZ = 2.0
    startZ = random.uniform(2.0, 5.0)

    cam.rotation_mode = 'XYZ'
    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + initZ
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)

    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + initZ + 3.0
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + math.ceil(incFrames/2))
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + math.ceil(incFrames/2))

    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + 3.0
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + incFrames)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + incFrames)

    self.frame = self.frame + incFrames + 12.0




  def renderOneFrame (self, frameNum):
    scene = bpy.data.scenes["Scene"]
    scene.frame_current=frameNum
    bpy.ops.render.render(write_still=True)

  def start (self):
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.ao_factor = 1.0

    self.buildScene()
    #camLookAt()0
    self.camRotate(0, 0, 0)
    #showPicture('pic2')

    #showSlideshow()
    # get scene
    scene = bpy.data.scenes["Scene"]

    # Set render resolution
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    fps = 24
    numPhotos = len(self.slideshow.photos)#16
    pps = 10.0

    scene.frame_start = 1
    scene.frame_end = numPhotos * pps * fps
    scene.frame_step = 1


    #renderOneFrame(50)
    self.showDeleite(numPhotos, scene.frame_end)
    self.showDeleite(numPhotos, scene.frame_end)

    self.showZoomInOut(numPhotos, scene.frame_end)
    self.showZoomInOut(numPhotos, scene.frame_end)

    self.showRowColumn(numPhotos, scene.frame_end)
    self.showRowColumn(numPhotos, scene.frame_end)

    self.showSlideshow(numPhotos, scene.frame_end)
    self.showSlideshow(numPhotos, scene.frame_end)

  def addBgSound (self, path, name=None):
    scene = bpy.data.scenes["Scene"]

    if not scene.sequence_editor:
      scene.sequence_editor_create()

    #Sequences.new_sound(name, filepath, channel, frame_start)
    if name is None:
      name = os.path.splitext(path)[0]
    soundstrip = scene.sequence_editor.sequences.new_sound(name, path, 3, 1)

    #scene.sequence_editor.sequences_all[name].animation_offset_start = 1000
    soundstrip.animation_offset_start = 200
    soundstrip.animation_offset_end = 4000

  def saveMovie (self, save=True):
    scene = bpy.data.scenes["Scene"]

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 10#100

    scene.frame_start = 1
    scene.frame_end = 240

    #Type: enum in [‘BMP’, ‘IRIS’, ‘PNG’, ‘JPEG’, ‘JPEG2000’, ‘TARGA’, ‘TARGA_RAW’, ‘CINEON’, ‘DPX’, ‘OPEN_EXR_MULTILAYER’, ‘OPEN_EXR’, ‘HDR’, ‘TIFF’, ‘AVI_JPEG’, ‘AVI_RAW’, ‘FRAMESERVER’, ‘H264’, ‘FFMPEG’, ‘THEORA’, ‘XVID’], default ‘TARGA’
    scene.render.image_settings.file_format = 'FFMPEG'

    #audio_codec #FFmpeg audio codec to use
    #Type:	enum in [‘NONE’, ‘MP2’, ‘MP3’, ‘AC3’, ‘AAC’, ‘VORBIS’, ‘FLAC’, ‘PCM’], default ‘NONE’
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.ffmpeg.audio_codec = 'MP3'
    scene.render.ffmpeg.audio_bitrate = 192

    scene.render.filepath = '/home/jmramoss/movie8.avi'
    if save:
      bpy.ops.render.render(animation=True)




director = Director()
director.start()
director.addBgSound("/media/jmramoss/ALMACEN/mp3/Bruno_Mars_-_24K_Magic_Official_Video[myplaylist-youtubemp3.com].mp3", "metal")
director.saveMovie(True)


#bpy.ops.mesh.primitive_plane_add(location=(0,0,0))
#bpy.context.active_object.name = 'aleluya'
#bpy.context.object.rotation_euler[1] = 1.5708
#bpy.ops.import_image.to_plane(files=[{"name":"cat-3553106_960_720.jpg", "name":"cat-3553106_960_720.jpg"}], directory="/media/jmramoss/ALMACEN/slideshow/", relative=False)
#list(bpy.data.objects)

