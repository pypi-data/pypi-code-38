#!/usr/bin/env python2.7
#coding:utf-8

#Split video (desde segundo 184 y dura 7 segundos)
#ffmpeg -i thirds.mp4 -ss 184 -t 7 t1.mp4

#Scalar video
#ffmpeg -i video_1920.mp4 -vf scale=640:360 video_640.mp4 -hide_banner

#Convertir video en imágenes
#ffmpeg -i thirds.mp4 -vsync 0 out%d.png

#Plantillas posibles para lower thirds
'''

[sellt6]: https://www.youtube.com/watch?v=1j2SdLcKX8I&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r&index=155
[sellt5]: https://www.youtube.com/watch?v=mdn-x5UW_9E&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r&index=151
[sellt4]: https://www.youtube.com/watch?v=Rdl4TUVQMpw&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r&index=149
[sellt3]: https://www.youtube.com/watch?v=QC0QjW2EWEo&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r&index=120
[sellt2]: https://www.youtube.com/watch?v=7ghdipr6d9w&index=105&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r

[sellt1]: https://www.youtube.com/watch?v=zpvpUrsCne8&index=13&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r

https://mega.nz/#F!LD5zRAwK!dgkpxG7HT9Lw6ANe7ro9Ug

Install bslideshow on Blender
1. curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
2. /home/jmramoss/.__blender__/blender-2.79b-linux-glibc219-x86_64/2.79/python/bin/python3.5m /home/jmramoss/.__blender__/blender-2.79b-linux-glibc219-x86_64/get-pip.py
3. /home/jmramoss/.__blender__/blender-2.79b-linux-glibc219-x86_64/2.79/python/bin/pip install bslideshow

'''

#Generar banner
#cd /media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64
#./blender /media/jmramoss/ALMACEN/pypi/slideshow/third4.blend --background --python /media/jmramoss/ALMACEN/pypi/slideshow/vse5.py
#/media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64/blender /media/jmramoss/ALMACEN/pypi/slideshow/third4.blend --background --python /media/jmramoss/ALMACEN/pypi/slideshow/vse5.py

#import bpy
import sys
import subprocess
import tempfile
import os
import requests
import tarfile
import math
import hjson
import codecs
from PIL import Image
import random

BLENDER_URL = 'https://ftp.halifax.rwth-aachen.de/blender/release/Blender2.79/blender-2.79b-linux-glibc219-x86_64.tar.bz2'
PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'

