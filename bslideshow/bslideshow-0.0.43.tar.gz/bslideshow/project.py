#!/usr/bin/env python2.7
#coding:utf-8


#import bpy
import os
import shutil

import math
import random
from PIL import Image
import time

import codecs
import hjson

from bslideshow.director import Director
from bslideshow.slideshow import Slideshow
from bslideshow.tools import BlenderTools

class Project(object):

  def __init__ (self, path):
    cwd = os.getcwd()
    if path is not None and not os.path.isabs(path):
      path = os.path.join(cwd, path)
    self.path = path
    self.renderMode = 'DRAFT2'
    #self.renderMode = 'LOW'
    self.verbose = True
    self.parents = []
    self.force = False

  def generateMainSection (self, section):
    print("generate Main Section " + section['title'])
    sectTitle = self.generateTitleSection(section, mode='section')
    outSections = list()
    for simpleSection in section['sections']:
      self.parents.append([simpleSection, section])
      outSection = self.generateSection(simpleSection)
      outSections.append(outSection)
    sectContent = self.mergeWithTransitions(section, outSections)
    print("sectContent = " + str(sectContent))

    tools = self.__newBlenderTools()

    '''
    print("sectTitle = " + sectTitle)
    sectionTitleFadeIn = os.path.join(os.path.dirname(self.path), section['path'] + "_title_fadeIn" + ".mp4")
    if self.force or not os.path.isfile(sectionTitleFadeIn):
      tools.fadeIn(moviePath=str(sectTitle), duration=48, movieOutput=str(sectionTitleFadeIn))
    print("sectionTitleFadeIn = " + sectionTitleFadeIn)
    sectionTitleFadeOut = os.path.join(os.path.dirname(self.path), section['path'] + "_title_fadeOut" + ".mp4")
    if self.force or not os.path.isfile(sectionTitleFadeOut):
      tools.fadeOut(moviePath=str(sectionTitleFadeIn), duration=48, movieOutput=str(sectionTitleFadeOut))
    print("sectionTitleFadeOut = " + sectionTitleFadeOut)
    '''

    sectionContentFadeIn = os.path.join(os.path.dirname(self.path), section['path'] + "_fadeIn" + ".mp4")
    if self.force or not os.path.isfile(sectionContentFadeIn):
      tools.fadeIn(moviePath=str(sectContent), duration=48, movieOutput=str(sectionContentFadeIn))
    print("sectionContentFadeIn = " + sectionContentFadeIn)
    sectionContentFadeOut = os.path.join(os.path.dirname(self.path), section['path'] + "_fadeOut" + ".mp4")
    if self.force or not os.path.isfile(sectionContentFadeOut):
      tools.fadeOut(moviePath=str(sectionContentFadeIn), duration=48, movieOutput=str(sectionContentFadeOut))
    print("sectionContentFadeOut = " + sectionContentFadeOut)

    if True and 'music_background' in section:
      sectionMainWithMusic = os.path.join(os.path.dirname(self.path), section['path'] + "-music" + ".mp4")
      if self.force or not os.path.isfile(sectionMainWithMusic):
        tools.runMode = self.renderMode
        tools.verbose = self.verbose
        #musicData = section['music_background']
        musicData = self.loadMusic(section['music_background'])

        tools.doAddBackgroundMusic(str(sectionContentFadeOut), musicData, lenFadeIn=3*24, lenFadeOut=3*24, movieOutput=str(sectionMainWithMusic))

      result = sectionMainWithMusic
      sectionContentFadeOut = sectionMainWithMusic


    sectionMain = os.path.join(os.path.dirname(self.path), section['path'] + "" + ".mp4")
    if self.force or not os.path.isfile(sectionMain):
      #tools.merge(movie1Path=str(sectionTitleFadeOut), movie2Path=str(sectionContentFadeOut), movieOutput=str(sectionMain))
      tools.merge(movie1Path=str(sectTitle), movie2Path=str(sectionContentFadeOut), movieOutput=str(sectionMain))

    result = sectionMain
    print("mainSection = " + sectionMain)

    if False and 'music_background' in section:
      sectionMainWithMusic = os.path.join(os.path.dirname(self.path), section['path'] + "-music" + ".mp4")
      if self.force or not os.path.isfile(sectionMainWithMusic):
        tools.runMode = self.renderMode
        tools.verbose = self.verbose
        musicData = section['music_background']
        tools.doAddBackgroundMusic(str(sectionMain), musicData, movieOutput=str(sectionMainWithMusic))
      result = sectionMainWithMusic

    return result

  def generateTitleSlideshow (self, section, mode='project'):
    result = None

    pathFolderTitle = self.selectTitleFolder(section)
    print("pathFolderTitle = " + pathFolderTitle)

    durationPhoto = 5 * 24
    numPhotos = 5
    if mode == 'project':
      durationPhoto = 200
      numPhotos = 3
    elif mode == 'section':
      durationPhoto = 5 * 24
      numPhotos = 5

    parts = list()
    for i in range(0, numPhotos):
      director = Director()
      director.runMode = self.renderMode
      director.verbose = self.verbose
      director.frame_step = 1
      part = None
      if mode == 'project':
        part = director.animSceneTitleItem(str(pathFolderTitle), durationFrames=durationPhoto, mode=mode)
      elif mode == 'section':
        part = director.animSceneTitleItem(str(pathFolderTitle), durationFrames=durationPhoto, mode=mode)
      else:
        part = director.animSceneTitleItem(str(pathFolderTitle), durationFrames=durationPhoto, mode=mode)

      parts.append(part)

    transforms = list()
    for i in range(0, numPhotos-1):
      transforms.append("RANDOM")

    sectionTitle = os.path.join(os.path.dirname(self.path), section['path'] + "_title.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title.mp4")
    tools = self.__newBlenderTools()
    tools.mergeWithTransform(moviesPath=parts, transforms=transforms, transitionDuration = 24, movieOutput=str(sectionTitle))
    result = sectionTitle

    if False and 'music_title' in section:
      sectionTitleWithMusic = os.path.join(os.path.dirname(self.path), section['path'] + "_title-music.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title-music.mp4")
      if self.force or not os.path.isfile(sectionTitleWithMusic):
        tools = self.__newBlenderTools()
        musicData = [section['music_title']]
        tools.doAddBackgroundMusic(str(sectionTitle), musicData, movieOutput=str(sectionTitleWithMusic))
      result = sectionTitleWithMusic


    return result

  #/home/jmramoss/hd/res_slideshow/bslideshow/titles/music_for_titles.hjson
  def loadMusicById (self, musicId):
    result = None

    pathLib = '/home/jmramoss/hd/res_slideshow/bslideshow/titles/music.hjson'
    dataMusic = self.__loadObj__ (pathLib)
    '''
    {
      id: acoustic-folk
      music: acoustic-folk
      start: "0:58"
      end: "1:23"
    }
    '''
    listMusic = dataMusic['fragments']
    result = None
    for item in listMusic:
      if item['id'] == musicId:
        result = item
        break
    fid = result['music']
    listMusic = dataMusic['music']
    for item in listMusic:
      if item['id'] == fid:
        result['path'] = item['path']
        break
    #result['path'] = os.path.join(os.path.dirname(pathLib), result['music'] + '.mp3')
    print("music by id = " + str(result))
    return result

  #/home/jmramoss/hd/res_slideshow/bslideshow/titles/music_for_titles.hjson
  def loadMusic (self, musicData):
    result = list()
    print("################3 musicData = " + str(musicData))
    #print("################3 musicData type = " + str(type(musicData)))
    if type(musicData) is dict:
      if 'id' in musicData:
        toAdd = self.loadMusicById(musicData['id'])
        toAdd.update(musicData)
        result.append(toAdd)
      else:
        result.append(musicData)
    elif type(musicData) is str or type(musicData) is unicode:
      result.append(self.loadMusicById(musicData))
    elif type(musicData) is list:
      for item in musicData:
        print("item music =" + str(item))
        if type(item) is dict:
          if 'id' in item:
            toAdd = self.loadMusicById(item['id'])
            toAdd.update(item)
            result.append(toAdd)
          else:
            result.append(item)
        elif type(item) is str or type(item) is unicode:
          result.append(self.loadMusicById(item))
    print("musicData = " + str(result))
    return result


  def generateTitleSection (self, section, mode='project'):
    result = None

    print("generate Title Section " + section['title'])

    sectionTitle = os.path.join(os.path.dirname(self.path), section['path'] + "_title.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title.mp4")
    result = sectionTitle
    print("sectionTitle generate Title Section " + sectionTitle)
    if self.force or not os.path.isfile(sectionTitle):

      sectionTitle = self.generateTitleSlideshow(section, mode=mode)
      #sectionTitle = '/home/jmramoss/hd/res_slideshow/project/year1_title.mp4'
      print("sectionTitle base = " + sectionTitle)

      foregroundPath = 'overlay22.mp4'
      tools = self.__newBlenderTools()
      tools.frame_step = 1

      sectionTitleForeground = os.path.join(os.path.dirname(self.path), section['path'] + "_title_foreground.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title_foreground.mp4")
      if self.force or not os.path.isfile(sectionTitleForeground):
        tools.addForeground(str(sectionTitle), foregroundPath, movieOutput=str(sectionTitleForeground))
        sectionTitle = sectionTitleForeground

      tools = self.__newBlenderTools()

      movTitle = tools.generateTitle (title=section['title'], subtitle = section['subtitle'], title_right=section['title_right'] if 'title_right' in section else '', subtitle_right = section['subtitle_right'] if 'subtitle_right' in section else '')
      #movTitle = '/tmp/.movieLxoiqx.mp4'
      print("movTitle = " + movTitle)


      tools = self.__newBlenderTools()
      infoPre = tools.getInfo(sectionTitle)
      tools = self.__newBlenderTools()
      infoTitle = tools.getInfo(movTitle)
      print("infoPre['frames'] = " + str(infoPre['frames']))
      print("infoTitle['frames'] = " + str(infoTitle['frames']))
      offset = infoPre['frames'] - infoTitle['frames']
      print("offset = " + str(offset))

      sectionTitleBlur = os.path.join(os.path.dirname(self.path), section['path'] + "_title_blur.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title_blur.mp4")
      tools.applyBlur(moviePath=sectionTitle, offset=offset, sizeBlur=7.5, movieOutput=sectionTitleBlur)

      #tools = self.__newBlenderTools()
      #offsetMov = tools.addOffset(moviePath=movTitle, framesOffset = offset)
      #print("offsetMov = " + offsetMov)
      tools = self.__newBlenderTools()
      #sectionTitle = tools.doAddBanner(moviePath=sectionTitle, bannerPath=offsetMov)
      sectionTitle = tools.doAddGreenScreen (moviePath=sectionTitleBlur, bannerPath=movTitle, offset=offset)
      print("sectionTitle with title = " + sectionTitle)

      sectionTitleBlurFadeIn = os.path.join(os.path.dirname(self.path), section['path'] + "_title_blur_fade_in.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title_blur_fade_in.mp4")
      tools.fadeIn(moviePath=sectionTitle, duration=3*24, movieOutput=sectionTitleBlurFadeIn)

      sectionTitleBlurFadeOut = os.path.join(os.path.dirname(self.path), section['path'] + "_title_blur_fade_out.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title_blur_fade_out.mp4")
      tools.fadeOut(moviePath=sectionTitleBlurFadeIn, duration=3*24, movieOutput=sectionTitleBlurFadeOut)
      sectionTitle = sectionTitleBlurFadeOut
      result = sectionTitle



    if True and 'music_title' in section:
      sectionTitleWithMusic = os.path.join(os.path.dirname(self.path), section['path'] + "_title-music.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title-music.mp4")
      if self.force or not os.path.isfile(sectionTitleWithMusic):
        tools = self.__newBlenderTools()

        #musicData = [section['music_title']]
        musicData = self.loadMusic(section['music_title'])
        print(">>>>>>>>>>> musicData = " + str(musicData))
        tools.doAddBackgroundMusic(str(sectionTitle), musicData, lenFadeIn=3*24, lenFadeOut=3*24, movieOutput=str(sectionTitleWithMusic))
      result = sectionTitleWithMusic

      '''
      sectionTitleMusicFadeIn = os.path.join(os.path.dirname(self.path), section['path'] + "_title_music_fade_in.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title_music_fade_in.mp4")
      tools.musicFadeIn(moviePath=sectionTitleWithMusic, duration=3*24, movieOutput=sectionTitleMusicFadeIn)

      sectionTitleMusicFadeOut = os.path.join(os.path.dirname(self.path), section['path'] + "_title_music_fade_out.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title_music_fade_out.mp4")
      tools.musicFadeOut(moviePath=sectionTitleMusicFadeIn, duration=3*24, movieOutput=sectionTitleMusicFadeOut)
      result = sectionTitleMusicFadeOut
      '''

    return result


  def generateTitleSectionOld (self, section):
    result = None

    print("generate Title Section " + section['title'])

    sectionTitle = os.path.join(os.path.dirname(self.path), section['path'] + "_title.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title.mp4")
    print("sectionTitle generate Title Section " + sectionTitle)
    if self.force or not os.path.isfile(sectionTitle):
      director = Director()
      director.runMode = self.renderMode
      director.verbose = self.verbose
      #director.maxDebugFrames = 9999999
      director.frame_step = 1
      pathFolderTitle = self.selectTitleFolder(section)
      print("pathFolderTitle = " + pathFolderTitle)
      director.animSceneTitle(str(pathFolderTitle), movieOutput=str(sectionTitle))
      print("out section = " + sectionTitle)
    result = sectionTitle


    if True and 'music_title' in section:
      sectionTitleWithMusic = os.path.join(os.path.dirname(self.path), section['path'] + "_title-music.mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), "title-music.mp4")
      if self.force or not os.path.isfile(sectionTitleWithMusic):
        tools = self.__newBlenderTools()
        musicData = [section['music_title']]
        tools.doAddBackgroundMusic(str(sectionTitle), musicData, movieOutput=str(sectionTitleWithMusic))
      result = sectionTitleWithMusic



    return result

  def selectTitleFolder (self, section, size=16):
    result = None

    sectionPath = section['path'] if 'path' in section else self.path
    sections = section['sections'] if 'path' in section else self.loadAllSubsections(section)

    result = os.path.join(os.path.dirname(self.path), sectionPath + "_title_folder") if 'path' in section else os.path.join(os.path.dirname(self.path), "title_folder")
    if self.force or not os.path.isdir(result):
      if not os.path.isdir(result):
        os.mkdir(result)

      for i in range(size):
        subsection = random.choice(sections)
        folderSubsection = os.path.join(os.path.dirname(self.path), subsection['path'])
        imagesSubsection = [os.path.join(folderSubsection, f) for f in os.listdir(folderSubsection) if (f.lower().endswith('.jpg') or f.lower().endswith('.png')) and os.path.isfile(os.path.join(folderSubsection, f))]
        selectedImg = random.choice(imagesSubsection)
        filename, fextension = os.path.splitext(os.path.basename(selectedImg))
        shutil.copyfile(selectedImg, os.path.join(result, filename + '_' + str(i) + fextension))

    return result

  def loadAllSubsections (self, section):
    result = list()
    for item in section['sections']:
      result.extend(item['sections'])
    return result

  def mergeWithTransitions (self, section, sections=None):
    result = None
    print("mergeWithTransitions " + section['title'])

    pathSection = os.path.join(os.path.dirname(self.path), section['path'] + "_transitions" + ".mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), os.path.splitext(os.path.basename(self.path))[0] + "_transitions" + ".mp4")

    tools = self.__newBlenderTools()
    tools.frame_step = 1

    if self.force or not os.path.isfile(pathSection):
      transitions = ['transition41.mp4', 'transition45.mp4', 'transition48.mp4', 'transition80.mp4', 'transition90.mp4']
      for item in sections:
        if result is None:
          result = pathSection
          shutil.copyfile(item, pathSection)
        else:
          tools.doAddTransition(movie1Path=str(pathSection), movie2Path=str(item), transitionPath=str(random.choice(transitions)), movieOutput=str(pathSection))

    result = pathSection

    return result


  def mergeWithBlanks (self, section, sections=None):
    result = None
    print("mergeWithBlanks " + section['title'])

    pathSection = os.path.join(os.path.dirname(self.path), section['path'] + "_blanks" + ".mp4") if 'path' in section else os.path.join(os.path.dirname(self.path), os.path.splitext(os.path.basename(self.path))[0] + "_blanks" + ".mp4")
    print("pathSection blanks = " + str(pathSection))

    tools = self.__newBlenderTools()

    if self.force or not os.path.isfile(pathSection):
      print("NO EXISTE")
      movies = list()
      movies.append(sections[0])
      if len(sections) > 0:
        blankPath = tools.getResource('blank5s.mp4', 'transitions')
        for i in range(1, len(sections)):
          movies.append(blankPath)
          movies.append(sections[i])
      tools.mergeMultiples(movies, movieOutput=pathSection)
    result = pathSection

    return result





  def generateSection (self, section):
    result = None

    print("generate Section " + section['title'])
    director = Director()
    director.runMode = self.renderMode
    director.verbose = self.verbose
    #director.maxDebugFrames = 9999999
    director.frame_step = 1
    pathSection = os.path.join(os.path.dirname(self.path), section['path'])

    sectionBase = os.path.join(os.path.dirname(self.path), section['path'] + "_base" + ".mp4")
    print("path section = " + pathSection)
    if self.force or not os.path.isfile(sectionBase):
      #director.animScene(str(pathSection), movieOutput=str(sectionBase))
      #director.animSceneDuration(str(pathSection), movieOutput=str(sectionBase))
      director.animSlideshow(str(pathSection), time=(section['time'] if 'time' in section else None), movieOutput=str(sectionBase))
    print("out section = " + sectionBase)

    foregroundPath = 'overlay22.mp4'
    tools = self.__newBlenderTools()
    #tools.maxDebugFrames = 99
    tools.frame_step = 1
    #tools.maxDebugFrames = 24

    sectionForeground = os.path.join(os.path.dirname(self.path), section['path'] + "_foreground" + ".mp4")
    if self.force or not os.path.isfile(sectionForeground):
      tools.addForeground(str(sectionBase), foregroundPath, movieOutput=str(sectionForeground))
    print("out2 section = " + sectionForeground)


    #tools.maxDebugFrames = 24
    sectionBanner = os.path.join(os.path.dirname(self.path), section['path'] + "_banner" + ".mp4")
    if self.force or not os.path.isfile(sectionBanner):
      print("generating banner")
      print("type title = " + str(type(section['title'])))
      tools.generateBanner(title = section['title'], subtitle = section['subtitle'], movieOutput=str(sectionBanner))
    print("banner section = " + sectionBanner)

    sectionBannerOffset = os.path.join(os.path.dirname(self.path), section['path'] + "_bannerOffset" + ".mp4")
    if self.force or not os.path.isfile(sectionBannerOffset):
      tools.addOffset(str(sectionBanner), framesOffset = 48, movieOutput=str(sectionBannerOffset))
    #bannerOffset = '/tmp/.movieRWAuLJ.mp4'
    print("bannerOffset section = " + sectionBannerOffset)


    sectionResult = os.path.join(os.path.dirname(self.path), section['path'] + "" + ".mp4")
    if self.force or not os.path.isfile(sectionResult):
      tools.doAddBanner(str(sectionForeground), str(sectionBannerOffset), movieOutput=str(sectionResult))
    print("result section = " + sectionResult)

    result = sectionResult
    return result

  def __saveObj__ (self, path, obj):
    fp = codecs.open(path, mode='w', encoding='utf-8')
    hjson.dump(obj, fp)

  def __loadObj__ (self, path):
    result = None
    fp = codecs.open(path, mode='r', encoding='utf-8')
    result = hjson.load(fp)
    return result

  def __get_parent__ (self, data):
    result = None
    for item in self.parents:
      if data == item[0]:
        result = item[1]
        break
    return result

  def __newBlenderTools (self):
    result = None
    result = BlenderTools()
    result.runMode = self.renderMode
    result.verbose = self.verbose
    return result

  def generate (self):
    result = None
    data = self.__loadObj__(self.path)
    self.parents.append([data, None])
    mainTitle = self.generateTitleSection(data, mode='project')
    outSections = list()
    for mainSection in data['sections']:
      self.parents.append([mainSection, data])
      outSection = os.path.join(os.path.dirname(self.path), mainSection['path'] + "" + ".mp4")
      if self.force or not os.path.isfile(outSection):
        outSection = self.generateMainSection(mainSection)
      outSections.append(outSection)
    #mainContent = self.mergeWithTransitions(data, outSections)
    mainContent = self.mergeWithBlanks(data, outSections)

    movFinal = os.path.join(os.path.dirname(self.path), os.path.basename(self.path) + "" + ".mp4")
    if self.force or not os.path.isfile(movFinal):
      tools = self.__newBlenderTools()
      tools.merge(movie1Path=str(mainTitle), movie2Path=str(mainContent), movieOutput=str(movFinal))
    result = movFinal

    return result





if __name__ == '__main__':
  p = Project("/media/jmramoss/TOSHIBA EXT13/res_slideshow/video_primaria12/project.hjson")
  #p.force = True
  p.renderMode = 'PRODUCTION'
  p.renderMode = 'DRAFT2'
  #Green screen https://www.youtube.com/watch?v=jw8a_9OfVN8
  #p.generate()
  #tools = BlenderTools()
  #tools.runMode = 'LOW'
  #tools.split(moviePath='/home/jmramoss/hd/res_slideshow/project/test.mp4', frameStart=1, frameEnd=4*96, movieOutput='/home/jmramoss/hd/res_slideshow/project/test_split.mp4')
  #tools.fadeIn(moviePath='/home/jmramoss/hd/res_slideshow/project/test_split.mp4', duration=96, movieOutput='/home/jmramoss/hd/res_slideshow/project/test_fadeIn2.mp4')
  #tools.fadeOut(moviePath='/home/jmramoss/hd/res_slideshow/project/test_fadeIn2.mp4', duration=96, movieOutput='/home/jmramoss/hd/res_slideshow/project/test_fadeOut2.mp4')
  #tools.merge(movie1Path='/home/jmramoss/hd/res_slideshow/project/test_fadeIn2.mp4', movie2Path='/home/jmramoss/hd/res_slideshow/project/test_fadeOut2.mp4', movieOutput='/home/jmramoss/hd/res_slideshow/project/test_merge.mp4')
  #p.mergeWithTransitions(None, ["/tmp/.movie8p71ol.mp4", "/tmp/.moviehkqFpL.mp4", "/tmp/.movie5H4coh.mp4"])
  #p.generateTitleSection(p.sections[0])
  data = p.__loadObj__(p.path)
  #print(str(data))
  #print(str(p.generateTitleSlideshow(data['sections'][0])))
  #print(str(p.generateTitleSection(data['sections'][0])))
  #print(str(p.generateSection(data['sections'][0]['sections'][0])))
  #print(str(p.generateMainSection(data['sections'][0])))

  tools = BlenderTools()
  tools.verbose = True
  tools.runMode = 'LOW'
  #tools.applyBlur(moviePath='/home/jmramoss/hd/res_slideshow/project/year1_title.mp4', offset=(15*24), movieOutput='/home/jmramoss/hd/res_slideshow/project/year1_title_blur.mp4')

  section = data['sections'][0]['sections'][1]
  #section = data['sections'][0]
  #print(str(tools.generateTitle (title=section['title'], subtitle = section['subtitle'], title_right=section['title_right'] if 'title_right' in section else '', subtitle_right = section['subtitle_right'] if 'subtitle_right' in section else '')))
  #print(str(p.mergeWithBlanks(data, sections=['/home/jmramoss/hd/res_slideshow/video_primaria12/Tutoria_1A_2017_2018.mp4', '/home/jmramoss/hd/res_slideshow/video_primaria12/Tutoria_2A_2018_2019.mp4'])))

  print(str(p.generateSection(section)))


  #movTitle = tools.generateTitle(title='HOLA', subtitle='ADIOS', title_right='Tutora: Maite Martínez Santana', subtitle_right='CEIP Esteban Navarron Sánchez')
  #movTitle = '/tmp/.movieLxoiqx.mp4'
  #print("movTitle = " + movTitle)
  #movTitle = tools.doAddBackgroundMusic (moviePath='/home/jmramoss/hd/res_slideshow/project/test_year1.mp4', musicData=[{'path': '/home/jmramoss/hd/res_slideshow/bslideshow/titles/culture-code-make-me-move-feat-karra.mp3', 'start': '0:35', 'end': '1:00'}], lenFadeIn=120, lenFadeOut=120)
  #movTitle = tools.doAddBackgroundMusic (moviePath='/home/jmramoss/hd/res_slideshow/project/test_year1.mp4', musicData=[{'path': '/home/jmramoss/hd/res_slideshow/bslideshow/titles/culture-code-make-me-move-feat-karra.mp3', 'start': '0:35', 'end': '1:00'}, {'path': '/home/jmramoss/hd/res_slideshow/bslideshow/titles/happy-mbb.mp3', 'start': '0:17', 'end': '0:42'}, {'path': '/home/jmramoss/hd/res_slideshow/bslideshow/titles/island-mbb.mp3', 'start': '0:12', 'end': '0:37'}], lenFadeIn=120, lenFadeOut=120)

  #movTitle = tools.doAddBackgroundMusic (moviePath='/home/jmramoss/hd/res_slideshow/project/myproject.hjson.mp4', musicData=p.loadMusic(['loveliness', 'blow-it-away']), lenFadeIn=120, lenFadeOut=120)
  #movTitle = tools.doAddBackgroundMusic (moviePath='/home/jmramoss/hd/res_slideshow/project/myproject.hjson.mp4', musicData=p.loadMusic(['loveliness', 'blow-it-away']), lenFadeIn=120, lenFadeOut=120)
  #movTitle = tools.doAddBackgroundMusic (moviePath='/home/jmramoss/hd/res_slideshow/project/myproject.hjson.mp4', musicData=p.loadMusic(['title_adventures', 'title_alive']), lenFadeIn=120, lenFadeOut=120)

  #movTitle = tools.doAddBackgroundMusic   (moviePath='/home/jmramoss/hd/res_slideshow/project/myproject.hjson.mp4', musicData=p.loadMusic('loveliness'), lenFadeIn=120, lenFadeOut=120)
  #print("movTitle = " + movTitle)

  #p.generate()


