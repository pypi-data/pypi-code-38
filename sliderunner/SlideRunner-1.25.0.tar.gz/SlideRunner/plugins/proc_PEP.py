"""

        This is SlideRunner - An Open Source Annotation Tool 
        for Digital Histology Slides.

         Marc Aubreville, Pattern Recognition Lab, 
         Friedrich-Alexander University Erlangen-Nuremberg 
         marc.aubreville@fau.de

        If you use this software in research, please citer our paper:
        M. Aubreville, C. Bertram, R. Klopfleisch and A. Maier:
        SlideRunner - A Tool for Massive Cell Annotations in Whole Slide Images. 
        In: Bildverarbeitung für die Medizin 2018. 
        Springer Vieweg, Berlin, Heidelberg, 2018. pp. 309-314.

        This file:
         Positive Pixel Count Algorithm  (Aperio)
         
         see:
         Olson, Allen H. "Image analysis using the Aperio ScanScope." Technical manual. Aperio Technologies Inc (2006).



"""

import SlideRunner.general.SlideRunnerPlugin as SlideRunnerPlugin
import queue
from threading import Thread
from queue import Queue
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt 
import sklearn.cluster
import matplotlib.colors
import staintools
import scipy
import SlideRunner.dataAccess.annotations as annotations 
import matplotlib.path as path
from skimage.feature import blob_dog
from staintools.miscellaneous.get_concentrations import get_concentrations

def BlobDetection(I):
    # removes salt and pepper noise
    image_gray = scipy.ndimage.filters.median_filter(I, size=(2, 2))

    # Difference of Gaussian
    blobs_dog = blob_dog(image_gray, max_sigma=20, threshold=.1)

    #small detected blobs, because of the size (cannot be CD3-positive cells) were deleted,
    blob2 = np.extract(blobs_dog[:,2] > 6, blobs_dog[:,2])
    blob1 = np.extract(blobs_dog[:,2] > 6, blobs_dog[:,1])
    blob0 = np.extract(blobs_dog[:,2] > 6, blobs_dog[:,0])
    blobs_dog = np.c_[blob0, blob1]
    blobs_dog = np.c_[blobs_dog, blob2]

    return blobs_dog

def colorDeconv(img):
    normalizer = staintools.StainNormalizer(method='macenko')
    stain_matrix = normalizer.extractor.get_stain_matrix(img)
    conc = get_concentrations(img, stain_matrix)
    conc = np.reshape(conc,img.shape[0:2]+(2,))

    return conc



