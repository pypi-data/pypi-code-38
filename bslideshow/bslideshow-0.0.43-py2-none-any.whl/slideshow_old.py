#!/usr/bin/env python2.7
#coding:utf-8


import bpy
import os
import math
import random
from PIL import Image
import time

AVOID_OVERLAP = 0.0001

class Slideshow:
  def __init__ (self, name):
    self.name = name
    self.parentObj = None
    self.folder = None
    self.photos = []


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
  

#obj_camera = bpy.context.scene.camera

#tx = 0.0
#ty = 0.0
#tz = 80.0

#rx = 0.0
#ry = 0.0
#rz = 0.0

#fov = 50.0

#pi = 3.14159265

#scene = bpy.data.scenes["Scene"]

# Set render resolution
#scene.render.resolution_x = 480
#scene.render.resolution_y = 359

# Set camera fov in degrees
#scene.camera.data.angle = fov*(pi/180.0)

# Set camera rotation in euler angles
#scene.camera.rotation_mode = 'XYZ'
#scene.camera.rotation_euler[0] = rx*(pi/180.0)
#scene.camera.rotation_euler[1] = ry*(pi/180.0)
#scene.camera.rotation_euler[2] = rz*(pi/180.0)

# Set camera translation
#scene.camera.location.x = tx
#scene.camera.location.y = ty
#scene.camera.location.z = tz




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

def buildScene ():
  #for i in range(1, 10):
  #  add_image("/media/jmramoss/ALMACEN/slideshow/ramsau-3564068_960_720.jpg", i)
  bpy.context.scene.world.light_settings.use_ambient_occlusion = True
  bpy.context.scene.world.light_settings.ao_factor = 1.0

  for i in range(2):
    slideshow = Slideshow('background' + str(i))
    slideshow.selectPhotos("/media/jmramoss/ALMACEN/slideshow/grid_frames/")
    slideshow.shufflePhotos()
    slideshow.draw()
    #slideshow.alignColumn()
    slideshow.alignGrid()
    slideshow.shuffleTranslate()
    slideshow.shuffleRotateZ()
    slideshow.parentObj.location[0] += (random.uniform(-0.3, 0.3) * i)
    slideshow.parentObj.location[1] += (random.uniform(-0.3, 0.3) * i)
    slideshow.parentObj.location[2] += (random.uniform(-0.1, 0.1) * i)

def camLookAt ():
  if(len(bpy.data.cameras) == 1):
    obj = bpy.data.objects['Camera'] # bpy.types.Camera
    obj.location.x = 10.0
    obj.location.y = -5.0
    obj.location.z = 5.0
  pass

def camRotate (rx, ry, rz):
  if(len(bpy.data.cameras) == 1):
    obj = bpy.data.objects['Camera'] # bpy.types.Camera
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler[0] = rx*(math.pi/180.0)
    obj.rotation_euler[1] = ry*(math.pi/180.0)
    obj.rotation_euler[2] = rz*(math.pi/180.0)
  pass

def showPicture (picName):
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

def showSlideshow (numPhotos, maxFrames):
  incFrames = math.ceil(maxFrames / numPhotos)
  for i in range(numPhotos):
    idx = i + 1
    picName = 'pic' + str(idx)
    showPicture(picName)
    frame = i * incFrames
    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    if i == 0:
      cam.keyframe_insert(data_path="location", frame=frame+(2*24))
    else:
      cam.keyframe_insert(data_path="location", frame=frame-(2*24))
    cam.keyframe_insert(data_path="location", frame=frame)



buildScene()

#camLookAt()0
camRotate(0, 0, 0)
#showPicture('pic2')

#showSlideshow()

def renderOneFrame (frameNum):
  scene = bpy.data.scenes["Scene"]
  scene.frame_current=frameNum
  bpy.ops.render.render(write_still=True)


scene = bpy.data.scenes["Scene"]

# Set render resolution
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

fps = 24
numPhotos = 16
pps = 10.0

scene.frame_start = 1
scene.frame_end = numPhotos * pps * fps
scene.frame_step = 1


#renderOneFrame(50)
showSlideshow(numPhotos, scene.frame_end)

#bpy.ops.mesh.primitive_plane_add(location=(0,0,0))
#bpy.context.active_object.name = 'aleluya'
#bpy.context.object.rotation_euler[1] = 1.5708
#bpy.ops.import_image.to_plane(files=[{"name":"cat-3553106_960_720.jpg", "name":"cat-3553106_960_720.jpg"}], directory="/media/jmramoss/ALMACEN/slideshow/", relative=False)
#list(bpy.data.objects)
