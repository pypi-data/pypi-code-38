#!/usr/bin/env python2.7
#coding:utf-8

#Convert heic to jpg
#tifig -v -p IMG_3654.heic IMG_3654.jpg

import sys
import os

def _main_ ():
  cwd = os.getcwd()
  srcPath = sys.argv[1]
  if srcPath is not None and not os.path.isabs(srcPath):
    srcPath = os.path.join(cwd, srcPath)

  targetFolder = os.path.join(srcPath, 'jpg')
  if not os.path.isdir(targetFolder):
    os.mkdir(targetFolder)

  files = os.listdir(srcPath)
  for iFile in files:
    if iFile.lower().endswith('.heic'):
      fullPath = os.path.join(srcPath, iFile)
      targetFile = os.path.join(targetFolder, iFile) + '.jpg'
      if not os.path.isfile(targetFile):
        cmd = 'tifig -v -p ' + fullPath + ' ' + targetFile
        print(cmd)
        os.system(cmd)
        cmd2 = 'mogrify -auto-orient ' + targetFile
        print(cmd2)
        os.system(cmd2)

if True and __name__ == '__main__':
  _main_()
