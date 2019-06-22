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

class Photo:
  def __init__ (self, path):
    self.obj = None
    self.path = os.path.abspath(path)
    self.width = None
    self.height = None
    im = Image.open(self.path)
    self.width, self.height = im.size
    im.close()

  # For call to repr(). Prints object's information
  def __repr__(self):
    return self.path

  # For call to str(). Prints readable form
  def __str__(self):
    return self.path

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
    import bpy
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


if __name__ == '__main__':
  pass

