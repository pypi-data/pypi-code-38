import SlideRunner.general.SlideRunnerPlugin as SlideRunnerPlugin
import SlideRunner.dataAccess.annotations as annotations
import queue
from threading import Thread
from queue import Queue
import cv2
import numpy as np
import torch
from fastai import *
from fastai.vision import *
import torchvision.transforms as transforms

import math
import cv2
import numpy as np


'''

MacenkoNorm: Normalize a RGB image by mapping the appearance to that of a target

 Inputs:
 image    - Original Image.

 Output:
 Inorm    - Normalised RGB image.

 References:
 [1] M Macenko, M Niethammer, JS Marron, D Borland, JT Woosley, X Guan, C
     Schmitt, NE Thomas. "A method for normalizing histology slides for
     quantitative analysis". IEEE International Symposium on Biomedical
     Imaging: From Nano to Macro, 2009 vol.9, pp.1107-1110, 2009.

 Acknowledgements:
     This function is inspired by the Stain normalization toolbox by WARWICK
     ,which is available for download at:
     http://www2.warwick.ac.uk/fac/sci/dcs/research/tia/software/sntoolbox/

 Info: provided by Max Krappmann
'''

class Plugin(SlideRunnerPlugin.SlideRunnerPlugin):
    version = 0.1
    shortName = 'PEP-UNET'
    inQueue = Queue()
    outQueue = Queue()
    initialOpacity=0.5
    updateTimer=0.5
    outputType = SlideRunnerPlugin.PluginOutputType.RGB_IMAGE
    description = 'PEP-UNET'
    pluginType = SlideRunnerPlugin.PluginTypes.IMAGE_PLUGIN
    configurationList = list(())

    def __init__(self, statusQueue:Queue):
        self.statusQueue = statusQueue
        self.p = Thread(target=self.queueWorker, daemon=True)
        self.p.start()
        
        pass

    def queueWorker(self):
        quitSignal = False
        fname = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'UNET-PEPsegmentation.pth'
        state = torch.load(fname, map_location='cpu')     if defaults.device == torch.device('cpu')     else torch.load(fname)
        model = state.pop('model')
        mean = state['data']['normalize']['mean']
        std = state['data']['normalize']['std']

        while not quitSignal:
            job = SlideRunnerPlugin.pluginJob(self.inQueue.get())
            image = job.currentImage

            if (job.jobDescription == SlideRunnerPlugin.JobDescription.QUIT_PLUGIN_THREAD):
                # signal to exit this thread
                quitSignal=True
                continue

            print('Macenko norm plugin: received 1 image from queue')
            self.setProgressBar(0)

            print(job)
            print(job.configuration)

            with torch.no_grad():
                print('Original mean and std: ',np.mean(image),np.std(image))
                sizeY, sizeX, b = image.shape
                print('Input size: ',image.shape)
                tImageSize = (sizeY, sizeX, 3)
                sizeX = sizeX - (sizeX % 2)
                sizeY = sizeY - (sizeY % 2)
                image = image[0:sizeY,0:sizeX,0:3]
                print('Input size: ',image.shape)
                image = torch.from_numpy(image[:,:,0:3].transpose(2,0,1).astype(np.float32, copy=False)/255.0)
                print('Mean and std: ',mean,std)
                image = transforms.Normalize(mean,std)(image)
                print('Input size: ',image.shape)
                out = model(image[None, :,:,:]).argmax(1)
                print(out.shape)
                out = np.array(out[0,:,:])
                print(out.shape)
                retval = np.zeros(tImageSize)
                print('Max values:',np.max(out))
                retarr = np.zeros((sizeY,sizeX,3))
                retarr[out==1,0] = 255
                retarr[out==2,1] = 255
                retarr[out==3,2] = 255
                retval[0:sizeY,0:sizeX,:] = retarr


            self.returnImage(np.float32(retval), job.procId)
            self.setMessage('PEP UNET: done.')
            self.setProgressBar(-1)



        