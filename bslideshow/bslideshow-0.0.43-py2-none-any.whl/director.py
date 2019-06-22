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

from bslideshow.slideshow import Slideshow
from bslideshow.tools import BlenderTools

ADJUST_Y = -0.1

class Director(BlenderTools):

  def __init__ (self):
    self.slideshow = None
    self.frame = 0.0
    self.sortPhotos = False
    BlenderTools.__init__(self)

  def buildSlideshow (self, i, folderImages):
    #folderImages = "/media/jmramoss/ALMACEN/unai_colegio_primaria/Tutoria_1A_2017_2018/01_21dic17_bailamos/.bak2"
    slideshow = Slideshow('background' + str(i))
    #slideshow.selectPhotos("/media/jmramoss/ALMACEN/slideshow/grid_frames/")
    slideshow.selectPhotos(folderImages)
    print("PRE")
    print(slideshow.photos)
    if False or (i == 0 and self.sortPhotos):
      #sorted(slideshow.photos, key=path)
      slideshow.photos.sort(key=lambda x: x.path)
      print("POST")
      print(slideshow.photos)
      #quit()
    if True and (i != 0 or (i == 0 and not self.sortPhotos)):
      slideshow.shufflePhotos()
    slideshow.draw()
    #slideshow.alignColumn(separator=0.05)
    slideshow.alignGrid(separator=0.2)
    slideshow.shuffleTranslate(maxX = 0.05, maxY = 0.05)
    slideshow.shuffleRotateZ()
    return slideshow

  def buildScene (self, folderImages):
    import bpy
    cam = bpy.data.objects['Camera']
    print(str(type(cam)))
    from pprint import pprint
    pprint(cam)
    print(str(cam.items()))
    cam.data.clip_start = 0.001
    #for i in range(1, 10):
    #  add_image("/media/jmramoss/ALMACEN/slideshow/ramsau-3564068_960_720.jpg", i)
    slideshow = self.buildSlideshow(0, folderImages)
    slideshow.parentObj.location[0] += 0.0
    slideshow.parentObj.location[1] += 0.0
    slideshow.parentObj.location[2] += 0.0
    self.slideshow = slideshow

    posZ = -0.5
    #separator = 1.02
    separator = -1.5
    separator = 1.2
    incZ = -1.1 * 5

    for i in range(0, 0):
      randomX = 0
      randomY = 0

      if False:
        slideshow = self.buildSlideshow(1, folderImages)
        slideshow.parentObj.location[0] += (random.uniform(-0.3, 0.3) * 1)
        slideshow.parentObj.location[1] += (random.uniform(-0.3, 0.3) * 1)
        slideshow.parentObj.location[2] += (2.0 * posZ) + incZ

      incZ -= 0.2

      if i > 0:
        randomX = (random.uniform(-0.3, 0.3) * 1)
        randomY = (random.uniform(-0.3, 0.3) * 1)

      slideshow = self.buildSlideshow(2, folderImages)
      slideshow.parentObj.location[0] += -self.slideshow.getDimensions()[0] - separator + randomX
      slideshow.parentObj.location[1] += 0 + randomY
      slideshow.parentObj.location[2] += incZ
      incZ -= 0.2

      if i > 0:
        randomX = (random.uniform(-0.3, 0.3) * 1)
        randomY = (random.uniform(-0.3, 0.3) * 1)

      slideshow = self.buildSlideshow(3, folderImages)
      slideshow.parentObj.location[0] += self.slideshow.getDimensions()[0] + separator + randomX
      slideshow.parentObj.location[1] += 0 + randomY
      slideshow.parentObj.location[2] += incZ
      incZ -= 0.2

      if i > 0:
        randomX = (random.uniform(-0.3, 0.3) * 1)
        randomY = (random.uniform(-0.3, 0.3) * 1)

      slideshow = self.buildSlideshow(4, folderImages)
      slideshow.parentObj.location[0] += 0 + randomX
      slideshow.parentObj.location[1] += self.slideshow.getDimensions()[1] + separator + randomY
      slideshow.parentObj.location[2] += incZ
      incZ -= 0.2

      if i > 0:
        randomX = (random.uniform(-0.3, 0.3) * 1)
        randomY = (random.uniform(-0.3, 0.3) * 1)

      slideshow = self.buildSlideshow(5, folderImages)
      slideshow.parentObj.location[0] += 0 + randomX
      slideshow.parentObj.location[1] += -self.slideshow.getDimensions()[1] - separator + randomY
      slideshow.parentObj.location[2] += incZ
      incZ -= 0.2

      if i > 0:
        randomX = (random.uniform(-0.3, 0.3) * 1)
        randomY = (random.uniform(-0.3, 0.3) * 1)

      slideshow = self.buildSlideshow(6, folderImages)
      slideshow.parentObj.location[0] += -self.slideshow.getDimensions()[0] - separator + randomX
      slideshow.parentObj.location[1] += -self.slideshow.getDimensions()[1] - separator + randomY
      slideshow.parentObj.location[2] += incZ
      incZ -= 0.2

      if i > 0:
        randomX = (random.uniform(-0.3, 0.3) * 1)
        randomY = (random.uniform(-0.3, 0.3) * 1)

      slideshow = self.buildSlideshow(7, folderImages)
      slideshow.parentObj.location[0] += self.slideshow.getDimensions()[0] + separator + randomX
      slideshow.parentObj.location[1] += self.slideshow.getDimensions()[1] + separator + randomY
      slideshow.parentObj.location[2] += incZ
      incZ -= 0.2

      if i > 0:
        randomX = (random.uniform(-0.3, 0.3) * 1)
        randomY = (random.uniform(-0.3, 0.3) * 1)

      slideshow = self.buildSlideshow(8, folderImages)
      slideshow.parentObj.location[0] += -self.slideshow.getDimensions()[0] - separator + randomX
      slideshow.parentObj.location[1] += self.slideshow.getDimensions()[1] + separator + randomY
      slideshow.parentObj.location[2] += incZ
      incZ -= 0.2

      if i > 0:
        randomX = (random.uniform(-0.3, 0.3) * 1)
        randomY = (random.uniform(-0.3, 0.3) * 1)

      slideshow = self.buildSlideshow(9, folderImages)
      slideshow.parentObj.location[0] += self.slideshow.getDimensions()[0] + separator + randomX
      slideshow.parentObj.location[1] += -self.slideshow.getDimensions()[1] - separator + randomY
      slideshow.parentObj.location[2] += incZ
      incZ -= 0.2


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
    import bpy
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
    import bpy
    if(len(bpy.data.cameras) == 1):
      obj = bpy.data.objects['Camera'] # bpy.types.Camera
      obj.rotation_mode = 'XYZ'
      obj.rotation_euler[0] = rx*(math.pi/180.0)
      obj.rotation_euler[1] = ry*(math.pi/180.0)
      obj.rotation_euler[2] = rz*(math.pi/180.0)
    pass

  def showPicture (self, picName):
    import bpy
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
    import bpy
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
    import bpy
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



  def showSlideshowDuration (self, duration=120):
    import bpy

    numPhotos = len(self.slideshow.photos)#16

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

    cam.keyframe_insert(data_path="location", frame=self.frame + duration)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration)

    self.frame = self.frame + duration + 12.0






  def showSlideshow (self, numPhotos, maxFrames):
    import bpy
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



  def showRowColumnDuration (self, duration=120):
    import bpy

    numPhotos = len(self.slideshow.photos)#16

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

    cam.keyframe_insert(data_path="location", frame=self.frame + duration)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration)

    self.frame = self.frame + duration + 12.0


  def showAllPhotos (self, duration=120, zoom=True, onlyEnd=False):
    import bpy

    numPhotos = len(self.slideshow.photos)#16
    sizeBorder = int(math.sqrt(numPhotos))

    cam = bpy.data.objects['Camera'] # bpy.types.Camera

    zoomMinZ1 = 6.0
    zoomMaxZ1 = 7.0

    zoomMinZ2 = 16.0
    zoomMaxZ2 = 17.0

    if sizeBorder == 6:
      zoomMinZ2 = 16.0
      zoomMaxZ2 = 17.0
    elif sizeBorder == 5:
      #zoomMinZ2 = 14.0
      #zoomMaxZ2 = 15.0
      zoomMinZ2 = 8.0
      zoomMaxZ2 = 9.0

      zoomMinZ1 = 3.0
      zoomMaxZ1 = 4.0
    elif sizeBorder == 4:
      zoomMinZ2 = 12.0
      zoomMaxZ2 = 13.0
    elif sizeBorder == 3:
      zoomMinZ2 = 10.0
      zoomMaxZ2 = 11.0
    elif sizeBorder == 2:
      zoomMinZ2 = 8.0
      zoomMaxZ2 = 9.0


    if zoom:
      zoomMinZStart = zoomMinZ2
      zoomMaxZStart = zoomMaxZ2

      zoomMinZEnd = zoomMinZ1
      zoomMaxZEnd = zoomMaxZ1
    else:
      zoomMinZStart = zoomMinZ1
      zoomMaxZStart = zoomMaxZ1

      zoomMinZEnd = zoomMinZ2
      zoomMaxZEnd = zoomMaxZ2


    centerPosition = self.slideshow.getCenterPosition()

    cam.rotation_mode = 'XYZ'

    cam.scale[0] = 1.0
    cam.scale[1] = 1.0
    cam.scale[2] = 1.0
    cam.keyframe_insert(data_path="scale", frame=self.frame)


    if not onlyEnd:
      cam.location.x = centerPosition[0] + random.uniform(-0.01, 0.01)
      cam.location.y = centerPosition[1] + random.uniform(-0.01, 0.01)
      cam.location.z = centerPosition[2] + random.uniform(zoomMinZStart, zoomMaxZStart)
      cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
      cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
      cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

      cam.keyframe_insert(data_path="location", frame=self.frame)
      cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)

    cam.location.x = centerPosition[0] + random.uniform(-0.01, 0.01)
    cam.location.y = centerPosition[1] + random.uniform(-0.01, 0.01)
    cam.location.z = centerPosition[2] + random.uniform(zoomMinZEnd, zoomMaxZEnd)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12)

    self.frame = self.frame + duration


  def getAllPics (self):
    result = list()
    for p in self.slideshow.photos:
      result.append(p.obj)
    return result




  def showAllPhotosPicZoomIn (self, picName, duration=120):
    import bpy

    pic = bpy.data.objects[picName]

    numPhotos = len(self.slideshow.photos)#16
    sizeBorder = int(math.sqrt(numPhotos))

    cam = bpy.data.objects['Camera'] # bpy.types.Camera

    zoomMinZ1 = 6.0
    zoomMaxZ1 = 7.0

    zoomMinZ2 = 16.0
    zoomMaxZ2 = 17.0

    if sizeBorder == 6:
      zoomMinZ2 = 16.0
      zoomMaxZ2 = 17.0
    elif sizeBorder == 5:
      #zoomMinZ2 = 14.0
      #zoomMaxZ2 = 15.0
      zoomMinZ2 = 8.0
      zoomMaxZ2 = 9.0

      zoomMinZ1 = 3.0
      zoomMaxZ1 = 4.0
    elif sizeBorder == 4:
      zoomMinZ2 = 12.0
      zoomMaxZ2 = 13.0
    elif sizeBorder == 3:
      zoomMinZ2 = 10.0
      zoomMaxZ2 = 11.0
    elif sizeBorder == 2:
      zoomMinZ2 = 8.0
      zoomMaxZ2 = 9.0


    zoomMinZStart = zoomMinZ2
    zoomMaxZStart = zoomMaxZ2

    zoomMinZEnd = zoomMinZ1
    zoomMaxZEnd = zoomMaxZ1


    centerPosition = self.slideshow.getCenterPosition()

    cam.rotation_mode = 'XYZ'

    cam.scale[0] = 1.0
    cam.scale[1] = 1.0
    cam.scale[2] = 1.0
    cam.keyframe_insert(data_path="scale", frame=self.frame)

    allPics = self.getAllPics()

    timeFinalPhoto = int(duration / 4)

    cam.location.x = centerPosition[0] + random.uniform(-0.01, 0.01)
    cam.location.y = centerPosition[1] + random.uniform(-0.01, 0.01)
    cam.location.z = centerPosition[2] + random.uniform(zoomMinZStart, zoomMaxZStart)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    self.showObjects(allPics)
    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)


    cam.location.x = centerPosition[0] + random.uniform(-0.01, 0.01)
    cam.location.y = centerPosition[1] + random.uniform(-0.01, 0.01)
    #cam.location.z = centerPosition[2] + random.uniform(zoomMinZEnd, zoomMaxZEnd)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    self.showObjects([pic])
    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12 - timeFinalPhoto)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12 - timeFinalPhoto)


    cam.location.x += random.uniform(-0.01, 0.01)
    cam.location.y += random.uniform(-0.01, 0.01)
    #cam.location.z = centerPosition[2] + random.uniform(-0.001, 0.001)
    cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12)



    self.frame = self.frame + duration









  def showAllPhotosPicZoomOut (self, picName, duration=120):
    import bpy

    pic = bpy.data.objects[picName]

    numPhotos = len(self.slideshow.photos)#16
    sizeBorder = int(math.sqrt(numPhotos))

    cam = bpy.data.objects['Camera'] # bpy.types.Camera

    zoomMinZ1 = 6.0
    zoomMaxZ1 = 7.0

    zoomMinZ2 = 16.0
    zoomMaxZ2 = 17.0

    if sizeBorder == 6:
      zoomMinZ2 = 16.0
      zoomMaxZ2 = 17.0
    elif sizeBorder == 5:
      #zoomMinZ2 = 14.0
      #zoomMaxZ2 = 15.0
      zoomMinZ2 = 8.0
      zoomMaxZ2 = 9.0

      zoomMinZ1 = 3.0
      zoomMaxZ1 = 4.0
    elif sizeBorder == 4:
      zoomMinZ2 = 12.0
      zoomMaxZ2 = 13.0
    elif sizeBorder == 3:
      zoomMinZ2 = 10.0
      zoomMaxZ2 = 11.0
    elif sizeBorder == 2:
      zoomMinZ2 = 8.0
      zoomMaxZ2 = 9.0


    zoomMinZStart = zoomMinZ1
    zoomMaxZStart = zoomMaxZ1

    zoomMinZEnd = zoomMinZ2
    zoomMaxZEnd = zoomMaxZ2


    centerPosition = self.slideshow.getCenterPosition()

    cam.rotation_mode = 'XYZ'

    cam.scale[0] = 1.0
    cam.scale[1] = 1.0
    cam.scale[2] = 1.0
    cam.keyframe_insert(data_path="scale", frame=self.frame)

    allPics = self.getAllPics()

    timeFinalPhoto = int(duration / 4)

    cam.location.x = centerPosition[0] + random.uniform(-0.01, 0.01)
    cam.location.y = centerPosition[1] + random.uniform(-0.01, 0.01)
    cam.location.z = centerPosition[2] + random.uniform(zoomMinZStart, zoomMaxZStart)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    self.showObjects([pic])
    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)


    cam.location.x = centerPosition[0] + random.uniform(-0.001, 0.001)
    cam.location.y = centerPosition[1] + random.uniform(-0.001, 0.001)
    #cam.location.z = centerPosition[2] + random.uniform(-0.001, 0.001)
    cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    self.showObjects([pic])
    cam.keyframe_insert(data_path="location", frame=self.frame + timeFinalPhoto)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + timeFinalPhoto)


    cam.location.x = centerPosition[0] + random.uniform(-0.01, 0.01)
    cam.location.y = centerPosition[1] + random.uniform(-0.01, 0.01)
    cam.location.z = centerPosition[2] + random.uniform(zoomMinZEnd, zoomMaxZEnd)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    self.showObjects(allPics)
    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12)


    self.frame = self.frame + duration








  def showAllPhotosPic (self, picName, duration=120, zoom=True):
    import bpy

    pic = bpy.data.objects[picName]

    numPhotos = len(self.slideshow.photos)#16
    sizeBorder = int(math.sqrt(numPhotos))

    cam = bpy.data.objects['Camera'] # bpy.types.Camera

    zoomMinZ1 = 6.0
    zoomMaxZ1 = 7.0

    zoomMinZ2 = 16.0
    zoomMaxZ2 = 17.0

    if sizeBorder == 6:
      zoomMinZ2 = 16.0
      zoomMaxZ2 = 17.0
    elif sizeBorder == 5:
      #zoomMinZ2 = 14.0
      #zoomMaxZ2 = 15.0
      zoomMinZ2 = 8.0
      zoomMaxZ2 = 9.0

      zoomMinZ1 = 3.0
      zoomMaxZ1 = 4.0
    elif sizeBorder == 4:
      zoomMinZ2 = 12.0
      zoomMaxZ2 = 13.0
    elif sizeBorder == 3:
      zoomMinZ2 = 10.0
      zoomMaxZ2 = 11.0
    elif sizeBorder == 2:
      zoomMinZ2 = 8.0
      zoomMaxZ2 = 9.0


    if zoom:
      zoomMinZStart = zoomMinZ2
      zoomMaxZStart = zoomMaxZ2

      zoomMinZEnd = zoomMinZ1
      zoomMaxZEnd = zoomMaxZ1
    else:
      zoomMinZStart = zoomMinZ1
      zoomMaxZStart = zoomMaxZ1

      zoomMinZEnd = zoomMinZ2
      zoomMaxZEnd = zoomMaxZ2


    centerPosition = self.slideshow.getCenterPosition()

    cam.rotation_mode = 'XYZ'

    cam.scale[0] = 1.0
    cam.scale[1] = 1.0
    cam.scale[2] = 1.0
    cam.keyframe_insert(data_path="scale", frame=self.frame)

    allPics = self.getAllPics()

    timeFinalPhoto = 24*3

    cam.location.x = centerPosition[0] + random.uniform(-0.01, 0.01)
    cam.location.y = centerPosition[1] + random.uniform(-0.01, 0.01)
    cam.location.z = centerPosition[2] + random.uniform(zoomMinZStart, zoomMaxZStart)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    if zoom:
      self.showObjects(allPics)
    else:
      self.showObjects([pic])

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)

    if not zoom:
      cam.location.x = centerPosition[0] + random.uniform(-0.001, 0.001)
      cam.location.y = centerPosition[1] + random.uniform(-0.001, 0.001)
      cam.location.z = centerPosition[2] + random.uniform(zoomMinZStart, zoomMaxZStart)
      cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
      cam.rotation_euler[1] = random.uniform(0.0, 1.0)*(math.pi/180.0)
      cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
      cam.keyframe_insert(data_path="location", frame=self.frame + timeFinalPhoto)
      cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + timeFinalPhoto)


    cam.location.x = centerPosition[0] + random.uniform(-0.01, 0.01)
    cam.location.y = centerPosition[1] + random.uniform(-0.01, 0.01)
    cam.location.z = centerPosition[2] + random.uniform(zoomMinZEnd, zoomMaxZEnd)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    if zoom:
      self.showObjects([pic])
    else:
      self.showObjects(allPics)

    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12 - timeFinalPhoto)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12 - timeFinalPhoto)

    cam.location.x = centerPosition[0] + random.uniform(-0.001, 0.001)
    cam.location.y = centerPosition[1] + random.uniform(-0.001, 0.001)
    cam.location.z = centerPosition[2] + random.uniform(zoomMinZEnd, zoomMaxZEnd)
    cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12)



    self.frame = self.frame + duration



  def showLinePhotosGroup (self, duration=120, picNameStart=None, picNameEnd=None, zoom=None, groupStart=None, groupEnd=None):
    import bpy

    numPhotos = len(self.slideshow.photos)#16

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z

    picStart = None
    if picNameStart is None:
      startIdx = random.randint(1, numPhotos)
      picName = 'pic' + str(startIdx)
      picStart = bpy.data.objects[picName]
    else:
      picStart = bpy.data.objects[picNameStart]

    zoomMinZ = 3.5
    zoomMaxZ = 5.0
    if zoom == 0:
      zoomMinZ = 1.8
      zoomMaxZ = 2.5
    elif zoom == 1:
      zoomMinZ = 2.5
      zoomMaxZ = 3.5
    elif zoom == 2:
      zoomMinZ = 5.0
      zoomMaxZ = 6.0
    elif zoom == 3:
      zoomMinZ = 7.0
      zoomMaxZ = 8.0

    timeStartEnd = int(duration / 6)

    cam.rotation_mode = 'XYZ'
    cam.location.x = picStart.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = picStart.location.y + random.uniform(-0.01, 0.01) + ADJUST_Y
    cam.location.z = picStart.location.z + random.uniform(zoomMinZ, zoomMaxZ)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.scale[0] = 1.0
    cam.scale[1] = 1.0
    cam.scale[2] = 1.0

    if groupStart is not None and len(groupStart) >  0:
      pics = list()
      for groupName in groupStart:
        picGroup = bpy.data.objects[groupName]
        pics.append(picGroup)
      self.showObjects(pics)

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)
    cam.keyframe_insert(data_path="scale", frame=self.frame)

    cam.location.x += random.uniform(-0.01, 0.01)
    cam.location.y += random.uniform(-0.01, 0.01)
    #cam.location.z = picStart.location.z + random.uniform(zoomMinZ, zoomMaxZ)
    cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.keyframe_insert(data_path="location", frame=self.frame + timeStartEnd)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + timeStartEnd)




    picEnd = None
    if picNameEnd is None:
      endIdx = random.randint(1, numPhotos)
      picName = 'pic' + str(endIdx)
      picEnd = bpy.data.objects[picName]
    else:
      picEnd = bpy.data.objects[picNameEnd]

    cam.location.x = picEnd.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = picEnd.location.y + random.uniform(-0.01, 0.01) + ADJUST_Y
    cam.location.z = picEnd.location.z + random.uniform(zoomMinZ, zoomMaxZ)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    if groupEnd is not None and len(groupEnd) >  0:
      pics = list()
      for groupName in groupEnd:
        picGroup = bpy.data.objects[groupName]
        pics.append(picGroup)
      self.showObjects(pics)


    cam.keyframe_insert(data_path="location", frame=self.frame + duration - timeStartEnd - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - timeStartEnd - 12)





    cam.location.x += random.uniform(-0.01, 0.01)
    cam.location.y += random.uniform(-0.01, 0.01)
    #cam.location.z = picStart.location.z + random.uniform(zoomMinZ, zoomMaxZ)
    cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12)

    self.frame = self.frame + duration






  def showLinePhotos (self, duration=120, picNameStart=None, picNameEnd=None, zoom=None):
    import bpy

    numPhotos = len(self.slideshow.photos)#16

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z

    picStart = None
    if picNameStart is None:
      startIdx = random.randint(1, numPhotos)
      picName = 'pic' + str(startIdx)
      picStart = bpy.data.objects[picName]
    else:
      picStart = bpy.data.objects[picNameStart]

    zoomMinZ = 3.5
    zoomMaxZ = 5.0
    if zoom == 0:
      zoomMinZ = 1.8
      zoomMaxZ = 2.5
    elif zoom == 1:
      zoomMinZ = 2.5
      zoomMaxZ = 3.5
    elif zoom == 2:
      zoomMinZ = 5.0
      zoomMaxZ = 6.0
    elif zoom == 3:
      zoomMinZ = 7.0
      zoomMaxZ = 8.0

    timeStartEnd = int(duration / 8)

    cam.rotation_mode = 'XYZ'
    cam.location.x = picStart.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = picStart.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = picStart.location.z + random.uniform(zoomMinZ, zoomMaxZ)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.scale[0] = 1.0
    cam.scale[1] = 1.0
    cam.scale[2] = 1.0

    self.showObjects([picStart])

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)
    cam.keyframe_insert(data_path="scale", frame=self.frame)


    cam.location.x += random.uniform(-0.01, 0.01)
    cam.location.y += random.uniform(-0.01, 0.01)
    #cam.location.z = picStart.location.z + random.uniform(zoomMinZ, zoomMaxZ)
    cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.keyframe_insert(data_path="location", frame=self.frame + timeStartEnd)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + timeStartEnd)


    picEnd = None
    if picNameEnd is None:
      endIdx = random.randint(1, numPhotos)
      picName = 'pic' + str(endIdx)
      picEnd = bpy.data.objects[picName]
    else:
      picEnd = bpy.data.objects[picNameEnd]

    cam.location.x = picEnd.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = picEnd.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = picEnd.location.z + random.uniform(zoomMinZ, zoomMaxZ)
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    self.showObjects([picEnd])
    cam.keyframe_insert(data_path="location", frame=self.frame + duration - timeStartEnd - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - timeStartEnd - 12)


    cam.location.x += random.uniform(-0.01, 0.01)
    cam.location.y += random.uniform(-0.01, 0.01)
    #cam.location.z = picStart.location.z + random.uniform(zoomMinZ, zoomMaxZ)
    cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[1] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12)






    self.frame = self.frame + duration





  def showRowColumn (self, numPhotos, maxFrames):
    import bpy
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


  def showZoomInOutDuration (self, duration=120):
    import bpy

    numPhotos = len(self.slideshow.photos)#16

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

    cam.keyframe_insert(data_path="location", frame=self.frame + duration)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration)

    self.frame = self.frame + duration + 12.0



  def showZoomInOut (self, numPhotos, maxFrames):
    import bpy
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


  #Se acerca y se aleja de una foto
  def showDeleite (self, numPhotos, maxFrames):
    import bpy
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





  def showDeleiteDuration (self, duration=120, picName=None):
    import bpy

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z

    if picName is None:
      print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> numPHOTOSOSSSSSSSSSSSS = " + str(numPhotos))
      numPhotos = len(self.slideshow.photos)#16
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

    cam.keyframe_insert(data_path="location", frame=self.frame + math.ceil(duration/2))
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + math.ceil(duration/2))

    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + 3.0
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12)

    self.frame = self.frame + duration


  def showObjects (self, selection):
    import bpy
    scene = bpy.context.scene
    for obj in scene.objects:
      obj.select = False
    for obj in selection:
      obj.select = True
    bpy.ops.view3d.camera_to_view_selected()


  '''
  def getDistanceMaxXY (self, pic1, pic2):
    result = None

    result = (maxX, maxY)
    return result
  '''

  '''
  from bpy import context
  # Select objects that will be rendered
  for obj in scene.objects:
    obj.select = False
  for obj in context.visible_objects:
    if not (obj.hide or obj.hide_render):
      obj.select = True
  bpy.ops.view3d.camera_to_view_selected()
  '''

  '''
  camera_fit_coords(scene, coordinates)
Compute the coordinate (and scale for ortho cameras) given object should be to ‘see’ all given coordinates

Parameters:	
scene (Scene) – Scene to get render size information from, if available
coordinates (float array of 1 items in [-inf, inf], (never None)) – Coordinates to fit in
Return (co_return, scale_return):
 	
co_return, The location to aim to be able to see all given points, float array of 3 items in [-inf, inf]

scale_return, The ortho scale to aim to be able to see all given points (if relevant), float in [-inf, inf]
  '''

  #Se acerca y se aleja de una foto
  def showDeleiteTwoPhotos (self, duration=120, picName1=None, picName2=None):
    import bpy

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z

    if picName1 is None:
      numPhotos = len(self.slideshow.photos)
      startIdx = random.randint(1, numPhotos)
      picName1 = 'pic' + str(startIdx)
    pic1 = bpy.data.objects[picName1]

    if picName2 is None:
      numPhotos = len(self.slideshow.photos)
      startIdx = random.randint(1, numPhotos)
      picName2 = 'pic' + str(startIdx)
    pic2 = bpy.data.objects[picName2]

    pos = [0, 0, 0]
    pos[0] = (pic1.location.x + pic2.location.x) / 2.0
    pos[1] = (pic1.location.y + pic2.location.y) / 2.0
    pos[2] = (pic1.location.z + pic2.location.z) / 2.0

    #initZ1 = random.uniform(5.0, 5.5)
    #initZ2 = random.uniform(4.5, 5.0)

    initZ1 = random.uniform(3.01, 3.5)
    initZ2 = random.uniform(2.5, 3.0)


    #factorRandom1 = random.uniform(0.26, 0.31)
    factorRandom1 = random.uniform(0.01, 0.05)
    factorRandom2 = random.uniform(0.01, 0.05)

    cam.rotation_mode = 'XYZ'
    cam.location.x = pos[0] + random.uniform(- factorRandom1, factorRandom1)
    cam.location.y = pos[1] + random.uniform(- factorRandom1, factorRandom1) + ADJUST_Y
    cam.location.z = pos[2] + initZ1
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.scale[0] = 1.0
    cam.scale[1] = 1.0
    cam.scale[2] = 1.0

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)
    cam.keyframe_insert(data_path="scale", frame=self.frame)

    '''
    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + initZ + 3.0
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + math.ceil(duration/2))
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + math.ceil(duration/2))
    '''
    cam.location.x = pos[0] + random.uniform(factorRandom2, factorRandom2)
    cam.location.y = pos[1] + random.uniform(factorRandom2, factorRandom2) + ADJUST_Y
    cam.location.z = pos[2] + initZ2
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    '''
    scene = bpy.context.scene
    c1Pic1 = self.getCorner1(pic1)
    c2Pic1 = self.getCorner2(pic1)
    c3Pic1 = self.getCorner3(pic1)
    c4Pic1 = self.getCorner4(pic1)
    c1Pic2 = self.getCorner1(pic2)
    c2Pic2 = self.getCorner2(pic2)
    c3Pic2 = self.getCorner3(pic2)
    c4Pic2 = self.getCorner4(pic2)
    co_return, scale_return = cam.camera_fit_coords(scene, (c1Pic1[0], c1Pic1[1], c1Pic1[2], c2Pic1[0], c2Pic1[1], c2Pic1[2], c3Pic1[0], c3Pic1[1], c3Pic1[2], c4Pic1[0], c4Pic1[1], c4Pic1[2], c1Pic2[0], c1Pic2[1], c1Pic2[2], c2Pic2[0], c2Pic2[1], c2Pic2[2], c3Pic2[0], c3Pic2[1], c3Pic2[2], c4Pic2[0], c4Pic2[1], c4Pic2[2]))


    cam.location.x = co_return[0]
    cam.location.y = co_return[1]
    #cam.location.z = co_return[2]
    cam.scale[0] = scale_return
    cam.scale[1] = scale_return
    cam.scale[2] = scale_return
    '''

    self.showObjects([pic1, pic2])

    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12)
    #cam.keyframe_insert(data_path="scale", frame=self.frame + duration - 12)

    self.frame = self.frame + duration

  def getCorner1 (self, pic):
    result = None
    result = [0, 0, 0]
    result[0] = pic.location.x - (pic.dimensions[0]/2.0)
    result[1] = pic.location.y + (pic.dimensions[1]/2.0)
    result[2] = pic.location.z
    return result

  def getCorner2 (self, pic):
    result = None
    result = [0, 0, 0]
    result[0] = pic.location.x + (pic.dimensions[0]/2.0)
    result[1] = pic.location.y + (pic.dimensions[1]/2.0)
    result[2] = pic.location.z
    return result

  def getCorner3 (self, pic):
    result = None
    result = [0, 0, 0]
    result[0] = pic.location.x - (pic.dimensions[0]/2.0)
    result[1] = pic.location.y - (pic.dimensions[1]/2.0)
    result[2] = pic.location.z
    return result

  def getCorner4 (self, pic):
    result = None
    result = [0, 0, 0]
    result[0] = pic.location.x + (pic.dimensions[0]/2.0)
    result[1] = pic.location.y - (pic.dimensions[1]/2.0)
    result[2] = pic.location.z
    return result



  #Se acerca y se aleja de una foto
  def showDeleiteOnePhoto (self, duration=120, picName=None):
    import bpy

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z

    if picName is None:
      numPhotos = len(self.slideshow.photos)
      startIdx = random.randint(1, numPhotos)
      picName = 'pic' + str(startIdx)
    pic = bpy.data.objects[picName]

    #initZ1 = random.uniform(2.51, 3.0)
    #initZ2 = random.uniform(2.0, 2.5)
    initZ1 = random.uniform(2.01, 2.5)
    initZ2 = random.uniform(1.8, 2.0)
    #factorRandom1 = random.uniform(0.06, 0.10)
    factorRandom1 = random.uniform(0.01, 0.05)
    factorRandom2 = random.uniform(0.01, 0.05)

    cam.rotation_mode = 'XYZ'
    cam.location.x = pic.location.x + random.uniform(- factorRandom1, factorRandom1)
    cam.location.y = pic.location.y + random.uniform(- factorRandom1, factorRandom1) + ADJUST_Y
    cam.location.z = pic.location.z + initZ1
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.scale[0] = 1.0
    cam.scale[1] = 1.0
    cam.scale[2] = 1.0

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)
    cam.keyframe_insert(data_path="scale", frame=self.frame)

    '''
    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + initZ + 3.0
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + math.ceil(duration/2))
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + math.ceil(duration/2))
    '''
    cam.location.x = pic.location.x + random.uniform(factorRandom2, factorRandom2)
    cam.location.y = pic.location.y + random.uniform(factorRandom2, factorRandom2) + ADJUST_Y
    cam.location.z = pic.location.z + initZ2
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    '''
    scene = bpy.context.scene
    c1Pic1 = self.getCorner1(pic)
    c2Pic1 = self.getCorner2(pic)
    c3Pic1 = self.getCorner3(pic)
    c4Pic1 = self.getCorner4(pic)
    co_return, scale_return = cam.camera_fit_coords(scene, (c1Pic1[0], c1Pic1[1], c1Pic1[2], c2Pic1[0], c2Pic1[1], c2Pic1[2], c3Pic1[0], c3Pic1[1], c3Pic1[2], c4Pic1[0], c4Pic1[1], c4Pic1[2]))

    cam.location.x = co_return[0]
    cam.location.y = co_return[1]
    #cam.location.z = co_return[2]
    cam.scale[0] = scale_return
    cam.scale[1] = scale_return
    cam.scale[2] = scale_return
    '''

    self.showObjects([pic])

    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 12)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 12)
    #cam.keyframe_insert(data_path="scale", frame=self.frame + duration - 12)

    self.frame = self.frame + duration



  #Se acerca y se aleja de una foto
  def showDeleiteOnePhotoProject (self, duration=120):
    import bpy

    numPhotos = len(self.slideshow.photos)

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z

    startIdx = random.randint(1, numPhotos)
    picName = 'pic' + str(startIdx)
    pic = bpy.data.objects[picName]

    initZ1 = random.uniform(1.5, 1.8)
    initZ2 = random.uniform(1.5, 1.8)
    initZ3 = random.uniform(1.5, 1.8)
    factorRandom1 = random.uniform(0.50, 1.00)
    factorRandom2 = random.uniform(0.01, 0.05)

    cam.rotation_mode = 'XYZ'

    cam.location.x = pic.location.x + random.uniform(-0.01 - factorRandom1, 0.01 + factorRandom1)
    cam.location.y = pic.location.y + random.uniform(-0.01 - factorRandom1, 0.01 + factorRandom1)
    cam.location.z = pic.location.z + initZ1
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)
    '''
    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + initZ + 3.0
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + math.ceil(duration/2))
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + math.ceil(duration/2))
    '''
    cam.location.x = pic.location.x + random.uniform(-0.01 - factorRandom2, 0.01 + factorRandom2)
    cam.location.y = pic.location.y + random.uniform(-0.01 - factorRandom2, 0.01 + factorRandom2)
    cam.location.z = pic.location.z + initZ2
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + (duration/2))
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + (duration/2))


    cam.location.x = pic.location.x + random.uniform(-0.01 - factorRandom2, 0.01 + factorRandom2)
    cam.location.y = pic.location.y + random.uniform(-0.01 - factorRandom2, 0.01 + factorRandom2)
    cam.location.z = pic.location.z + initZ3
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + (duration))
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + (duration))


    self.frame = self.frame + duration

  #Se acerca y se aleja de una foto
  def showDeleiteOnePhotoSection (self, duration=120):
    import bpy

    numPhotos = len(self.slideshow.photos)

    cam = bpy.data.objects['Camera'] # bpy.types.Camera
    startCamLocationZ = cam.location.z

    startIdx = random.randint(1, numPhotos)
    picName = 'pic' + str(startIdx)
    pic = bpy.data.objects[picName]

    initZ1 = random.uniform(4.5, 6.0)
    initZ2 = random.uniform(3.0, 4.0)
    factorRandom1 = random.uniform(0.50, 1.00)
    factorRandom2 = random.uniform(0.01, 0.05)

    cam.rotation_mode = 'XYZ'
    cam.location.x = pic.location.x + random.uniform(-0.01 - factorRandom1, 0.01 + factorRandom1)
    cam.location.y = pic.location.y + random.uniform(-0.01 - factorRandom1, 0.01 + factorRandom1)
    cam.location.z = pic.location.z + initZ1
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)
    '''
    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + initZ + 3.0
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + math.ceil(duration/2))
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + math.ceil(duration/2))
    '''
    cam.location.x = pic.location.x + random.uniform(-0.01 - factorRandom2, 0.01 + factorRandom2)
    cam.location.y = pic.location.y + random.uniform(-0.01 - factorRandom2, 0.01 + factorRandom2)
    cam.location.z = pic.location.z + initZ2
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + duration)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration)

    self.frame = self.frame + duration



  def doAnimSlideshow (self, folderImages, time=None, movieOutput=None):
    import bpy
    result = None
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.ao_factor = 1.0

    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

    #filepath  imgBackground
    #bpy.context.scene.node_tree.nodes['imgBackground'].filepath = '/home/jmramoss/Descargas/low-poly-abstract-background/background.jpg'
    bpy.data.images['background'].filepath = '/home/jmramoss/Descargas/low-poly-abstract-background/background2.jpg'

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ folderImages = " + str(folderImages))
    self.buildScene(folderImages)
    #camLookAt()0
    self.camRotate(0, 0, 0)
    #showPicture('pic2')

    numPhotos = len(self.slideshow.photos)
    sizeBorder = int(math.sqrt(numPhotos))


    if time is None:
      if sizeBorder > 4:
        time = int(float(numPhotos) * 2.5)
      else:
        time = numPhotos * 3

    rest = list()
    for i in range(0, numPhotos):
      pic = 'pic' + str((i+1))
      rest.append(pic)

    dataAnim = list()
    #dataAnim.append({'type': 'zoom_in', 'time': 240})
    #dataAnim.append({'type': 'zoom_out', 'time': 120})
    #dataAnim.append({'type': 'corners', 'start': picCorner, 'end': picExtremo, 'time': 360})
    #dataAnim.append({'type': 'line', 'start': picStart, 'end': picExtremo, 'time': 360})
    #dataAnim.append({'type': 'one', 'pic': picOne, 'time': 120})
    #dataAnim.append({'type': 'two', 'pic1': picOne, 'pic2': picTwo, 'time': 120})
    #dataAnim.append({'type': 'two', 'pic1': picOne, 'pic2': picTwo, 'time': 120})
    #dataAnim.append({'type': 'two', 'pic1': picOne, 'pic2': picTwo, 'time': 120})
    #dataAnim.append({'type': 'two', 'pic1': picOne, 'pic2': picTwo, 'time': 120})

    durationZoomIn = 240
    durationZoomOut = 120
    durationCorner = 760
    durationLine = 560
    durationTwoPhotos = 120
    durationOnePhoto = 120

    if sizeBorder == 6:
      durationZoomIn = 240
      durationZoomOut = 120
      durationCorner = 760
      durationLine = 560
    elif sizeBorder == 5:
      durationZoomIn = 192
      durationZoomOut = 96
      durationCorner = 700
      durationLine = 500
    elif sizeBorder == 4:
      durationZoomIn = 144
      durationZoomOut = 72
      durationCorner = 640
      durationLine = 440
    elif sizeBorder == 3:
      durationZoomIn = 72
      durationZoomOut = 48
      durationCorner = 580
      durationLine = 380
    elif sizeBorder == 2:
      durationZoomIn = 72
      durationZoomOut = 48
      durationCorner = 520
      durationLine = 320

    picZoomIn = int(numPhotos / 2)
    picZoomOut = picZoomIn + 1
    if sizeBorder == 6:
      picZoomIn = 15
      picZoomOut = 22
    elif sizeBorder == 5:
      picZoomIn = 12
      picZoomOut = 14
    elif sizeBorder == 4:
      picZoomIn = 6
      picZoomOut = 11
    elif sizeBorder == 3:
      picZoomIn = 4
      picZoomOut = 6
    elif sizeBorder == 3:
      picZoomIn = 1
      picZoomOut = 4


    picZoomInName = 'pic' + str(picZoomIn)
    picZoomOutName = 'pic' + str(picZoomOut)
    if picZoomInName in rest:
      rest.remove(picZoomInName)
    if picZoomOutName in rest:
      rest.remove(picZoomOutName)

    if sizeBorder > 3:
      #corner
      picCorners = self.getCornerPictures()
      picCorner = random.choice(picCorners)
      picExtremo = self.getPicExtremoCorner(picCorner)
      if picCorner in picCorners:
        picCorners.remove(picCorner)
      if picExtremo in picCorners:
        picCorners.remove(picExtremo)
      if picCorner in rest:
        rest.remove(picCorner)
      if picExtremo in rest:
        rest.remove(picExtremo)
      picMiddle = self.getPicMiddle(picCorner, picExtremo)
      for itemMiddle in picMiddle:
        if itemMiddle in rest:
          rest.remove(itemMiddle)
      dataAnim.append({'type': 'corners', 'start': picCorner, 'end': picExtremo, 'time': durationCorner, 'zoom': 1})
      if sizeBorder >= 5:
        vecinosCorner = self.getPicVecinosCorner(picCorner, picExtremo)
        for itemVecino in picMiddle:
          if itemVecino in rest:
            rest.remove(itemVecino)

    #self.showLinePhotos(duration=360, picNameStart=picCorner, picNameEnd=picExtremo, zoom=2)

    if sizeBorder > 3:
      #line
      allBorders = self.getExternPictures()
      picBorders = list()
      for pic in allBorders:
        if pic not in picCorners:
          picBorders.append(pic)
      #picBorders = [x for x in self.getExternPictures() if x not in picCorners]
      picStart = random.choice(picBorders)
      picExtremo = self.getPicExtremo(picStart)
      if picStart in picBorders:
        picBorders.remove(picStart)
      if picExtremo in picBorders:
        picBorders.remove(picExtremo)
      if picStart in rest:
        rest.remove(picStart)
      if picExtremo in rest:
        rest.remove(picExtremo)
      picMiddle = self.getPicMiddle(picStart, picExtremo)
      for itemMiddle in picMiddle:
        if itemMiddle in rest:
          rest.remove(itemMiddle)
      dataAnim.append({'type': 'line', 'start': picStart, 'end': picExtremo, 'time': durationLine, 'zoom': 0})
      #self.showLinePhotos(duration=360, picNameStart=picStart, picNameEnd=picExtremo, zoom=1)


    numPendientes = len(rest)
    numParejas = int((1.0/3.0)*numPendientes)
    numIndividuales = numPendientes - (2*numParejas)


    while numParejas > 0:
      item = random.choice(rest)
      masCercana = self.getPhotoMasCercana(item, rest)
      if item is not None and masCercana is not None:
        if item in rest:
          rest.remove(item)
        if masCercana in rest:
          rest.remove(masCercana)
        dataAnim.append({'type': 'two', 'pic1': item, 'pic2': masCercana, 'time': durationTwoPhotos})
      numParejas -= 1

    numIndividuales += (2*numParejas)
    while numIndividuales > 0:
      item = random.choice(rest)
      if item is not None:
        if item in rest:
          rest.remove(item)
        dataAnim.append({'type': 'one', 'pic': item, 'time': durationOnePhoto})
      numIndividuales -= 1

    #self.showDeleiteOnePhoto(duration=120, picName='pic1')
    #dataAnim.append({'type': 'one', 'pic': 'pic1', 'time': 120})

    #self.showDeleiteTwoPhotos(duration=120, picName1='pic1', picName2='pic2')
    #dataAnim.append({'type': 'two', 'pic1': 'pic1', 'pic2': 'pic12', 'time': 120})

    if time is not None:
      totalTimeFrames = 0
      totalTimeFrames += durationZoomIn
      for itemAnim in dataAnim:
        totalTimeFrames += itemAnim['time']
      totalTimeFrames += durationZoomOut

      maxTimeFrames = time * 24
      if totalTimeFrames != maxTimeFrames:
        porcentaje = float(maxTimeFrames) / float(totalTimeFrames)

        durationZoomIn = int(porcentaje * float(durationZoomIn))
        durationZoomOut = int(porcentaje * float(durationZoomOut))
        for itemAnim in dataAnim:
          itemAnim['time'] = int(porcentaje * float(itemAnim['time']))

    #zoom in
    self.showAllPhotosPicZoomIn(picName=picZoomInName, duration=durationZoomIn)

    while len(dataAnim) > 0:
      itemAnim = random.choice(dataAnim)

      if itemAnim['type'] == 'corners':
        self.showLinePhotosGroup(duration=itemAnim['time'], picNameStart=itemAnim['start'], picNameEnd=itemAnim['end'], zoom=itemAnim['zoom'], groupStart=self.get4PicsCorner(itemAnim['start']), groupEnd=self.get4PicsCorner(itemAnim['end']))
      elif itemAnim['type'] == 'line':
        self.showLinePhotosGroup(duration=itemAnim['time'], picNameStart=itemAnim['start'], picNameEnd=itemAnim['end'], zoom=itemAnim['zoom'], groupStart=None, groupEnd=None)
      elif itemAnim['type'] == 'one':
        self.showDeleiteOnePhoto(duration=itemAnim['time'], picName=itemAnim['pic'])
      elif itemAnim['type'] == 'two':
        self.showDeleiteTwoPhotos(duration=itemAnim['time'], picName1=itemAnim['pic1'], picName2=itemAnim['pic2'])

      if itemAnim in dataAnim:
        dataAnim.remove(itemAnim)

    #zoom out
    self.showAllPhotosPicZoomOut(picName=picZoomOutName, duration=durationZoomOut)



    frameEnd = self.frame
    #frameEnd = 120
    #frameEnd = numPhotos * 120

    result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)
    return result


  def getPhotoMasCercana (self, pivot, listado):
    result = None
    curDistance = 99999999999
    for item in listado:
      if item != pivot:
        distance = self.getPhotoDistance(pivot, item)
        if distance < curDistance:
          result = item
          curDistance = distance

    return result

  def getPhotoDistance (self, item1, item2):
    result = None

    if item1 is not None and item2 is not None:
      import bpy

      pic1 = bpy.data.objects[item1]
      pic2 = bpy.data.objects[item2]

      result = math.sqrt(math.pow((pic1.location.x - pic2.location.x), 2) + math.pow((pic1.location.y - pic2.location.y), 2) + math.pow((pic1.location.z - pic2.location.z), 2))

    return result




  def doAnimSceneDeleiteAllPhotos (self, folderImages, movieOutput=None):
    import bpy
    result = None
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.ao_factor = 1.0

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ folderImages = " + str(folderImages))
    self.buildScene(folderImages)
    #camLookAt()0
    self.camRotate(0, 0, 0)
    #showPicture('pic2')

    numPhotos = len(self.slideshow.photos)

    '''
    for i in range(0, numPhotos):
      #startIdx = random.randint(1, numPhotos)
      startIdx = i + 1
      picName = 'pic' + str(startIdx)
      #self.showDeleiteOnePhoto(duration=120, picName=picName)
      self.showDeleiteDuration(duration=240, picName=picName)
    '''

    '''
    for i in range(0, numPhotos):
      #startIdx = random.randint(1, numPhotos)
      startIdx = i + 1
      picNameStart = 'pic' + str(startIdx)
      for j in range(0, numPhotos):
        endIdx = j + 1
        picNameEnd = 'pic' + str(endIdx)
        if i != j:
          self.showLinePhotos(duration=120, picNameStart=picNameStart, picNameEnd=picNameEnd)
    '''
    '''
    for i in range(0, numPhotos):
      startIdx = i + 1
      picNameStart = 'pic' + str(startIdx)
      for j in range(0, numPhotos):
        endIdx = j + 1
        picNameEnd = 'pic' + str(endIdx)
        if i != j:
          for k in range(0, numPhotos):
            picDistance = 'pic' + str((k+1))
            distance = self.distancePic2Line2Pics(picDistance, picNameStart, picNameEnd)
            print("start = " + picNameStart + " end = " + picNameEnd + " distance " + str(distance) + " to " + picDistance)


    picBorders = self.getExternPictures()
    for pic1 in picBorders:
      for pic2 in picBorders:
        if pic1 != pic2:
          pendiente = self.getPendiente2Pics(pic1, pic2)
          pendiente = pendiente if pendiente is not None else 'None'
          print('pendiente = ' + str(pendiente) + " pics = " +  pic1 + "+" + pic2)

    picBorders = self.getExternPictures()
    print("borders = " + str(picBorders))
    for pic1 in picBorders:
      print("for " + pic1 + " extremo is = " + str(self.getPicExtremo(pic1)))
    #print("for pic2 extremo is = " + str(self.getPicExtremo('pic2')))
    '''

    '''
    picBorders = self.getExternPictures()
    for picBorder1 in picBorders:
      picExtremo = self.getPicExtremo(picBorder1)
      for k in range(0, numPhotos):
        picDistance = 'pic' + str((k+1))
        distance = self.distancePic2Line2Pics(picDistance, picBorder1, picExtremo)
        if distance < 0.5:
          print("start = " + picBorder1 + " end = " + picExtremo + " distance " + str(distance) + " to " + picDistance)
    '''

    rest = list()
    for i in range(0, numPhotos):
      pic = 'pic' + str((i+1))
      rest.append(pic)

    '''
    maxTry3 = 10
    picBorders = self.getExternPictures()
    while len(rest) > 0 and maxTry3 > 0:

      picBorder = None
      picExtremo = None

      maxTry2 = 10
      while maxTry2 > 0:

        picBorder = None
        maxTry = 10
        while maxTry > 0:
          picBorder = random.choice(picBorders)
          if picBorder in rest:
            break
          maxTry -= 1

        if picBorder is not None:
          picExtremo = self.getPicExtremo(picBorder)
          if picExtremo in rest:
            break
        maxTry2 -= 1

      if picBorder is not None and picExtremo is not None:
        picMiddle = self.getPicMiddle(picBorder, picExtremo)
        valid = True if len(picMiddle) <= 0 else False
        for itemMiddle in picMiddle:
          if itemMiddle in rest:
            valid = True
            break

        if valid:
          if picBorder in rest:
            rest.remove(picBorder)
          if picExtremo in rest:
            rest.remove(picExtremo)
          for itemMiddle in picMiddle:
            if itemMiddle in rest:
              rest.remove(itemMiddle)
        else:
          maxTry3 -= 1

          self.showLinePhotos(duration=120, picNameStart=picBorder, picNameEnd=picExtremo)
      else:
        maxTry3 -= 1
    '''

    '''
    maxTry3 = 10
    #picBorders = self.getExternPictures()
    picBorders = self.getCornerPictures()
    while len(rest) > 0 and maxTry3 > 0:
      line = self.selectLinePath(rest, picBorders)
      if line is None:
        maxTry3 -= 1
      else:
        print("rest = " + str(rest))
        print("line = " + str(line))
        self.showLinePhotos(duration=48, picNameStart=line[0], picNameEnd=line[1])
    '''

    '''
    for zoom in range(1, 4):
      picCorners = self.getCornerPictures()

      for i in range(0, 2):
        picCorner = random.choice(picCorners)
        picExtremo = self.getPicExtremoCorner(picCorner)
        picCorners.remove(picCorner)
        picCorners.remove(picExtremo)
        self.showLinePhotos(duration=240, picNameStart=picCorner, picNameEnd=picExtremo, zoom=zoom)
    '''
    self.showAllPhotos(duration=120, zoom=True)
    self.showAllPhotos(duration=120, zoom=False)


    frameEnd = self.frame
    #frameEnd = numPhotos * 120

    result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)
    return result

  def selectLinePath (self, rest, picBorders=None):
    result = None
    maxTry3 = 10
    picBorders = self.getExternPictures() if picBorders is None else picBorders
    #print("strssssss" + str(picBorders))
    while maxTry3 > 0:

      picBorder = None
      picExtremo = None

      maxTry2 = 10
      while maxTry2 > 0:

        picBorder = None
        maxTry = 10
        while maxTry > 0:
          picBorder = random.choice(picBorders)
          if picBorder in rest:
            break
          picBorder = None
          maxTry -= 1

        if picBorder is not None:
          picExtremo = self.getPicExtremo(picBorder)
          if picExtremo in rest and picExtremo in picBorders:
            break
          picExtremo = None
        maxTry2 -= 1

      if picBorder is not None and picExtremo is not None:
        picMiddle = self.getPicMiddle(picBorder, picExtremo)
        valid = True if len(picMiddle) <= 0 else False
        for itemMiddle in picMiddle:
          if itemMiddle in rest:
            valid = True
            break

        if valid:
          if picBorder in rest:
            rest.remove(picBorder)
          if picExtremo in rest:
            rest.remove(picExtremo)
          for itemMiddle in picMiddle:
            if itemMiddle in rest:
              rest.remove(itemMiddle)
          result = (picBorder, picExtremo)
          #self.showLinePhotos(duration=120, picNameStart=picBorder, picNameEnd=picExtremo)
          break
        else:
          maxTry3 -= 1
      else:
        maxTry3 -= 1
    return result

  def getPicMiddle (self, picStart, picEnd):
    result = list()
    numPhotos = len(self.slideshow.photos)
    for k in range(0, numPhotos):
      picDistance = 'pic' + str((k+1))
      if picDistance != picStart and picDistance != picEnd:
        distance = self.distancePic2Line2Pics(picDistance, picStart, picEnd)
        if distance < 0.5:
          #print("start = " + picBorder1 + " end = " + picExtremo + " distance " + str(distance) + " to " + picDistance)
          result.append(picDistance)
    return result


  def getPicVecinosCorner (self, picStart, picEnd):
    result = list()
    numPhotos = len(self.slideshow.photos)
    for k in range(0, numPhotos):
      picDistance = 'pic' + str((k+1))
      if picDistance != picStart and picDistance != picEnd:
        distance = self.distancePic2Line2Pics(picDistance, picStart, picEnd)
        #print("start = " + picStart + " end = " + picEnd + " distance " + str(distance) + " to " + picDistance)
        if distance > 0.5 and distance < 1.0:
          #print("start = " + picBorder1 + " end = " + picExtremo + " distance " + str(distance) + " to " + picDistance)
          result.append(picDistance)
    return result


  def get4PicsCorner(self, picName):
    result = list()
    result.append(picName)
    numPhotos = len(self.slideshow.photos)
    for k in range(0, numPhotos):
      picDistance = 'pic' + str((k+1))
      if picDistance != picName:
        distance = self.distance2Pics(picDistance, picName)
        print("picDistance = " + picDistance + " distance " + str(distance) + " to " + picName)
        if distance < 1.65:
          #print("start = " + picBorder1 + " end = " + picExtremo + " distance " + str(distance) + " to " + picDistance)
          result.append(picDistance)
    #print(str(result))
    #quit()
    return result




  def getPicExtremo (self, picName):
    result = None
    if picName is not None:
      picIdx = int(picName[3:]) - 1

      numPhotos = len(self.slideshow.photos)
      sizeBorder = int(math.sqrt(numPhotos))

      idxCorner1 = 0
      idxCorner2 = (sizeBorder - 1)
      idxCorner3 = (numPhotos - 1)
      idxCorner4 = (numPhotos - sizeBorder)

      div = int(picIdx / sizeBorder)
      div1 = int((picIdx + 1) / sizeBorder)
      mod = int(picIdx % sizeBorder)
      mod1 = int((picIdx + 1) % sizeBorder)

      corner = True if (picIdx == idxCorner1 or picIdx == idxCorner2 or picIdx == idxCorner3 or picIdx == idxCorner4) else False
      vertical = True if div == 0 or div == (sizeBorder - 1) else False
      horizontal = True if mod == 0 or mod1 == 0 else False

      '''
      print("picIdx = " + str(picIdx))
      print("numPhotos = " + str(numPhotos))
      print("sizeBorder = " + str(sizeBorder))
      print("corner = " + str(corner))
      print("vertical = " + str(vertical))
      print("horizontal = " + str(horizontal))
      print("div = " + str(picIdx / sizeBorder))
      print("mod = " + str(picIdx % sizeBorder))
      '''

      resultIdx = None
      if corner:
        listCorners = [idxCorner1, idxCorner2, idxCorner3, idxCorner4]
        listCorners.remove(picIdx)
        resultIdx = random.choice(listCorners)
      elif vertical:
        resultIdx = picIdx + (numPhotos - sizeBorder) if picIdx < sizeBorder else picIdx - (numPhotos - sizeBorder)
      elif horizontal:
        resultIdx = picIdx + (sizeBorder - 1) if mod == 0 else picIdx - (sizeBorder - 1)

      if resultIdx is not None:
        result = 'pic' + str((resultIdx + 1))
    return result

  def getPicExtremoCorner (self, picName):
    result = None
    if picName is not None:
      picIdx = int(picName[3:]) - 1

      numPhotos = len(self.slideshow.photos)
      sizeBorder = int(math.sqrt(numPhotos))

      idxCorner1 = 0
      idxCorner2 = (sizeBorder - 1)
      idxCorner3 = (numPhotos - 1)
      idxCorner4 = (numPhotos - sizeBorder)

      valid = False
      valid = valid or (picIdx == idxCorner1)
      valid = valid or (picIdx == idxCorner2)
      valid = valid or (picIdx == idxCorner3)
      valid = valid or (picIdx == idxCorner4)

      if valid:
        resultIdx = None
        resultIdx = idxCorner1 if picIdx == idxCorner3 else resultIdx
        resultIdx = idxCorner3 if picIdx == idxCorner1 else resultIdx
        resultIdx = idxCorner2 if picIdx == idxCorner4 else resultIdx
        resultIdx = idxCorner4 if picIdx == idxCorner2 else resultIdx
        if resultIdx is not None:
          result = 'pic' + str((resultIdx + 1))

    return result



  def getPendiente2Pics (self, picName1, picName2):
    result = None
    if picName1 is not None and picName2 is not None:
      import bpy
      pic1 = bpy.data.objects[picName1]
      pic2 = bpy.data.objects[picName2]

      try:
        result = (pic2.location.y - pic1.location.y) / (pic2.location.x - pic1.location.x)
      except:
        pass

    return result

  def distancePic2Line2Pics (self, picName, picNameStart, picNameEnd):
    result = None
    if picName is not None and picNameStart is not None and picNameEnd is not None:
      import bpy
      pic = bpy.data.objects[picName]
      picStart = bpy.data.objects[picNameStart]
      picEnd = bpy.data.objects[picNameEnd]

      point = (pic.location.x, pic.location.y)
      linePoint1 = (picStart.location.x, picStart.location.y)
      linePoint2 = (picEnd.location.x, picEnd.location.y)
      result = self.distancePoint2Line2P(point, linePoint1, linePoint2)
    return result

  def distance2Pics (self, picName1, picName2):
    result = None
    if picName1 is not None and picName2 is not None:
      import bpy
      pic1 = bpy.data.objects[picName1]
      pic2 = bpy.data.objects[picName2]

      result = math.sqrt(math.pow((pic2.location.x - pic1.location.x), 2) + math.pow((pic2.location.y - pic1.location.y), 2))
    return result



  def distancePoint2Line2P (self, point, linePoint1, linePoint2):
    result = None
    if point is not None and linePoint1 is not None and linePoint2 is not None:
      #recta y = mx + b
      mPendiente = (linePoint2[1] - linePoint1[1]) / (linePoint2[0] - linePoint1[0])
      b = linePoint1[1] - (mPendiente * linePoint1[0])
      distance = (math.fabs((mPendiente*point[0]) - point[1] + b)) / (math.sqrt(math.pow(mPendiente, 2) + 1))
      result = distance
    return result

  def getCornerPictures (self):
    result = None

    numPhotos = len(self.slideshow.photos)
    sizeBorder = int(math.sqrt(numPhotos))

    picCorner1 = 'pic1'
    picCorner2 = 'pic' + str(sizeBorder)
    picCorner3 = 'pic' + str(numPhotos)
    picCorner4 = 'pic' + str(numPhotos - sizeBorder + 1)

    result = [picCorner1, picCorner2, picCorner3, picCorner4]

    return result



  def getExternPictures (self):
    result = None

    numPhotos = len(self.slideshow.photos)
    print("numPhotos = " + str(numPhotos))

    sizeBorder = int(math.sqrt(numPhotos))
    print("sizeBorder = " + str(sizeBorder))

    result = list()

    for i in range(0, numPhotos):
      col = int(i / sizeBorder)
      print("col = " + str(col))

      valid = False
      if col == 0:
        valid = True
      elif col == (sizeBorder - 1):
        valid = True
      elif (i % sizeBorder) == 0 or ((i + 1) % sizeBorder) == 0:
        valid = True
      if valid:
        picName = 'pic' + str((i + 1))
        result.append(picName)

    return result



  def doAnimSceneSequential (self, folderImages, movieOutput=None):
    import bpy
    result = None
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.ao_factor = 1.0

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ folderImages = " + str(folderImages))
    self.buildScene(folderImages)
    #camLookAt()0
    self.camRotate(0, 0, 0)
    #showPicture('pic2')

    numPhotos = len(self.slideshow.photos)
    #print("NUM PHOTOS = " + str(numPhotos))
    for i in range(0, numPhotos):
      #startIdx = random.randint(1, numPhotos)
      startIdx = i + 1
      picName = 'pic' + str(startIdx)
      self.showSequentialPhoto(picName, duration=120)

    #print("EXTERN PICTURES = " + str(self.getExternPictures()))

    frameEnd = self.frame
    #frameEnd = numPhotos * 120

    result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)
    return result


  def showSequentialPhoto (self, picName, duration=120):
    import bpy

    cam = bpy.data.objects['Camera'] # bpy.types.Camera

    pic = bpy.data.objects[picName]

    initZ = 2.5

    cam.rotation_mode = 'XYZ'
    cam.location.x = pic.location.x + random.uniform(-0.01, 0.01)
    cam.location.y = pic.location.y + random.uniform(-0.01, 0.01)
    cam.location.z = pic.location.z + initZ
    cam.rotation_euler[0] = random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 3.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame)

    cam.location.x = pic.location.x + random.uniform(-0.001, 0.001)
    cam.location.y = pic.location.y + random.uniform(-0.001, 0.001)
    cam.location.z = pic.location.z + initZ + 0.01
    cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + math.ceil(duration/2) - 6)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + math.ceil(duration/2) - 6)

    cam.location.x = pic.location.x + random.uniform(-0.001, 0.001)
    cam.location.y = pic.location.y + random.uniform(-0.001, 0.001)
    cam.location.z = pic.location.z + initZ - 0.01
    cam.rotation_euler[0] = random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[1] = 0.0*random.uniform(0.0, 1.0)*(math.pi/180.0)
    cam.rotation_euler[2] = random.uniform(0.0, 1.0)*(math.pi/180.0)

    cam.keyframe_insert(data_path="location", frame=self.frame + duration - 6)
    cam.keyframe_insert(data_path="rotation_euler", frame=self.frame + duration - 6)

    self.frame = self.frame + duration


  def doAnimSceneDuration (self, folderImages, movieOutput=None):
    import bpy
    result = None
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.ao_factor = 1.0

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ folderImages = " + str(folderImages))
    self.buildScene(folderImages)
    #camLookAt()0
    self.camRotate(0, 0, 0)
    #showPicture('pic2')

    numPhotos = len(self.slideshow.photos)#16
    frameEnd = 8 * 120

    #renderOneFrame(50)
    self.showDeleiteDuration(duration=120)
    self.showDeleiteDuration(duration=120)

    self.showZoomInOutDuration(duration=120)
    self.showZoomInOutDuration(duration=120)

    self.showRowColumnDuration(duration=120)
    self.showRowColumnDuration(duration=120)

    self.showSlideshowDuration(duration=120)
    self.showSlideshowDuration(duration=120)

    result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)
    return result





  def doAnimScene (self, folderImages, movieOutput=None):
    import bpy
    result = None
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.ao_factor = 1.0

    self.buildScene(folderImages)
    #camLookAt()0
    self.camRotate(0, 0, 0)
    #showPicture('pic2')

    numPhotos = len(self.slideshow.photos)#16
    pps = 1.0
    fps = self.fps
    frameEnd = numPhotos * pps * fps


    #renderOneFrame(50)
    self.showDeleite(numPhotos, frameEnd)
    self.showDeleite(numPhotos, frameEnd)

    self.showZoomInOut(numPhotos, frameEnd)
    self.showZoomInOut(numPhotos, frameEnd)

    self.showRowColumn(numPhotos, frameEnd)
    self.showRowColumn(numPhotos, frameEnd)

    self.showSlideshow(numPhotos, frameEnd)
    self.showSlideshow(numPhotos, frameEnd)

    result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)
    return result


  def doAnimSceneTitle (self, folderImages, movieOutput=None):
    import bpy
    result = None
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.ao_factor = 1.0

    self.buildScene(folderImages)
    #camLookAt()0
    self.camRotate(0, 0, 0)
    #showPicture('pic2')

    numPhotos = len(self.slideshow.photos)#16
    pps = 1.0
    fps = self.fps
    frameEnd = numPhotos * pps * fps


    #renderOneFrame(50)
    self.showDeleite(numPhotos, frameEnd)

    self.showZoomInOut(numPhotos, frameEnd)

    self.showDeleite(numPhotos, frameEnd)

    result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)
    return result


  def animSceneDuration (self, folderImages, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "animSceneDuration", [folderImages], movieOutput=movieOutput)
    else:
      result = self.doAnimSceneDuration(folderImages, movieOutput)

    return result


  def animSceneSequential (self, folderImages, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "animSceneSequential", [folderImages], movieOutput=movieOutput)
    else:
      result = self.doAnimSceneSequential(folderImages, movieOutput)

    return result

  def animSceneDeleiteAllPhotos (self, folderImages, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "animSceneDeleiteAllPhotos", [folderImages], movieOutput=movieOutput)
    else:
      result = self.doAnimSceneDeleiteAllPhotos(folderImages, movieOutput)

    return result




  def animSlideshow (self, folderImages, time=None, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty_background.blend', 'templates')
      result = self.runMethodBlender(templatePath, "animSlideshow", [folderImages, time], movieOutput=movieOutput)
    else:
      result = self.doAnimSlideshow(folderImages, time, movieOutput)

    return result


  def animScene (self, folderImages, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "animScene", [folderImages], movieOutput=movieOutput)
    else:
      result = self.doAnimScene(folderImages, movieOutput)

    return result

  def animSceneTitle (self, folderImages, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "doAnimSceneTitle", [folderImages], movieOutput=movieOutput)
    else:
      result = self.doAnimSceneTitle(folderImages, movieOutput)

    return result

  def animSceneTitleItem (self, folderImages, durationFrames=120, mode='project', movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty_background.blend', 'templates')
      result = self.runMethodBlender(templatePath, "doAnimSceneTitleItem", [folderImages, durationFrames, mode], movieOutput=movieOutput)
    else:
      result = self.doAnimSceneTitleItem(folderImages=folderImages, durationFrames=durationFrames, mode=mode, movieOutput=movieOutput)

    return result

  def doAnimSceneTitleItem (self, folderImages, durationFrames=120, mode='project', movieOutput=None):
    import bpy
    result = None
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.ao_factor = 1.0

    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

    #filepath  imgBackground
    #bpy.context.scene.node_tree.nodes['imgBackground'].filepath = '/home/jmramoss/Descargas/low-poly-abstract-background/background.jpg'
    bpy.data.images['background'].filepath = '/home/jmramoss/Descargas/low-poly-abstract-background/background2.jpg'

    self.buildScene(folderImages)
    #camLookAt()0
    self.camRotate(0, 0, 0)
    #showPicture('pic2')

    #renderOneFrame(50)
    if mode == 'project':
      self.showDeleiteOnePhotoProject(durationFrames)
    elif mode == 'section':
      self.showDeleiteOnePhotoSection(durationFrames)
    else:
      self.showDeleiteOnePhoto(durationFrames)

    result = self.saveMovie(frameStart=1, frameEnd=durationFrames, movieOutput=movieOutput)
    return result




if __name__ == '__main__':
  director = Director()
  director.runMode = 'LOW'
  director.verbose = True
  director.forceFullRender = True
  director.sortPhotos = True
  #director.forceFrameEnd = 6
  #out = director.animScene("/media/jmramoss/ALMACEN/unai_colegio_primaria/Tutoria_1A_2017_2018/01_21dic17_bailamos/.bak2")
  #print(str(out))
  #out = director.animSceneDuration("/home/jmramoss/hd/res_slideshow/tests/2x2")
  #out = director.animSceneDuration("/home/jmramoss/hd/res_slideshow/tests/3x3")
  #out = director.animSceneDuration("/home/jmramoss/hd/res_slideshow/tests/4x4")
  #out = director.animSceneDuration("/home/jmramoss/hd/res_slideshow/tests/5x5")
  #out = director.animSceneDuration("/home/jmramoss/hd/res_slideshow/tests/6x6")
  #out = director.animSceneSequential("/home/jmramoss/hd/res_slideshow/tests/2x2")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/2x2")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/3x3")
  #out = director.animSceneSequential("/home/jmramoss/hd/res_slideshow/tests/3x2")
  #out = director.animSceneSequential("/home/jmramoss/hd/res_slideshow/tests/2x2")
  #out = director.animSceneSequential("/home/jmramoss/hd/res_slideshow/tests/3x3")
  #out = director.animSceneSequential("/home/jmramoss/hd/res_slideshow/tests/4x4")
  #out = director.animSceneSequential("/home/jmramoss/hd/res_slideshow/tests/5x5")
  #out = director.animSceneSequential("/home/jmramoss/hd/res_slideshow/tests/6x6")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/6x6")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/5x5")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/4x4")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/3x3")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/2x2")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/6x6")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/5x5")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/4x4")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/3x3")
  #out = director.animSceneDeleiteAllPhotos("/home/jmramoss/hd/res_slideshow/tests/2x2")
  #out = director.animSlideshow("/home/jmramoss/hd/res_slideshow/tests/6x6")
  #out = director.animSlideshow("/home/jmramoss/hd/res_slideshow/unai_colegio_primaria/Tutoria_1A_2017_2018/01_21dic17_bailamos/.bak2")
  out = director.animSlideshow("/media/jmramoss/TOSHIBA EXT13/res_slideshow/unai_colegio_primaria/Tutoria_2A_2018_2019/02/jpg/.bak")
  print(str(out))

  #director.addBgSound("/media/jmramoss/ALMACEN/mp3/Bruno_Mars_-_24K_Magic_Official_Video[myplaylist-youtubemp3.com].mp3", "metal")
  #director.saveMovie(True)