class Plugin(SlideRunnerPlugin.SlideRunnerPlugin):
    version = 0.1
    shortName = 'Polyethylene Particle Detection'
    inQueue = Queue()
    outQueue = Queue()
    initialOpacity=1.0
    updateTimer=0.1
    outputType = SlideRunnerPlugin.PluginOutputType.RGB_IMAGE
    description = 'Particle-Detection of PE particles'
    pluginType = SlideRunnerPlugin.PluginTypes.WHOLESLIDE_PLUGIN
    configurationList = list((
                            SlideRunnerPlugin.PushbuttonPluginConfigurationEntry(uid=0, name='Calculate'),
                            SlideRunnerPlugin.PluginConfigurationEntry(uid='min_size', name='Min Particle Area (px2)', initValue=10, minValue=0.0, maxValue=10000.0),
                            SlideRunnerPlugin.PluginConfigurationEntry(uid='max_size', name='Max Particle Area (px2)', initValue=2000, minValue=0.0, maxValue=10000.0),
                            SlideRunnerPlugin.PluginConfigurationEntry(uid='threshold', name='MPE: Threshold', initValue=0.5, minValue=0.0, maxValue=1.5),
                            SlideRunnerPlugin.PluginConfigurationEntry(uid='closingksize', name='MPE: Closing kernel', initValue=16.0, minValue=1.0, maxValue=100.0),
                            SlideRunnerPlugin.PluginConfigurationEntry(uid='CD3threshold', name='CD3: Threshold', initValue=2.0, minValue=0.5, maxValue=3.0),
                            SlideRunnerPlugin.PluginConfigurationEntry(uid='CD3min_size', name='Min CD3 Area (px2)', initValue=100, minValue=0.0, maxValue=1000.0),
                            ))
    
    annotationLabels = {'MacroPE' : SlideRunnerPlugin.PluginAnnotationLabel(0,'Macro PE/SMPE', [0,0,0,0]),
                    'PEP' :  SlideRunnerPlugin.PluginAnnotationLabel(1,'PEP', [255,127,0,255]),
                    'CD3' : SlideRunnerPlugin.PluginAnnotationLabel(2,'CD3 particle', [255,0,255,255])}

    def __init__(self, statusQueue:Queue):
        self.statusQueue = statusQueue
        self.p = Thread(target=self.queueWorker, daemon=True)
        self.p.start()
        
        pass

    def getAnnotationUpdatePolicy():
          # This is important to tell SlideRunner that he needs to update for every change in position.
          return SlideRunnerPlugin.AnnotationUpdatePolicy.UPDATE_ON_SLIDE_CHANGE

    def preprocessImage(self, imageName) -> (np.ndarray, np.ndarray):
        img = staintools.read_image(imageName)
        self.setProgressBar(10)

        conc = colorDeconv(img)
        self.setProgressBar(60)

        return img, conc

    def segmentImage(self, concentrations, threshold, ksize=35, CD3threshold=1.0):

        concsum = concentrations[:,:,0]+concentrations[:,:,1]
        
        thres = 255*np.uint8(concsum<threshold)
        
        ksize=int(ksize)
        kernel = np.ones((ksize,ksize))
        thres = cv2.morphologyEx(thres, cv2.MORPH_CLOSE, kernel)

    #    thres = Closing(thres)
        self.setProgressBar(80)


        image, contours, hierarchy = cv2.findContours(thres, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        print('CD3 threshold: ',CD3threshold)

        thresCD3 = 255*np.uint8(concentrations[:,:,1]>CD3threshold)
        thresCD3 = cv2.morphologyEx(thresCD3, cv2.MORPH_CLOSE, kernel)

        image, contoursCD3, hierarchy = cv2.findContours(thresCD3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


#        print('Pixels above filter:', np.sum(np.float32(thresCD3>0)))

        #image, contoursCD3, hierarchy = cv2.findContours(thresCD3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#        image = scipy.ndimage.filters.median_filter(thresCD3, (10, 10))
#        np.savez('/tmp/conc.npz',concentrations=concentrations, thres=thresCD3)

#        blobsCD3 = BlobDetection(image)

#        print('Output of blob detection: ',blobsCD3.shape)

        return contours, contoursCD3


    def queueWorker(self):
        debugModule= False
        quitSignal = False
        oldFilename = ''
        while not quitSignal:
            job = SlideRunnerPlugin.pluginJob(self.inQueue.get())
            image = job.currentImage

            if (job.jobDescription == SlideRunnerPlugin.JobDescription.QUIT_PLUGIN_THREAD):
                # signal to exit this thread
                quitSignal=True
                continue

            if (oldFilename is not job.slideFilename):
                # process slide
                oldFilename=job.slideFilename
                self.setProgressBar(0)
                img,conc = self.preprocessImage(job.slideFilename)

            print(job.configuration)
            contours,contoursCD3 = self.segmentImage(conc, job.configuration['threshold'],job.configuration['closingksize'], job.configuration['CD3threshold'])
            self.setProgressBar(90)

            self.annos = list()
            for idx in range(len(contoursCD3)):
                
                epsilon = 0.0005*cv2.arcLength(contoursCD3[idx],True)
#                print(epsilon)

                cont = cv2.approxPolyDP(contoursCD3[idx],epsilon,True)
                cont = cont.squeeze()
                ## simplify path
                
                if len(cont.shape)>1:
                    myanno = annotations.polygonAnnotation(uid=idx, coordinates=cont, 
                                                           pluginAnnotationLabel=self.annotationLabels['CD3'])
                    if (cv2.contourArea(contoursCD3[idx])>job.configuration['CD3min_size']):
                        self.annos.append(myanno)

            for idx in range(len(contours)):
                
                epsilon = 0.005*cv2.arcLength(contours[idx],True)
#                print(epsilon)

                cont = cv2.approxPolyDP(contours[idx],epsilon,True)
                cont = cont.squeeze()
                ## simplify path
                
                
                if len(cont.shape)>1:
                    contarea = cv2.contourArea(contours[idx])
                    if (contarea>job.configuration['min_size']) and (contarea<job.configuration['max_size']):
                        myanno = annotations.polygonAnnotation(uid=idx, coordinates=cont, text='MPE', 
                                                           pluginAnnotationLabel=self.annotationLabels['PEP'])
                        self.annos.append(myanno)
                    elif (contarea>job.configuration['max_size']):
                        myanno = annotations.polygonAnnotation(uid=idx, coordinates=cont, text='MacroPE', 
                                                           pluginAnnotationLabel=self.annotationLabels['MacroPE'])
                        self.annos.append(myanno)

#            for idx in range(blobsCD3.shape[0]):
                
#                myanno = annotations.circleAnnotation(uid=idx+1000, x1=blobsCD3[idx,1],y1=blobsCD3[idx,0], r=blobsCD3[idx,2], pluginAnnotationLabel=self.annotationLabels['CD3'])
                                                           
#                self.annos.append(myanno)

            self.updateAnnotations()
            self.setProgressBar(-1)
            self.setMessage('found %d PE particle candidates.' % len(self.annos))



    def getAnnotations(self):
        return self.annos


    def getAnnotationLabels(self):
            # sending default annotation labels
            return [self.annotationLabels[k] for k in self.annotationLabels.keys()]

        