class BlenderTools:

  '''
DEBUG: pocos frames
DRAFT : Baja resolución
PRODUCTION: Máxima resolución
  '''

  def __init__ (self):
    self.blender = True
    #self.test = False
    self.fps = 24
    self.verbose = False
    self.maxDebugFrames = 24*8
    self.runMode = 'PRODUCTION'
    self.forceFullRender = False
    self.frame_step = 1
    self.forceFrameEnd = None
    pass



  def getResource (self, key, prefix=None):
    result = None

    if os.path.isfile(key):
      result = key
    else:
      home = os.path.expanduser("~")
      target = os.path.join(home, ".__blender__")
      target = os.path.join(target, "resources")
      if not os.path.isdir(target):
        os.makedirs(target)

      targetFile = os.path.join(target, key)
      if not os.path.isfile(targetFile):
        if prefix is not None and key.find('/') < 0:
          key = prefix + os.sep + key
      print("key = " + key)
      targetFile = os.path.join(target, key)
      if not os.path.isfile(targetFile):
        sys.path.append(os.path.dirname(__file__))
        from downloader import Downloader
        downloader = Downloader()
        arrayKey = key.split(os.sep)
        targetFolder = os.path.dirname(targetFile)
        #print("download on " + targetFolder)
        if not os.path.isdir(targetFolder):
          os.makedirs(targetFolder)
        result = downloader.downloadFile(arrayKey[0], arrayKey[1], targetFolder)
      else:
        result = targetFile

    return result

  def installBlender (self):
    #https://www.blender.org/download/Blender2.79/blender-2.79b-linux-glibc219-x86_64.tar.bz2/
    url = BLENDER_URL
    r = requests.get(url, allow_redirects=True)

    home = os.path.expanduser("~")

    target= os.path.join(home, ".__blender__")
    if not os.path.isdir(target):
      os.makedirs(target)

    basename = os.path.basename(url)
    ftar = os.path.join(home, basename)
    open(ftar, 'wb').write(r.content)
    tar = tarfile.open(ftar, "r:bz2")
    tar.extractall(target)
    tar.close()

  '''
Install bslideshow on Blender
1. curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
2. /home/jmramoss/.__blender__/blender-2.79b-linux-glibc219-x86_64/2.79/python/bin/python3.5m /home/jmramoss/.__blender__/blender-2.79b-linux-glibc219-x86_64/get-pip.py
3. /home/jmramoss/.__blender__/blender-2.79b-linux-glibc219-x86_64/2.79/python/bin/pip install bslideshow
  '''
  def setupBlender (self):
    self.__downloadBlenderPip__()
    self.__installBlenderPip__()
    self.__installBlenderBslideshow__()
    pass

  def __downloadBlenderPip__ (self):
    url = PIP_URL
    r = requests.get(url, allow_redirects=True)

    home = os.path.expanduser("~")
    target= os.path.join(home, ".__blender__")
    if not os.path.isdir(target):
      os.makedirs(target)

    basename = os.path.basename(url)
    fpip = os.path.join(target, basename)
    open(fpip, 'wb').write(r.content)

  def __loadPipInstaller__ (self):
    result = None

    home = os.path.expanduser("~")
    target = os.path.join(home, ".__blender__")
    result = os.path.join(target, 'get-pip.py')

    return result

  def __loadDirBlenderDir__ (self):
    result = None
    dirBlender = os.path.dirname(self.checkInstallBlender())
    result = os.path.join(dirBlender, '2.79/python/bin')
    return result

  def __installBlenderPip__ (self):
    dirBlenderBin = self.__loadDirBlenderDir__()
    blenderPython = os.path.join(dirBlenderBin, 'python3.5m')
    pipPath = self.__loadPipInstaller__()
    subprocess.call([blenderPython, pipPath])

  def __installBlenderBslideshow__ (self):
    dirBlenderBin = self.__loadDirBlenderDir__()
    pipPython = os.path.join(dirBlenderBin, 'pip')
    subprocess.call([pipPython, 'install', 'bslideshow'])

  def updateBlenderBslideshow (self):
    dirBlenderBin = self.__loadDirBlenderDir__()
    pipPython = os.path.join(dirBlenderBin, 'pip')
    subprocess.call([pipPython, 'install', '--upgrade', 'bslideshow'])

  def checkInstallBlender (self):
    result = None

    home = os.path.expanduser("~")
    target= os.path.join(home, ".__blender__")

    onlyfiles = [os.path.join(target, f) for f in os.listdir(target) if os.path.isdir(os.path.join(target, f))]
    executable = os.path.join(onlyfiles[0], 'blender')
    if os.path.isfile(executable):
      result = executable

    return result

  def runBlender (self, templatePath, scriptPath):
    #templatePath = "/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend"
    #scriptPath = "/media/jmramoss/ALMACEN/pypi/slideshow/generate_banner.py"
    blenderPath = None
    #blenderPath = "/media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64/blender"

    blenderPath = self.checkInstallBlender()
    if blenderPath is None:
      self.installBlender()
      self.setupBlender()
      blenderPath = self.checkInstallBlender()

    args = [blenderPath, templatePath, "--background", "--python", scriptPath]
    if self.verbose:
      subprocess.call(args)
    else:
      FNULL = open(os.devnull, 'w')
      subprocess.call(args, stdout=FNULL, stderr=FNULL)
    pass

  def runMethodBlender (self, templatePath, method, args, movieOutput=None):
    result = None

    result = self.createTmpMoviePath() if movieOutput is None else movieOutput

    iargs = ""
    argsIdx = 0
    margs = []
    for arg in args:
      #print("arg = " + str(arg) + " type = " + str(type(arg)))
      if type(arg) == str:
        margs.append("'" + arg + "'")
      elif type(arg) == unicode:
        margs.append('u"' + arg.encode('utf-8') + '"')
      else:
        margs.append(arg)
      iargs += (", " if len(iargs) > 0 else "") + "{" + str(argsIdx) + "}"
      argsIdx += 1
    margs.append("'" + result + "'")
    iargs += (", " if len(iargs) > 0 else "") + "{" + str(argsIdx) + "}"

    #scriptPath = "/media/jmramoss/ALMACEN/pypi/slideshow/____fg_23.py"
    #scriptPath = os.path.join(os.path.dirname(__file__), '____fg_23.py')
    scriptPath = tempfile.mkstemp(prefix='.script', suffix='.py')[1]
    #templatePath = "/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend"

    className = self.__class__.__name__
    #className = 'BlenderTools'

    script = open(scriptPath, "w")

    script.write("#!/usr/bin/env python2.7" + "\n")
    script.write("#coding:utf-8" + "\n")
    script.write("" + "\n")

    script.write("import os" + "\n")
    script.write("import sys" + "\n")
    script.write("import bslideshow" + "\n")
    script.write("from collections import OrderedDict" + "\n")
    #script.write("sys.path.append(os.path.dirname(__file__))" + "\n")
    #script.write("from tools import BlenderTools" + "\n")
    script.write("import bpy" + "\n")
    script.write("" + "\n")
    script.write("tools = bslideshow." + className + "()" + "\n")
    self.__writeScriptProperties__(script)
    script.write("tools.blender = False" + "\n")
    script.write("tools." + method + "(" + iargs.format(*margs) + ")" + "\n")

    script.close()

    self.runBlender(templatePath, scriptPath)

    os.remove(scriptPath)

    return result


  def __writeScriptProperties__ (self, script):
    script.write("tools.fps = {0}".format(str(self.fps)) + "\n")
    script.write("tools.verbose = {0}".format(str(self.verbose)) + "\n")
    script.write("tools.maxDebugFrames = {0}".format(str(self.maxDebugFrames)) + "\n")
    script.write("tools.runMode = '{0}'".format(self.runMode) + "\n")
    script.write("tools.frame_step = {0}".format(str(self.frame_step)) + "\n")

  '''
  def runAddForeground (self, moviePath, foregroundPath, movieOutput=None):
    result = None

    result = self.createTmpMoviePath() if movieOutput is None else movieOutput

    scriptPath = "/media/jmramoss/ALMACEN/pypi/slideshow/____fg.py"
    templatePath = "/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend"

    script = open(scriptPath, "w")

    script.write("#!/usr/bin/env python2.7" + "\n")
    script.write("#coding:utf-8" + "\n")
    script.write("" + "\n")

    script.write("import os" + "\n")
    script.write("import sys" + "\n")
    script.write("sys.path.append(os.path.dirname(__file__))" + "\n")
    script.write("from tools import BlenderTools" + "\n")
    script.write("import bpy" + "\n")
    script.write("" + "\n")
    script.write("tools = BlenderTools()" + "\n")
    script.write("tools.blender = False" + "\n")
    script.write("tools.runMode = '{0}'".format(self.runMode) + "\n")
    script.write("tools.addForeground('{0}', '{1}', '{2}')".format(moviePath, foregroundPath, result) + "\n")

    script.close()

    self.runBlender(templatePath, scriptPath)

    return result
  '''

  '''
    subprocess.call(["/media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64/blender", "/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend", "--background", "--python", "/media/jmramoss/ALMACEN/pypi/slideshow/generate_banner.py"])



  '''
  #Más overlays: https://www.youtube.com/watch?v=gcNo1cqyubU
  def addForeground (self, moviePath, foregroundPath, movieOutput=None):
    result = None

    foregroundPath = self.getResource(foregroundPath, 'footages')

    if self.blender:
      #result = self.runAddForeground(moviePath, foregroundPath, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend"
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "addForeground", [moviePath, foregroundPath], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
      video1 = sequences.new_movie("video1", moviePath, 1, 1)
      audio1 = sequences.new_sound("audio1", moviePath, 2, 1)

      #foreground = sequences.new_movie("fg1", "/media/jmramoss/ALMACEN/pypi/slideshow/foreground2.mp4", 2, 1)
      #print("LENGTH FOREGROUND = " + str(foreground.frame_duration))
      #print("LENGTH VIDEO = " + str(video1.frame_duration))

      duration_cubierta = 0
      offset_layer = 3

      #       frame_end=frame_end,
      #add_strip = sequences.new_effect("minameAdd", 'ADD', offset_layer, frame_start=1, seq1=foreground, seq2=video1)

      #foregroundPath = "/media/jmramoss/ALMACEN/pypi/slideshow/foreground2.mp4"
      while duration_cubierta < video1.frame_duration:
        foreground = sequences.new_movie("fg" + str(offset_layer), foregroundPath, offset_layer, duration_cubierta + 1)
        #       frame_end=frame_end,
        add_strip = sequences.new_effect("minameAdd" + str(offset_layer), 'ADD', offset_layer + 1, frame_start=duration_cubierta + 1, seq1=foreground, seq2=video1)
        duration_cubierta += foreground.frame_duration
        offset_layer += 2

      result = self.saveMovie(frameStart=1, frameEnd=video1.frame_duration, movieOutput=movieOutput)

    return result


  def getInfo (self, moviePath, tmpFile=None):
    result = None

    if self.blender:
      templatePath = self.getResource('encode.blend', 'templates')
      result = self.runMethodBlender(templatePath, "getInfo", [moviePath], movieOutput=tmpFile)
      fp = codecs.open(result, mode='r', encoding='utf-8')
      result = hjson.load(fp)
      #print(">>> oytttttttttt = " + str(result))
    else:
      import bpy

      frames = None
      width = None
      height = None

      try:
        movieClip = bpy.data.movieclips.load(moviePath)
        #print(str(movieClip))

        frames = movieClip.frame_duration
        width = movieClip.size[0]
        height = movieClip.size[1]
      except:
        pass

      if frames is None or frames == 0:
        context = bpy.context
        scene = context.scene
        scene.sequence_editor_create()
        sed = scene.sequence_editor
        sequences = sed.sequences

        #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
        audio = sequences.new_sound("audio1", moviePath, 1, 1)

        frames = audio.frame_duration
        width = None
        height = None

      dataResult = {
        "frames": frames,
        "width": width,
        "height": height
      }

      result = tempfile.mkstemp(prefix='.info', suffix='.hjson')[1] if tmpFile is None else tmpFile
      fp = codecs.open(result, mode='w', encoding='utf-8')
      hjson.dump(dataResult, fp)

      #print(">>> result = " + str(result))

    return result



  '''
  def runGenerateBanner (self, title, subtitle = None, title_right = None, subtitle_right = None, movieOutput=None):
    result = None

    result = self.createTmpMoviePath() if movieOutput is None else movieOutput

    scriptPath = "/media/jmramoss/ALMACEN/pypi/slideshow/___gb.py"
    templatePath = "/media/jmramoss/ALMACEN/pypi/slideshow/generateBanner.blend"

    script = open(scriptPath, "w")

    script.write("#!/usr/bin/env python2.7" + "\n")
    script.write("#coding:utf-8" + "\n")
    script.write("" + "\n")
    script.write("import os" + "\n")
    script.write("import sys" + "\n")
    script.write("sys.path.append(os.path.dirname(__file__))" + "\n")
    script.write("from tools import BlenderTools" + "\n")
    script.write("import bpy" + "\n")
    script.write("" + "\n")
    script.write("tools = BlenderTools()" + "\n")
    script.write("tools.blender = False" + "\n")
    script.write("tools.runMode = '{0}'".format(self.runMode) + "\n")
    script.write("tools.generateBanner('{0}', '{1}', '{2}', '{3}', '{4}')".format(title, subtitle, title_right, subtitle_right, result) + "\n")

    script.close()

    self.runBlender(templatePath, scriptPath)

    return result
  '''

  '''
    subprocess.call(["/media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64/blender", "/media/jmramoss/ALMACEN/pypi/slideshow/generateBanner.blend", "--background", "--python", "/media/jmramoss/ALMACEN/pypi/slideshow/generate_banner.py"])
  '''
  def generateBanner (self, title, subtitle = None, title_right = None, subtitle_right = None, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runGenerateBanner(title, subtitle, title_right, subtitle_right, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/generateBanner.blend"
      templatePath = self.getResource('generateBanner.blend', 'templates')
      result = self.runMethodBlender(templatePath, "generateBanner", [title, subtitle, title_right, subtitle_right], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene

      bpy.data.images['prepared_best_t5.mp4'].filepath = '/home/jmramoss/.__blender__/resources/thirds/prepared_best_t5.mp4'
      bpy.data.images['logo3.png'].filepath = '/home/jmramoss/.__blender__/resources/thirds/logo3.png'

      oTitle = bpy.data.objects['Title']
      oTitle.data.body = title if title is not None else ""#"Lorem Ipsum"

      oSubtitle = bpy.data.objects['Subtitle']
      oSubtitle.data.body = subtitle if subtitle is not None else ""#"Descripción de Lorem Ipsum"

      oTitleRight = bpy.data.objects['title_right']
      oTitleRight.data.body = title_right if title_right is not None else ""#"Periquito"#""#"Dic 2017"

      oSubtitleRight = bpy.data.objects['subtitle_right']
      oSubtitleRight.data.body = subtitle_right if subtitle_right is not None else ""#"Nuevo año 2019"#""#"Curso 2017-2018"

      #img = bpy.data.images["logo3.png"]
      #img.filepath = "//logo3.png"

      result = self.saveMovie(frameStart=1, frameEnd=250, movieOutput=movieOutput)

    return result

  #Best Green Screen Title Effets | Copyright Free || by technical dhamaka
  #https://www.youtube.com/watch?v=oXhcryU0mvU
  #https://www.youtube.com/watch?v=d2TJZTAO5sQ
  def generateTitle (self, title, subtitle = None, title_right=None, subtitle_right = None, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('generateTitle13.blend', 'templates')
      result = self.runMethodBlender(templatePath, "generateTitle", [title, subtitle, title_right, subtitle_right], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene

      bpy.data.images['video'].filepath = '/home/jmramoss/hd/res_slideshow/bslideshow/titles/title13.mp4'
      bpy.data.images['logo3.png'].filepath = '/home/jmramoss/hd/res_slideshow/project/logo.png'

      oTitle = bpy.data.objects['Title']
      oTitle.data.body = title if title is not None else ""#"Lorem Ipsum"

      oSubtitle = bpy.data.objects['Subtitle']
      oSubtitle.data.body = subtitle if subtitle is not None else ""#"Descripción de Lorem Ipsum"

      oTitleRight = bpy.data.objects['title_right']
      oTitleRight.data.body = title_right if title_right is not None else ""#"Periquito"#""#"Dic 2017"

      oSubtitleRight = bpy.data.objects['subtitle_right']
      oSubtitleRight.data.body = subtitle_right if subtitle_right is not None else ""#"Nuevo año 2019"#""#"Curso 2017-2018"

      result = self.saveMovie(frameStart=1, frameEnd=240, movieOutput=movieOutput)

    return result

  def _sort_names(self, imgPath):
    result = None
    imname = os.path.splitext(os.path.basename(imgPath))[0]
    while imname[0] == '0':
      imname = imname[1:]
    result = int(imname)
    return result

  def encode (self, inpath, mode, prefix = None, outpath = None):
    result = None
    if outpath is None:
      outpath = tempfile.mkdtemp(prefix=os.path.basename(inpath), suffix='_out', dir=os.path.dirname(inpath))
    if not os.path.isdir(outpath) and not os.path.isfile(outpath):
      os.makedirs(outpath)
    if os.path.isdir(inpath):
      movies = [os.path.join(inpath, f) for f in os.listdir(inpath) if os.path.isfile(os.path.join(inpath, f))]
      idx = 1
      prefix = prefix if prefix is not None else ''
      for moviePath in movies:
        outMovie = os.path.join(outpath, prefix + str(idx) + '.mp4')
        self.encodeMovie(moviePath, mode, outMovie)
        idx += 1
      result = outpath
    else:
      result = self.encodeMovie(inpath, mode, outpath)
    return result

  def encodeMovie (self, inpath, mode, outpath = None):
    result = None
    if os.path.isfile(inpath):
      if outpath is None:
        outpath = os.path.join(tempfile.mkdtemp(prefix=os.path.basename(inpath), suffix='_out', dir=os.path.dirname(inpath)), os.path.basename(inpath))
      if self.blender:
        templatePath = self.getResource('encode.blend', 'templates')
        result = self.runMethodBlender(templatePath, "encodeMovie", [inpath, mode], movieOutput=outpath)
      else:
        import bpy

        movieClip = bpy.data.movieclips.load(inpath)
        bpy.context.scene.node_tree.nodes['movie'].clip = movieClip

        frameEnd = movieClip.frame_duration
        width = movieClip.size[0]
        height = movieClip.size[1]

        self.runMode = mode
        result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=outpath, resolution_x = width, resolution_y = height)
    return result

  def splitGs (self, inpath, moviePath=None, offset=24, outpath=None):
    result = None

    result = list()
    folder = inpath
    if os.path.isfile(inpath):
      folder = self.frames(inpath)
    images = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    images = sorted(images, key=self._sort_names)
    #print(str(images))
    #quit()
    #images.sort()
    numImages = len(images) if images is not None else 0
    if numImages > 1:
      im = Image.open(images[0])
      rgb_im = im.convert('RGB')
      greenColor = rgb_im.getpixel((0, 0))
      print(str(greenColor))
      rgb_im.close()
      im.close()
      #quit()

      speed = 24

      idx = speed
      frameStart = -1
      frameEnd = -1
      while idx < numImages:
        imgPath = images[idx]
        imname = os.path.splitext(os.path.basename(imgPath))[0]
        greenScreen = self.checkImgGreenScreen(imgPath, greenColor)

        if frameStart < 0 and not greenScreen:
          if speed < 2:
            frameStart = idx
          else:
            ridx = idx - 1
            while not self.checkImgGreenScreen(images[ridx], greenColor):
              ridx -= 1
            frameStart = ridx + 1

        if frameStart > 0 and frameEnd < 0 and greenScreen:
          if speed < 2:
            frameEnd = idx - 1
          else:
            ridx = idx - 1
            while self.checkImgGreenScreen(images[ridx], greenColor):
              ridx -= 1
            frameEnd = ridx

        print("imname = " + imname + " idx = " + str(idx) + " greenScreen = " + str(greenScreen) + " frameStart = " + str(frameStart) + " frameEnd = " + str(frameEnd))

        if frameStart > 0 and frameEnd > 0:
          frameStart -= offset
          frameEnd += offset
          result.append([frameStart, frameEnd])
          print(str(result))
          frameStart = -1
          frameEnd = -1

        idx += speed

    if moviePath is not None:
      movies = list()
      for dataItem in result:
        frameStart = dataItem[0]
        frameEnd = dataItem[1]
        out = self.split(moviePath, frameStart, frameEnd)
        movies.append(out)
        print(out)
      result = movies

    return result

  def checkImgGreenScreen (self, imgPath, greenColor):
    result = True
    im = Image.open(imgPath)
    rgb_im = im.convert('RGB')
    for wIdx in range(0, rgb_im.width, 4):
      for hIdx in range(0, rgb_im.height, 4):
        color = rgb_im.getpixel((wIdx, hIdx))
        distance = self.getDistanceColor(color, greenColor)
        if distance > 40:
          print(str(distance))
          result = False
          break
      if not result:
        break
    rgb_im.close()
    im.close()
    return result

  def getDistanceColor (self, color, greenColor):
    result = None
    r = (greenColor[0] - color[0])
    r = r * r
    g = (greenColor[1] - color[1])
    g = g * g
    b = (greenColor[2] - color[2])
    b = b * b
    result = math.sqrt(r + g + b)
    return result

  def split (self, moviePath, frameStart, frameEnd, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runGenerateBanner(title, subtitle, title_right, subtitle_right, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/generateBanner.blend"
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "split", [moviePath, frameStart, frameEnd], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
      video1 = sequences.new_movie("video1", moviePath, 1, 1)
      audio1 = sequences.new_sound("audio1", moviePath, 2, 1)

      result = self.saveMovie(frameStart=frameStart, frameEnd=frameEnd, movieOutput=movieOutput)

    return result

  def merge (self, movie1Path, movie2Path, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "merge", [movie1Path, movie2Path], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
      video1 = sequences.new_movie("video1", movie1Path, 1, 1)
      audio1 = sequences.new_sound("audio1", movie1Path, 2, 1)

      video2 = sequences.new_movie("video2", movie2Path, 3, video1.frame_duration + 1)
      audio2 = sequences.new_sound("audio2", movie2Path, 4, video1.frame_duration + 1)

      result = self.saveMovie(frameStart=1, frameEnd=video1.frame_duration + video2.frame_duration, movieOutput=movieOutput)

    return result

  def mergeMultiples (self, moviesPath, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "mergeMultiples", [moviesPath], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      frame = 1
      channel = 1
      for moviePath in moviesPath:
        video = sequences.new_movie("video" + str(channel), moviePath, channel, frame)
        channel += 1
        audio = sequences.new_sound("audio" + str(channel), moviePath, channel, frame)
        channel += 1
        frame += video.frame_duration + 1

      result = self.saveMovie(frameStart=1, frameEnd=frame, movieOutput=movieOutput)

    return result


  def scale (self, moviePath, width = 1920, height = 1080, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runGenerateBanner(title, subtitle, title_right, subtitle_right, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/generateBanner.blend"
      templatePath = self.getResource('scale.blend', 'templates')
      result = self.runMethodBlender(templatePath, "scale", [moviePath, width, height], movieOutput=movieOutput)
    else:
      import bpy

      movieClip = bpy.data.movieclips.load(moviePath)
      bpy.context.scene.node_tree.nodes['movie'].clip = movieClip

      frameEnd = movieClip.frame_duration

      result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput, resolution_x = width, resolution_y = height)

    return result

  def frames (self, moviePath, frameStart=None, frameEnd=None, folderOutput=None):
    result = None

    if self.blender:
      #result = self.runGenerateBanner(title, subtitle, title_right, subtitle_right, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/generateBanner.blend"
      folderOutput = tempfile.mkdtemp(prefix='.frames', suffix='.png', dir=os.path.dirname(moviePath)) if folderOutput is None else folderOutput
      folderOutput += "" if folderOutput.endswith(os.sep) else os.sep
      print("folderOutput = " + folderOutput)
      templatePath = self.getResource('frames.blend', 'templates')
      result = self.runMethodBlender(templatePath, "frames", [moviePath, frameStart, frameEnd], movieOutput=folderOutput)
    else:
      import bpy

      movieClip = bpy.data.movieclips.load(moviePath)
      bpy.context.scene.node_tree.nodes['movie'].clip = movieClip

      frameStart = frameStart if frameStart is not None else 1
      frameEnd = frameEnd if frameEnd is not None else movieClip.frame_duration

      #print(str(movieClip.size[0]))
      #print(str(movieClip.size[1]))
      resolution_x = movieClip.size[0]
      resolution_y = movieClip.size[1]
      #resolution_x = 1920
      #resolution_y = 1080

      result = self.saveFrames(frameStart=frameStart, frameEnd=frameEnd, folderOutput=folderOutput, resolution_x = resolution_x, resolution_y = resolution_y)

    return result


  '''
  def runOffset (self, moviePath, framesOffset = 48, color=None, movieOutput=None):
    result = None

    result = self.createTmpMoviePath() if movieOutput is None else movieOutput

    scriptPath = "/media/jmramoss/ALMACEN/pypi/slideshow/___bo.py"
    templatePath = "/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend"

    script = open(scriptPath, "w")

    script.write("#!/usr/bin/env python2.7" + "\n")
    script.write("#coding:utf-8" + "\n")
    script.write("" + "\n")
    script.write("import os" + "\n")
    script.write("import sys" + "\n")
    script.write("sys.path.append(os.path.dirname(__file__))" + "\n")
    script.write("from tools import BlenderTools" + "\n")
    script.write("import bpy" + "\n")
    script.write("" + "\n")
    script.write("tools = BlenderTools()" + "\n")
    script.write("tools.blender = False" + "\n")
    script.write("tools.runMode = '{0}'".format(self.runMode) + "\n")
    script.write("tools.addOffset('{0}', {1}, {2}, '{3}')".format(moviePath, framesOffset, color, result) + "\n")

    script.close()

    self.runBlender(templatePath, scriptPath)

    return result
  '''


  '''
    subprocess.call(["/media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64/blender", "/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend", "--background", "--python", "/media/jmramoss/ALMACEN/pypi/slideshow/generate_banner.py"])
  '''
  def addOffset (self, moviePath, framesOffset = 48, color=None, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runOffset(moviePath, framesOffset, color, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend"
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "addOffset", [moviePath, framesOffset, color], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/banner.mp4"

      color = sequences.new_effect("color", 'COLOR', 1, 1, framesOffset)
      color.color = (0.006, 0.991, 0.006)

      video1 = sequences.new_movie("video1", moviePath, 2, framesOffset)
      audio1 = sequences.new_sound("audio1", moviePath, 3, framesOffset)

      #print("LENGTH VIDEO = " + str(video1.frame_duration))

      result = self.saveMovie(frameStart=1, frameEnd=framesOffset + video1.frame_duration, movieOutput=movieOutput)

    return result

  '''
  def runDorr (self, moviePath, bannerPath, movieOutput=None):
    result = None

    result = self.createTmpMoviePath() if movieOutput is None else movieOutput

    scriptPath = "/media/jmramoss/ALMACEN/pypi/slideshow/__ab.py"
    templatePath = "/media/jmramoss/ALMACEN/pypi/slideshow/banner_overlap2.blend"

    script = open(scriptPath, "w")

    script.write("#!/usr/bin/env python2.7" + "\n")
    script.write("#coding:utf-8" + "\n")
    script.write("" + "\n")
    script.write("import os" + "\n")
    script.write("import sys" + "\n")
    script.write("sys.path.append(os.path.dirname(__file__))" + "\n")
    script.write("from tools import BlenderTools" + "\n")
    script.write("import bpy" + "\n")
    script.write("" + "\n")
    script.write("tools = BlenderTools()" + "\n")
    script.write("tools.blender = False" + "\n")
    script.write("tools.runMode = '{0}'".format(self.runMode) + "\n")
    script.write("tools.doAddBanner('{0}', '{1}', '{2}')".format(moviePath, bannerPath, result) + "\n")

    script.close()

    self.runBlender(templatePath, scriptPath)

    return result
  '''

  '''
    subprocess.call(["/media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64/blender", "/media/jmramoss/ALMACEN/pypi/slideshow/banner_overlap2.blend", "--background", "--python", "/media/jmramoss/ALMACEN/pypi/slideshow/add_banner.py"])
  '''
  def doAddBanner (self, moviePath, bannerPath, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runDoAddBanner(moviePath, bannerPath, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/banner_overlap2.blend"
      templatePath = self.getResource('banner_overlap2.blend', 'templates')
      result = self.runMethodBlender(templatePath, "doAddBanner", [moviePath, bannerPath], movieOutput=movieOutput)
    else:
      import bpy
      #nodes = bpy.data.scenes['Scene'].node_tree.nodes
      #print(str(nodes))
      #clip_path =
      #get the new movie clip
      #movie_clip = bpy.data.movieclips.get(clip_name)
      ##assign movie clip to the node
      context = bpy.context
      scene = context.scene
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video3.mp4"
      movieClip = bpy.data.movieclips.load(moviePath)
      #bpy.context.scene.node_tree.nodes['video'].clip = movieClip

      #bannerPath = "/media/jmramoss/ALMACEN/pypi/slideshow/banner.mp4"
      #bannerPath = "/media/jmramoss/ALMACEN/pypi/slideshow/banner_offset.mkv"
      bannerClip = bpy.data.movieclips.load(bannerPath)
      bpy.context.scene.node_tree.nodes['banner'].clip = bannerClip

      #print(">>>>>>>")
      #print(str(bpy.data.movieclips))
      #video
      #banner
      #nodes['Alpha Over'].premul

      sed.sequences_all["seq_movie"].filepath = moviePath
      #sed.sequences_all["seq_audio"].sound = filepath = moviePath

      sed.sequences_all["scene"].frame_final_duration = bannerClip.frame_duration - 2
      sed.sequences_all["seq_movie"].frame_final_duration = movieClip.frame_duration - 1
      #sed.sequences_all["seq_audio"].frame_final_duration = movieClip.frame_duration - 1

      audio1 = sed.sequences.new_sound("audio1", moviePath, 1, 1)

      frameEnd = movieClip.frame_duration
      result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)
      print("QQQQQQQQQQQQQQQQQQQ QQQQQQQQQQQQ")
      bpy.ops.wm.save_as_mainfile(filepath="/tmp/doAddBanner.blend")


    return result

  def applyBlur (self, moviePath, offset, sizeBlur=50.0, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "applyBlur", [moviePath, offset, sizeBlur], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
      video = sequences.new_movie("video1", moviePath, 1, 1)
      audio = sequences.new_sound("audio1", moviePath, 2, 1)

      startBlur = offset
      endBlur = offset + (2*24)

      blur = sequences.new_effect("transform_blur", 'GAUSSIAN_BLUR', 3, frame_start=startBlur, frame_end=endBlur, seq1=video)
      blur.blend_type = 'REPLACE'
      blur.size_x = 0.0
      blur.size_y = 0.0
      blur.keyframe_insert(data_path="size_x", frame=startBlur)
      blur.keyframe_insert(data_path="size_y", frame=startBlur)
      blur.size_x = sizeBlur
      blur.size_y = sizeBlur
      blur.keyframe_insert(data_path="size_x", frame=endBlur)
      blur.keyframe_insert(data_path="size_y", frame=endBlur)
      blur.keyframe_insert(data_path="size_x", frame=video.frame_duration)
      blur.keyframe_insert(data_path="size_y", frame=video.frame_duration)

      result = self.saveMovie(frameStart=1, frameEnd=video.frame_duration, movieOutput=movieOutput)
      #bpy.ops.wm.save_mainfile(filepath="/tmp/mifile3.blend")
      bpy.ops.wm.save_as_mainfile(filepath="/tmp/applyBlur.blend")

    return result


  def doAddGreenScreen (self, moviePath, bannerPath, offset, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runDoAddBanner(moviePath, bannerPath, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/banner_overlap2.blend"
      templatePath = self.getResource('banner_overlap2.blend', 'templates')
      result = self.runMethodBlender(templatePath, "doAddGreenScreen", [moviePath, bannerPath, offset], movieOutput=movieOutput)
    else:
      import bpy
      #nodes = bpy.data.scenes['Scene'].node_tree.nodes
      #print(str(nodes))
      #clip_path =
      #get the new movie clip
      #movie_clip = bpy.data.movieclips.get(clip_name)
      ##assign movie clip to the node
      context = bpy.context
      scene = context.scene
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video3.mp4"
      movieClip = bpy.data.movieclips.load(moviePath)
      #bpy.context.scene.node_tree.nodes['video'].clip = movieClip

      #bannerPath = "/media/jmramoss/ALMACEN/pypi/slideshow/banner.mp4"
      #bannerPath = "/media/jmramoss/ALMACEN/pypi/slideshow/banner_offset.mkv"
      bannerClip = bpy.data.movieclips.load(bannerPath)
      bpy.context.scene.node_tree.nodes['banner'].clip = bannerClip

      #print(">>>>>>>")
      #print(str(bpy.data.movieclips))
      #video
      #banner
      #nodes['Alpha Over'].premul

      sed.sequences_all["seq_movie"].filepath = moviePath
      #sed.sequences_all["seq_audio"].sound = filepath = moviePath

      sed.sequences_all["scene"].frame_start = offset
      sed.sequences_all["scene"].frame_final_duration = bannerClip.frame_duration
      sed.sequences_all["seq_movie"].frame_start = 1
      sed.sequences_all["seq_movie"].frame_final_duration = movieClip.frame_duration
      #sed.sequences_all["seq_audio"].frame_final_duration = movieClip.frame_duration - 1

      audio1 = sed.sequences.new_sound("audio1", moviePath, 1, 1)

      frameEnd = movieClip.frame_duration
      result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)
      print("QQQQQQQQQQQQQQQQQQQ QQQQQQQQQQQQ")
      bpy.ops.wm.save_as_mainfile(filepath="/tmp/doAddGrenScreen.blend")


    return result




  def doAddBanner_old (self, moviePath, bannerPath, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runDoAddBanner(moviePath, bannerPath, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/banner_overlap2.blend"
      templatePath = self.getResource('banner_overlap2.blend', 'templates')
      result = self.runMethodBlender(templatePath, "doAddBanner", [moviePath, bannerPath], movieOutput=movieOutput)
    else:
      import bpy
      #nodes = bpy.data.scenes['Scene'].node_tree.nodes
      #print(str(nodes))
      #clip_path =
      #get the new movie clip
      #movie_clip = bpy.data.movieclips.get(clip_name)
      ##assign movie clip to the node

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video3.mp4"
      movieClip = bpy.data.movieclips.load(moviePath)
      bpy.context.scene.node_tree.nodes['video'].clip = movieClip

      #bannerPath = "/media/jmramoss/ALMACEN/pypi/slideshow/banner.mp4"
      #bannerPath = "/media/jmramoss/ALMACEN/pypi/slideshow/banner_offset.mkv"
      bannerClip = bpy.data.movieclips.load(bannerPath)
      bpy.context.scene.node_tree.nodes['banner'].clip = bannerClip

      #print(">>>>>>>")
      #print(str(bpy.data.movieclips))
      #video
      #banner
      #nodes['Alpha Over'].premul

      frameEnd = bpy.context.scene.node_tree.nodes['video'].clip.frame_duration
      result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)

    return result



  '''
  def runDoAddMusic (self, moviePath, musicPath, movieOutput=None):
    result = None

    result = self.createTmpMoviePath() if movieOutput is None else movieOutput

    scriptPath = "/media/jmramoss/ALMACEN/pypi/slideshow/__am.py"
    templatePath = "/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend"

    script = open(scriptPath, "w")

    script.write("#!/usr/bin/env python2.7" + "\n")
    script.write("#coding:utf-8" + "\n")
    script.write("" + "\n")
    script.write("import os" + "\n")
    script.write("import sys" + "\n")
    script.write("sys.path.append(os.path.dirname(__file__))" + "\n")
    script.write("from tools import BlenderTools" + "\n")
    script.write("import bpy" + "\n")
    script.write("" + "\n")
    script.write("tools = BlenderTools()" + "\n")
    script.write("tools.blender = False" + "\n")
    script.write("tools.runMode = '{0}'".format(self.runMode) + "\n")
    script.write("tools.doAddMusic('{0}', '{1}', '{2}')".format(moviePath, musicPath, result) + "\n")

    script.close()

    self.runBlender(templatePath, scriptPath)

    return result
  '''

  '''
    subprocess.call(["/media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64/blender", "/media/jmramoss/ALMACEN/pypi/slideshow/banner_overlap2.blend", "--background", "--python", "/media/jmramoss/ALMACEN/pypi/slideshow/add_banner.py"])
  '''
  def doAddMusic (self, moviePath, musicPath, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runDoAddMusic(moviePath, musicPath, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend"
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "doAddMusic", [moviePath, musicPath], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
      video1 = sequences.new_movie("video1", moviePath, 1, 1)
      audio1 = sequences.new_sound("audio1", musicPath, 2, 1)

      result = self.saveMovie(frameStart=1, frameEnd=video1.frame_duration, movieOutput=movieOutput)

    return result

  def musicTime2Seconds (self, time):
    result = None
    if time is not None and len(time) > 0:
      time = time.strip()
      minutes = int(time.split(":")[0])
      seconds = int(time.split(":")[1])
      result = (minutes*60) + seconds
    return result

  def doAddBackgroundMusic (self, moviePath, musicData, lenFadeIn=120, lenFadeOut=120, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runDoAddMusic(moviePath, musicPath, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/empty.blend"
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "doAddBackgroundMusic", [moviePath, musicData, lenFadeIn, lenFadeOut], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
      video1 = sequences.new_movie("video1", moviePath, 1, 1)
      channel = 3
      offset = 1
      for itemMusicData in musicData:
        musicPath = itemMusicData['path']
        musicStart = self.musicTime2Seconds(itemMusicData['start']) if 'start' in itemMusicData else None
        musicEnd = self.musicTime2Seconds(itemMusicData['end']) if 'end' in itemMusicData else None

        audio = sequences.new_sound("audio" + str(channel), musicPath, channel, offset)

        #lenFadeIn = (5*24)
        #lenFadeOut = (5*24)

        trimStart = 0
        trimEnd = 0
        if musicEnd is not None and musicStart is None:
          musicStart = 0
        if musicStart is not None and musicEnd is None:
          musicEnd = int(audio.frame_duration / 24)
        if musicStart is not None:
          print("music start = " + str(musicStart))
          trimStart = musicStart * 24
        if True and musicEnd is not None:
          print("music end = " + str(musicEnd))
          trimEnd = audio.frame_duration - (musicEnd * 24)
        videoFrameDuration = video1.frame_duration
        audioFrameDuration = audio.frame_duration
        audioFrameDuration -= trimStart
        audioFrameDuration -= trimEnd

        print(">>>>>>>>>>>>>>>>>>>>> AAAAAAAAAAAAAAAAAAAAAAAA")
        audio.animation_offset_start = trimStart
        audio.animation_offset_end = trimEnd
        audio.frame_start = offset
        if True and musicStart is not None and musicEnd is not None:
          audio.frame_final_duration = (musicEnd - musicStart) * 24

        #sequence_editor.sequences_all["Cleric_-_Loveliness.mp3"].volume = 1.0
        if lenFadeIn > 0:
          audio.volume = 0.0
          audio.keyframe_insert(data_path="volume", frame=offset)
        audio.volume = 1.0
        audio.keyframe_insert(data_path="volume", frame=offset + lenFadeIn)

        audio.volume = 1.0
        audio.keyframe_insert(data_path="volume", frame=offset + audioFrameDuration - lenFadeOut)
        if lenFadeOut > 0:
          audio.volume = 0.0
          audio.keyframe_insert(data_path="volume", frame=offset + audioFrameDuration)


        offset += audioFrameDuration
        channel += 1

      result = self.saveMovie(frameStart=1, frameEnd=video1.frame_duration, movieOutput=movieOutput)
      bpy.ops.wm.save_as_mainfile(filepath="/tmp/bg_music_fadeq12.blend")

    return result



  '''
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
  '''






  '''
  def runDoAddTransition (self, movie1Path, movie2Path, movieOutput=None):
    result = None

    result = self.createTmpMoviePath() if movieOutput is None else movieOutput

    scriptPath = "/media/jmramoss/ALMACEN/pypi/slideshow/__tr.py"
    templatePath = "/media/jmramoss/ALMACEN/pypi/slideshow/transition.blend"

    script = open(scriptPath, "w")

    script.write("#!/usr/bin/env python2.7" + "\n")
    script.write("#coding:utf-8" + "\n")
    script.write("" + "\n")
    script.write("import os" + "\n")
    script.write("import sys" + "\n")
    script.write("sys.path.append(os.path.dirname(__file__))" + "\n")
    script.write("from tools import BlenderTools" + "\n")
    script.write("import bpy" + "\n")
    script.write("" + "\n")
    script.write("tools = BlenderTools()" + "\n")
    script.write("tools.blender = False" + "\n")
    script.write("tools.runMode = '{0}'".format(self.runMode) + "\n")
    script.write("tools.doAddTransition('{0}', '{1}', '{2}')".format(movie1Path, movie2Path, result) + "\n")

    script.close()

    self.runBlender(templatePath, scriptPath)

    return result
  '''

  '''
    subprocess.call(["/media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64/blender", "/media/jmramoss/ALMACEN/pypi/slideshow/banner_overlap2.blend", "--background", "--python", "/media/jmramoss/ALMACEN/pypi/slideshow/add_banner.py"])
  '''
  def doAddTransition (self, movie1Path, movie2Path, transitionPath=None, movieOutput=None):
    result = None

    if self.blender:
      #result = self.runDoAddTransition(movie1Path, movie2Path, movieOutput)
      #"/media/jmramoss/ALMACEN/pypi/slideshow/transition.blend"
      templatePath = self.getResource('transition.blend', 'templates')
      transitionPath = transitionPath if transitionPath is not None else 'transition1.mp4'
      result = self.runMethodBlender(templatePath, "doAddTransition", [movie1Path, movie2Path, transitionPath], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      #scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      # deselect all
      #bpy.ops.object.select_all(action='DESELECT')
      # selection
      #bpy.data.objects['Camera'].select = True
      # remove it
      #bpy.ops.object.delete()

      #bpy.ops.object.select_all(action='DESELECT')
      #sequences['video1'].select = True
      #sequences['audio1'].select = True
      #sequences['video2'].select = True
      #sequences['audio2'].select = True
      #bpy.ops.object.delete()

      '''
      sequences['video1'].filepath = movie1Path
      sequences['audio1'].sound.filepath = movie1Path

      sequences['video2'].filepath = movie2Path
      sequences['audio2'].sound.filepath = movie2Path
      '''

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"

      #transitionPath = "/media/jmramoss/ALMACEN/pypi/slideshow/transition2.mp4"
      transitionPath = self.getResource(transitionPath, 'transitions')
      movieClip = bpy.data.movieclips.load(transitionPath)
      bpy.context.scene.node_tree.nodes['movieTransition'].clip = movieClip


      video1 = sequences.new_movie("video1", movie1Path, 1, 1)
      audio1 = sequences.new_sound("audio1", movie1Path, 2, 1)

      video2 = sequences.new_movie("video2", movie2Path, 1, video1.frame_duration + 1)
      audio2 = sequences.new_sound("audio2", movie2Path, 2, video1.frame_duration + 1)

      transition = sequences['transition']
      transition.frame_start = video1.frame_duration - int(transition.frame_final_duration / 2)

      frameEnd = video1.frame_duration + video2.frame_duration
      result = self.saveMovie(frameStart=1, frameEnd=frameEnd, movieOutput=movieOutput)

    return result

  def fadeIn (self, moviePath, duration=48, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "fadeIn", [moviePath, duration], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
      video1 = sequences.new_movie("video1", moviePath, 1, 1)
      audio1 = sequences.new_sound("audio1", moviePath, 2, 1)

      frameStart = 1
      frameEnd = duration

      color_strip = sequences.new_effect("color", 'COLOR', 3, frame_start=frameStart, frame_end=frameEnd)
      color_strip.color = (0.000, 0.000, 0.000)
      gamma_cross_strip = sequences.new_effect("color", 'GAMMA_CROSS', 4, frame_start=frameStart, frame_end=frameEnd, seq1=color_strip, seq2=video1)

      result = self.saveMovie(frameStart=1, frameEnd=video1.frame_duration, movieOutput=movieOutput)

    return result




  def mergeWithTransform (self, moviesPath, transforms=None, transitionDuration = 96, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "mergeWithTransform", [moviesPath, transforms, transitionDuration], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      first = moviesPath.pop(0)

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
      video = sequences.new_movie("video0", first, 1, 1)
      #audio = sequences.new_sound("audio0", first, 2, 1)
      channel = 3
      frame = video.frame_duration

      setTransforms = ['NONE', 'BLUR_APPEAR', 'APPEAR', 'ZOOM_IN', 'ZOOM_OUT', 'FROM_RIGHT', 'FROM_LEFT', 'FROM_TOP', 'FROM_BOTTOM', 'FROM_TOPRIGHT', 'FROM_TOPLEFT', 'FROM_BOTTOMRIGHT', 'FROM_BOTTOMLEFT']
      setTransforms = ['APPEAR', 'ZOOM_IN', 'ZOOM_OUT']
      setTransforms = ['BLUR_APPEAR']
      setTransforms = ['NONE']

      for i in range(0, len(moviesPath)):
        moviePath = moviesPath[i]
        transform = 'RANDOM' if i >= len(transforms) else transforms[i]

        selTransform = random.choice(setTransforms)

        currentTransitionDuration = transitionDuration
        if selTransform == 'NONE':
          currentTransitionDuration = 0

        previousVideo = video
        #previousAudio = audio

        if selTransform == 'BLUR_APPEAR':
          imgLength = 72
          imgLastFramePath = u'/home/jmramoss/Imágenes/Selección_137.png'
          imgLastFrame = sequences.new_image("imgLastFrame" + str(i + 1), imgLastFramePath, channel, frame_start=frame)
          imgLastFrame.frame_final_duration = imgLength
          channel += 1

          blur = sequences.new_effect("transform_blurImg" + str(i + 1), 'GAUSSIAN_BLUR', channel, frame_start=frame, frame_end=frame + imgLength, seq1=imgLastFrame)
          channel += 1
          blur.blend_type = 'REPLACE'
          blur.size_x = 50.0
          blur.size_y = 50.0

          blur = sequences.new_effect("transform_blur" + str(i + 1), 'GAUSSIAN_BLUR', channel, frame_start=frame - currentTransitionDuration, frame_end=frame + currentTransitionDuration, seq1=previousVideo)
          channel += 1
          blur.blend_type = 'REPLACE'
          blur.size_x = 0.0
          blur.size_y = 0.0
          blur.keyframe_insert(data_path="size_x", frame=frame - currentTransitionDuration)
          blur.keyframe_insert(data_path="size_y", frame=frame - currentTransitionDuration)
          blur.size_x = 50.0
          blur.size_y = 50.0
          blur.keyframe_insert(data_path="size_x", frame=frame)
          blur.keyframe_insert(data_path="size_y", frame=frame)


        video = sequences.new_movie("video" + str(i + 1), moviePath, channel, frame - currentTransitionDuration)
        #audio = sequences.new_sound("audio" + str(i + 1), moviePath, channel + 1, frame - currentTransitionDuration)

        if selTransform != 'NONE':
          transform_strip = sequences.new_effect("transform" + str(i + 1), 'TRANSFORM', channel + 2, frame_start=frame -currentTransitionDuration, frame_end=frame + currentTransitionDuration, seq1=video)
          transform_strip.blend_type = 'ALPHA_OVER'
          transform_strip.translation_unit = 'PIXELS'
          #.scale_start_x
          #.scale_start_y
          #.rotation_start
          #.blend_alpha = 0.0 to 1.0


          transform_strip.translate_start_x = 0.0
          transform_strip.translate_start_y = 0.0
          transform_strip.scale_start_x = 1.0
          transform_strip.scale_start_y = 1.0
          transform_strip.rotation_start = 0.0
          transform_strip.blend_alpha = 1.0

          if selTransform == 'FROM_RIGHT':
            transform_strip.translate_start_x = 1920.0
            transform_strip.translate_start_y = 0.0
          elif selTransform == 'FROM_LEFT':
            transform_strip.translate_start_x = -1920.0
            transform_strip.translate_start_y = 0.0
          elif selTransform == 'FROM_TOP':
            transform_strip.translate_start_x = 0.0
            transform_strip.translate_start_y = -1080.0
          elif selTransform == 'FROM_BOTTOM':
            transform_strip.translate_start_x = 0.0
            transform_strip.translate_start_y = 1080.0
          elif selTransform == 'FROM_TOPRIGHT':
            transform_strip.translate_start_x = 1920.0
            transform_strip.translate_start_y = -1080.0
          elif selTransform == 'FROM_TOPLEFT':
            transform_strip.translate_start_x = -1920.0
            transform_strip.translate_start_y = -1080.0
          elif selTransform == 'FROM_BOTTOMRIGHT':
            transform_strip.translate_start_x = 1920.0
            transform_strip.translate_start_y = 1080.0
          elif selTransform == 'FROM_BOTTOMLEFT':
            transform_strip.translate_start_x = -1920.0
            transform_strip.translate_start_y = 1080.0
          elif selTransform == 'APPEAR':
            transform_strip.blend_alpha = 0.0
          elif selTransform == 'BLUR_APPEAR':
            transform_strip.blend_alpha = 0.0
          elif selTransform == 'ZOOM_IN':
            transform_strip.scale_start_x = 0.0
            transform_strip.scale_start_y = 0.0
            transform_strip.blend_alpha = 0.0
          elif selTransform == 'ZOOM_OUT':
            transform_strip.scale_start_x = 4.0
            transform_strip.scale_start_y = 4.0
            transform_strip.blend_alpha = 0.0
          elif selTransform == 'NONE':
            transform_strip.translate_start_x = 0.0
            transform_strip.translate_start_y = 0.0
            transform_strip.scale_start_x = 1.0
            transform_strip.scale_start_y = 1.0
            transform_strip.rotation_start = 0.0
            transform_strip.blend_alpha = 1.0

          transform_strip.keyframe_insert(data_path="translate_start_x", frame=frame - currentTransitionDuration)
          transform_strip.keyframe_insert(data_path="translate_start_y", frame=frame - currentTransitionDuration)
          transform_strip.keyframe_insert(data_path="scale_start_x", frame=frame - currentTransitionDuration)
          transform_strip.keyframe_insert(data_path="scale_start_y", frame=frame - currentTransitionDuration)
          transform_strip.keyframe_insert(data_path="rotation_start", frame=frame - currentTransitionDuration)
          transform_strip.keyframe_insert(data_path="blend_alpha", frame=frame - currentTransitionDuration)

          transform_strip.translate_start_x = 0.0
          transform_strip.translate_start_y = 0.0
          transform_strip.scale_start_x = 1.0
          transform_strip.scale_start_y = 1.0
          transform_strip.rotation_start = 0.0
          transform_strip.blend_alpha = 1.0
          transform_strip.keyframe_insert(data_path="translate_start_x", frame=frame)
          transform_strip.keyframe_insert(data_path="translate_start_y", frame=frame)
          transform_strip.keyframe_insert(data_path="scale_start_x", frame=frame)
          transform_strip.keyframe_insert(data_path="scale_start_y", frame=frame)
          transform_strip.keyframe_insert(data_path="rotation_start", frame=frame)
          transform_strip.keyframe_insert(data_path="blend_alpha", frame=frame)

        if selTransform != 'NONE':
          channel += 3
          frame +=  video.frame_duration - currentTransitionDuration
        else:
          channel += 2
          frame +=  video.frame_duration

      result = self.saveMovie(frameStart=1, frameEnd=frame, movieOutput=movieOutput)
      #bpy.ops.wm.save_mainfile(filepath="/tmp/mifile3.blend")
      bpy.ops.wm.save_as_mainfile(filepath="/tmp/miefileals3.blend")

    return result






  def fadeOut (self, moviePath, duration=48, movieOutput=None):
    result = None

    if self.blender:
      templatePath = self.getResource('empty.blend', 'templates')
      result = self.runMethodBlender(templatePath, "fadeOut", [moviePath, duration], movieOutput=movieOutput)
    else:
      import bpy
      context = bpy.context
      scene = context.scene
      scene.sequence_editor_create()
      sed = scene.sequence_editor
      sequences = sed.sequences

      #moviePath = "/media/jmramoss/ALMACEN/pypi/slideshow/video2.mp4"
      video1 = sequences.new_movie("video1", moviePath, 1, 1)
      audio1 = sequences.new_sound("audio1", moviePath, 2, 1)

      frameStart = video1.frame_duration-duration+1
      frameEnd = video1.frame_duration+1

      color_strip = sequences.new_effect("color", 'COLOR', 3, frame_start=frameStart, frame_end=frameEnd)
      color_strip.color = (0.000, 0.000, 0.000)
      gamma_cross_strip = sequences.new_effect("color", 'GAMMA_CROSS', 4, frame_start=frameStart, frame_end=frameEnd, seq1=video1, seq2=color_strip)

      result = self.saveMovie(frameStart=1, frameEnd=video1.frame_duration, movieOutput=movieOutput)

    return result









  def rmFile (self, path):
    if os.path.isfile(path):
      os.remove(path)
      #print("File Removed!")

  def createTmpMoviePath (self):
    result = None
    result = tempfile.mkstemp(prefix='.movie', suffix='.mp4')[1]
    return result

  def createTmpFolderPath (self):
    result = None
    result = tempfile.mkdtemp(prefix='.frames', suffix='.png')
    return result

  def addBanner (self, moviePath, title, subtitle = None, title_right = None, subtitle_right = None, framesOffset = 48, color=None, movieOutput=None):
    result = None
    print("generating banner")
    banner = self.generateBanner(title, subtitle, title_right, subtitle_right)
    print("banner = " + banner)
    print("banner generado")
    if framesOffset > 0:
      print("generating offset")
      banner2 = self.addOffset(banner, framesOffset, color)
      print("banner2 = " + banner2)
      print("offset generado")
      #self.rmFile(banner)
      banner = banner2

    print("generating foreground")
    movieFg = self.addForeground(moviePath, "foreground2.mp4", movieOutput=None)
    print("movieFg = " + movieFg)
    print("foreground generado")

    print("adding banner")
    result = self.doAddBanner(movieFg, banner, movieOutput=None)
    print("result = " + result)
    print("banner added")

    print("adding music")
    result = self.doAddMusic(result, moviePath, movieOutput)
    print("result = " + result)
    print("music added")


    return result

  def saveFrames (self, frameStart=1, frameEnd=250, folderOutput=None, resolution_x = 1920, resolution_y = 1080):
    result = None

    if self.runMode == 'DEBUG':
      frameEnd = min(self.maxDebugFrames, frameEnd)

    #frame_end = bpy.context.scene.node_tree.nodes['video'].clip.frame_duration

    import bpy
    context = bpy.context
    scene = context.scene

    scene.frame_start = frameStart
    scene.frame_end = frameEnd
    scene.frame_step = 1
    scene.render.fps = self.fps

    if resolution_x is None or resolution_y is None:
      resolution_x = 1920
      resolution_y = 1080

    if self.runMode == 'DEBUG':
      resolution_x = resolution_x / 10
      resolution_y = resolution_y / 10
    elif self.runMode == 'DRAFT':
      resolution_x = resolution_x / 5
      resolution_y = resolution_y / 5
    elif self.runMode == 'LOW':
      resolution_x = resolution_x
      resolution_y = resolution_y
    elif self.runMode == 'PRODUCTION':
      resolution_x = resolution_x
      resolution_y = resolution_y
    elif self.runMode == 'SUPER-PRODUCTION':
      resolution_x = resolution_x
      resolution_y = resolution_y

    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100#100

    #Type: enum in [‘BMP’, ‘IRIS’, ‘PNG’, ‘JPEG’, ‘JPEG2000’, ‘TARGA’, ‘TARGA_RAW’, ‘CINEON’, ‘DPX’, ‘OPEN_EXR_MULTILAYER’, ‘OPEN_EXR’, ‘HDR’, ‘TIFF’, ‘AVI_JPEG’, ‘AVI_RAW’, ‘FRAMESERVER’, ‘H264’, ‘FFMPEG’, ‘THEORA’, ‘XVID’], default ‘TARGA’
    scene.render.image_settings.file_format = 'PNG'

    result = self.createTmpFolderPath() if folderOutput is None else folderOutput

    scene.render.filepath = result
    bpy.ops.render.render(animation=True)

    return result

  def saveOneFrame (self, frameNum):
    scene = bpy.data.scenes["Scene"]
    scene.frame_current=frameNum
    bpy.ops.render.render(write_still=True)

  def saveMovie (self, frameStart=1, frameEnd=250, movieOutput=None, resolution_x = 1920, resolution_y = 1080):
    result = None

    if self.runMode == 'DEBUG' and not self.forceFullRender:
      frameEnd = min(self.maxDebugFrames, frameEnd)

    if self.forceFrameEnd is not None:
      frameEnd = min(self.forceFrameEnd, frameEnd)

    #frame_end = bpy.context.scene.node_tree.nodes['video'].clip.frame_duration

    import bpy
    context = bpy.context
    scene = context.scene

    scene.frame_start = frameStart
    scene.frame_end = frameEnd
    scene.frame_step = self.frame_step
    scene.render.fps = self.fps

    if resolution_x is None or resolution_y is None:
      resolution_x = 1920
      resolution_y = 1080

    if self.runMode == 'DEBUG':
      resolution_x = resolution_x / 10
      resolution_y = resolution_y / 10
    elif self.runMode == 'DRAFT2':
      resolution_x = resolution_x / 10
      resolution_y = resolution_y / 10
    elif self.runMode == 'DRAFT':
      resolution_x = resolution_x / 5
      resolution_y = resolution_y / 5
    elif self.runMode == 'DRAFT3':
      resolution_x = resolution_x / 5
      resolution_y = resolution_y / 5
    elif self.runMode == 'LOW':
      resolution_x = resolution_x
      resolution_y = resolution_y
    elif self.runMode == 'PRODUCTION':
      resolution_x = resolution_x
      resolution_y = resolution_y
    elif self.runMode == 'SUPER-PRODUCTION':
      resolution_x = resolution_x
      resolution_y = resolution_y

    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100#100

    #Type: enum in [‘BMP’, ‘IRIS’, ‘PNG’, ‘JPEG’, ‘JPEG2000’, ‘TARGA’, ‘TARGA_RAW’, ‘CINEON’, ‘DPX’, ‘OPEN_EXR_MULTILAYER’, ‘OPEN_EXR’, ‘HDR’, ‘TIFF’, ‘AVI_JPEG’, ‘AVI_RAW’, ‘FRAMESERVER’, ‘H264’, ‘FFMPEG’, ‘THEORA’, ‘XVID’], default ‘TARGA’
    scene.render.image_settings.file_format = 'FFMPEG'

    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'

    rateFactor = 'LOSSLESS'
    preset = 'VERYSLOW'
    if self.runMode == 'DEBUG':
      rateFactor = 'LOWEST'
      preset = 'ULTRAFAST'
    elif self.runMode == 'DRAFT2':
      rateFactor = 'LOWEST'
      preset = 'ULTRAFAST'
    elif self.runMode == 'DRAFT':
      rateFactor = 'MEDIUM'
      preset = 'MEDIUM'
    elif self.runMode == 'DRAFT3':
      rateFactor = 'LOW'
      preset = 'MEDIUM'
    elif self.runMode == 'LOW':
      rateFactor = 'LOW'
      preset = 'MEDIUM'
    elif self.runMode == 'PRODUCTION':
      rateFactor = 'MEDIUM'
      preset = 'MEDIUM'
    elif self.runMode == 'SUPER-PRODUCTION':
      rateFactor = 'LOSSLESS'
      preset = 'VERYSLOW'

    #constant_rate_factor = 'LOWEST', 'MEDIUM', 'HIGH', 'PERC_LOSSLESS', 'LOSSLESS'
    scene.render.ffmpeg.constant_rate_factor = rateFactor

    #ffmpeg_preset = 'ULTRAFAST', 'MEDIUM', 'VERYSLOW'
    scene.render.ffmpeg.ffmpeg_preset = preset

    #audio_codec #FFmpeg audio codec to use
    #Type:	enum in [‘NONE’, ‘MP2’, ‘MP3’, ‘AC3’, ‘AAC’, ‘VORBIS’, ‘FLAC’, ‘PCM’], default ‘NONE’
    scene.render.image_settings.color_mode = 'RGB'

    scene.render.ffmpeg.audio_codec = 'MP3'
    scene.render.ffmpeg.audio_bitrate = 192

    result = self.createTmpMoviePath() if movieOutput is None else movieOutput

    srcTmpDir = os.path.dirname(result)
    tmpDir = tempfile.mkdtemp(prefix=".tmp", dir=srcTmpDir)
    #tmpRender = os.path.join(tmpDir, 'movie')
    #print("TEMP RENDER = " + tmpRender)

    scene.render.filepath = os.path.join(tmpDir, 'movie')
    bpy.ops.render.render(animation=True)

    onlyfiles = [os.path.join(tmpDir, f) for f in os.listdir(tmpDir) if os.path.isfile(os.path.join(tmpDir, f))]
    if onlyfiles is not None and len(onlyfiles) == 1:
      #print("onlyfiles = " + str(onlyfiles[0]))
      #print("exit")
      #quit()
      #print("result = " + result)
      os.rename(onlyfiles[0], result)
      os.rmdir(tmpDir)
    else:
      result = None

    if (self.verbose or self.runMode == 'DEBUG' or self.runMode == 'DRAFT2' or self.runMode == 'DRAFT' or self.runMode == 'DRAFT3') and result is not None:
      outBlend = result + '.blend'
      bpy.ops.wm.save_as_mainfile(filepath=outBlend)

    return result

#tools = BlenderTools()
#tools.installBlender()
#print(tools.checkInstallBlender())

if True and __name__ == '__main__':
  tools = BlenderTools()
  tools.verbose = True
  tools.runMode = 'PRODUCTION'
  print(str(tools.generateTitle(title='1º de primaria', subtitle = u'CEIP Esteban Navarro Sánchez - Tutora: Maite Martínez Santana', title_right='Curso 2017-2018', subtitle_right = 'Esteban Navarro', movieOutput=None)))
  '''

  movies = [
    '/home/jmramoss/Descargas/cars.mkv',
    '/home/jmramoss/Descargas/flag.mkv',
    '/home/jmramoss/Descargas/cars.mkv',
    '/home/jmramoss/Descargas/flag.mkv'
  ]
  transforms = ['RANDOM']
  print(str(tools.mergeWithTransform(moviesPath=movies, transforms=transforms)))
  '''
  #moviePath = "/home/jmramoss/hd/res_slideshow/project/year1.mp4"
  #musicData = [
  #  {'path': '/home/jmramoss/hd/res_slideshow/project/year1/music/Cleric_-_Loveliness.mp3'},
  #  {'path': '/home/jmramoss/hd/res_slideshow/project/year1/music/The_Green_Duck_-_Blow_It_Away.mp3'},
  #  {'path': '/home/jmramoss/hd/res_slideshow/project/year1/music/RogerThat_-_Epic_Cinematic_Rock.mp3'}
  #]
  #print(str(tools.doAddBackgroundMusic(moviePath, musicData)))
  #print(str(tools.getDistanceColor ((100, 100, 100), (100, 100, 100))))
  #print(str(tools.getDistanceColor ((100, 100, 100), (111, 111, 111))))
  #print(str(tools.getDistanceColor ((100, 100, 100), (151, 151, 151))))
  #print(str(tools.getDistanceColor ((100, 100, 100), (151, 151, 251))))
  #print(str(tools.getDistanceColor ((100, 100, 100), (100, 151, 151))))
  #print(str(tools.getDistanceColor ((0, 0, 0), (255, 255, 255))))
  #tools.__a__()
  #print(str(tools.splitGs('/media/jmramoss/TOSHIBA EXT13/res_slideshow/transits/t', moviePath='/home/jmramoss/Descargas/transitions.mp4')))
  #print(str(tools.checkImgGreenScreen ('/media/jmramoss/TOSHIBA EXT13/res_slideshow/transits/t/1317.png', (0, 214, 0))))
  #print(str(tools.checkImgGreenScreen ('/media/jmramoss/TOSHIBA EXT13/res_slideshow/transits/t/1318.png', (0, 214, 0))))
  #print(str(tools.checkImgGreenScreen ('/media/jmramoss/TOSHIBA EXT13/res_slideshow/transits/t/1319.png', (0, 214, 0))))
  #print(str(tools.checkImgGreenScreen ('/media/jmramoss/TOSHIBA EXT13/res_slideshow/transits/t/1320.png', (0, 214, 0))))
  #print(str(tools.checkImgGreenScreen ('/media/jmramoss/TOSHIBA EXT13/res_slideshow/transits/t/1321.png', (0, 214, 0))))
  #tools.runMode = 'DRAFT'
  #res = tools.addForeground("/media/jmramoss/ALMACEN/pypi/slideshow/video3.mp4", "/media/jmramoss/ALMACEN/pypi/slideshow/foreground2.mp4", movieOutput=None)
  #res = tools.addForeground("/media/jmramoss/ALMACEN/pypi/slideshow/video3.mp4", "/media/jmramoss/ALMACEN/pypi/slideshow/foreground2.mp4", "/media/jmramoss/ALMACEN/pypi/slideshow/fg444.mp4")
  #print("res = " + res)
  #tools.split('/media/jmramoss/ALMACEN/pypi/slideshow/transitions.mp4', 150, 500, movieOutput='/media/jmramoss/ALMACEN/pypi/slideshow/transitions_split.mp4')

  #tools.scale('/home/jmramoss/Descargas/Pexels Videos 1110140.mp4', width = 1920, height = 1080, movieOutput='/home/jmramoss/Descargas/modPexels Videos 1110140.mp4')
  #print(str(tools.frames('/home/jmramoss/Descargas/Pexels Videos 1110140.mp4', frameStart=1, frameEnd=10, folderOutput='/home/jmramoss/Descargas')))
  #print(str(tools.frames('/home/jmramoss/Descargas/Pexels Videos 1110140.mp4', frameStart=1, frameEnd=10)))
  #tools.__downloadBlenderPip__()
  #tools.__installBlenderPip__()
  #tools.__installBlenderBslideshow__()

  #banner = tools.generateBanner("ESTO<<< FUNCIONA?", "PROBAaddcNDO", "Swwí", "Nbbbo", "/media/jmramoss/ALMACEN/pypi/slideshow/genBanner45.mp4")
  #print("banner = " + banner)
  #tools.runOffset ("/media/jmramoss/ALMACEN/pypi/slideshow/test1.mkv", framesOffset = 48, color=None, movieOutput="/media/jmramoss/ALMACEN/pypi/slideshow/offset_test1.mp4")
  #tools.doAddBanner("/media/jmramoss/ALMACEN/pypi/slideshow/video3.mp4", "/media/jmramoss/ALMACEN/pypi/slideshow/offset_test1.mkv", movieOutput="/media/jmramoss/ALMACEN/pypi/slideshow/video3_with_banner222.mp4")
  #tools.addBanner("/media/jmramoss/ALMACEN/pypi/slideshow/Background.mp4", "Bosque", "con niebla", "Forest", "with fog", framesOffset = 48, color=None, movieOutput="/media/jmramoss/ALMACEN/pypi/slideshow/video3_modificado56.mp4")
  #tools.blender = False
  #tools.addBanner("/media/jmramoss/ALMACEN/pypi/slideshow/long_video_audio.mp4", "Bosque", "con niebla", "nnnnnnnn", "joy con", framesOffset = 48, color=None, movieOutput="/media/jmramoss/ALMACEN/pypi/slideshow/long_modificado6.mp4")
  #tools.doAddTransition("/media/jmramoss/ALMACEN/pypi/slideshow/video1.mp4", "/media/jmramoss/ALMACEN/pypi/slideshow/video3.mp4", movieOutput="/media/jmramoss/ALMACEN/pypi/slideshow/traaaaa10.mp4")



  #print("banner generado " + str(banner))
  '''
  print("arguments#### (start)")
  print(str(sys.argv))
  print("arguments#### (end)")
  if sys.argv is not None and len(sys.argv) > 0 and sys.argv[0].endswith("blender"):
    import bpy
    addBanner()
    saveMovie()
  else:
    #subprocess.call(["ls", "-l"])
    subprocess.call(["/media/jmramoss/ALMACEN/slideshow/blender-2.79b-linux-glibc219-x86_64/blender", "/media/jmramoss/ALMACEN/pypi/slideshow/banner_overlap2.blend", "--background", "--python", "/media/jmramoss/ALMACEN/pypi/slideshow/add_banner.py"])

  '''
