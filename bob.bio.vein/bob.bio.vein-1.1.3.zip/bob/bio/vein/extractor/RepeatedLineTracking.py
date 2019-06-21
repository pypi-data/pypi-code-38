#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import math
import numpy
import scipy.ndimage

import bob.core
import bob.io.base
import bob.ip.base

from bob.bio.base.extractor import Extractor


class RepeatedLineTracking (Extractor):
  """Repeated Line Tracking feature extractor

  Based on N. Miura, A. Nagasaka, and T. Miyatake. Feature extraction of finger
  vein patterns based on repeated line tracking and its application to personal
  identification. Machine Vision and Applications, Vol. 15, Num. 4, pp.
  194--203, 2004
  """

  def __init__(
      self,
      iterations = 3000, # Maximum number of iterations
      r = 1,             # Distance between tracking point and cross section of the profile
      profile_w = 21,    # Width of profile (Error: profile_w must be odd)
      rescale = True,
      seed = 0,          # Seed for the algorithm's random walk
      ):

    # call base class constructor
    Extractor.__init__(
        self,
        iterations = iterations,
        r = r,
        profile_w = profile_w,
        rescale = rescale,
        seed = seed,
        )

    # block parameters
    self.iterations = iterations
    self.r = r
    self.profile_w = profile_w
    self.rescale = rescale
    self.seed = seed


  def repeated_line_tracking(self, finger_image, mask):
    """Computes and returns the MiuraMax features for the given input
    fingervein image"""

    # Sets the random seed before starting to process
    numpy.random.seed(self.seed)

    finger_mask = numpy.zeros(mask.shape)
    finger_mask[mask == True] = 1

    # Rescale image if required
    if self.rescale == True:
      scaling_factor = 0.6
      finger_image = bob.ip.base.scale(finger_image,scaling_factor)
      finger_mask = bob.ip.base.scale(finger_mask,scaling_factor)
      #To eliminate residuals from the scalation of the binary mask
      finger_mask = scipy.ndimage.binary_dilation(finger_mask, structure=numpy.ones((1,1))).astype(int)

    p_lr = 0.5  # Probability of goin left or right
    p_ud = 0.25 # Probability of going up or down

    Tr = numpy.zeros(finger_image.shape) # Locus space
    filtermask = numpy.array(([-1,-1],[-1,0],[-1,1],[0,-1],[0,0],[0,1],[1,-1],[1,0],[1,1]))

    # Check if progile w is even
    if (self.profile_w.__mod__(2) == 0):
        print ('Error: profile_w must be odd')

    ro = numpy.round(self.r*math.sqrt(2)/2)    # r for oblique directions
    hW = (self.profile_w-1)/2                  # half width for horz. and vert. directions
    hWo = numpy.round(hW*math.sqrt(2)/2)       # half width for oblique directions

    # Omit unreachable borders
    border = int(self.r+hW)
    finger_mask[0:border,:] = 0
    finger_mask[finger_mask.shape[0]-border:,:] = 0
    finger_mask[:,0:border] = 0
    finger_mask[:,finger_mask.shape[1]-border:] = 0

    ## Uniformly distributed starting points
    aux = numpy.argwhere( (finger_mask > 0) == True )
    indices = numpy.random.permutation(aux)
    indices = indices[0:self.iterations,:]    # Limit to number of iterations

    ## Iterate through all starting points
    for it in range(0,self.iterations):
        yc = indices[it,0] # Current tracking point, y
        xc = indices[it,1] # Current tracking point, x

        # Determine the moving-direction attributes
        # Going left or right ?
        if (numpy.random.random_sample() >= 0.5):
            Dlr = -1  # Going left
        else:
            Dlr = 1   # Going right

        # Going up or down ?
        if (numpy.random.random_sample() >= 0.5):
            Dud = -1  # Going up
        else:
            Dud = 1   # Going down

        # Initialize locus-positition table Tc
        Tc = numpy.zeros(finger_image.shape, numpy.bool)

        #Dlr = -1; Dud=-1; LET OP
        Vl = 1
        while (Vl > 0):
            # Determine the moving candidate point set Nc
            Nr = numpy.zeros([3,3], numpy.bool)
            Rnd = numpy.random.random_sample()
            #Rnd = 0.8 LET OP
            if (Rnd < p_lr):
                # Going left or right
                Nr[:,1+Dlr] = True
            elif (Rnd >= p_lr) and (Rnd < (p_lr + p_ud)):
                # Going up or down
                Nr[1+Dud,:] = True
            else:
                # Going any direction
                Nr = numpy.ones([3,3], numpy.bool)
                Nr[1,1] = False
            #tmp = numpy.argwhere( (~Tc[yc-2:yc+1,xc-2:xc+1] & Nr & finger_mask[yc-2:yc+1,xc-2:xc+1].astype(numpy.bool)).T.reshape(-1) == True )
            tmp = numpy.argwhere( (~Tc[yc-1:yc+2,xc-1:xc+2] & Nr & finger_mask[yc-1:yc+2,xc-1:xc+2].astype(numpy.bool)).T.reshape(-1) == True )
            Nc = numpy.concatenate((xc + filtermask[tmp,0],yc + filtermask[tmp,1]),axis=1)
            if (Nc.size==0):
                Vl=-1
                continue

            ## Detect dark line direction near current tracking point
            Vdepths = numpy.zeros((Nc.shape[0],1)) # Valley depths
            for i in range(0,Nc.shape[0]):
                ## Horizontal or vertical
                if (Nc[i,1] == yc):
                    # Horizontal plane
                    yp = Nc[i,1]
                    if (Nc[i,0] > xc):
                        # Right direction
                        xp = Nc[i,0] + self.r
                    else:
                        # Left direction
                        xp = Nc[i,0] - self.r
                    Vdepths[i] = finger_image[int(yp + hW), int(xp)] - 2*finger_image[int(yp),int(xp)] + finger_image[int(yp - hW), int(xp)]
                elif (Nc[i,0] == xc):
                    # Vertical plane
                    xp = Nc[i,0]
                    if (Nc[i,1] > yc):
                        # Down direction
                        yp = Nc[i,1] + self.r
                    else:
                        # Up direction
                        yp = Nc[i,1] - self.r
                    Vdepths[i] = finger_image[int(yp), int(xp + hW)] - 2*finger_image[int(yp),int(xp)] + finger_image[int(yp), int(xp - hW)]

                ## Oblique directions
                if ( (Nc[i,0] > xc) and (Nc[i,1] < yc) ) or ( (Nc[i,0] < xc) and (Nc[i,1] > yc) ):
                    # Diagonal, up /
                    if (Nc[i,0] > xc and Nc[i,1] < yc):
                        # Top right
                        xp = Nc[i,0] + ro
                        yp = Nc[i,1] - ro
                    else:
                        # Bottom left
                        xp = Nc[i,0] - ro
                        yp = Nc[i,1] + ro
                    Vdepths[i] = finger_image[int(yp - hWo), int(xp - hWo)] - 2*finger_image[int(yp),int(xp)] + finger_image[int(yp + hWo), int(xp + hWo)]
                else:
                    # Diagonal, down \
                    if (Nc[i,0] < xc and Nc[i,1] < yc):
                        # Top left
                        xp = Nc[i,0] - ro
                        yp = Nc[i,1] - ro
                    else:
                        # Bottom right
                        xp = Nc[i,0] + ro
                        yp = Nc[i,1] + ro
                    Vdepths[i] = finger_image[int(yp + hWo), int(xp - hWo)] - 2*finger_image[int(yp),int(xp)] + finger_image[int(yp - hWo), int(xp + hWo)]
            # End search of candidates
            index = numpy.argmax(Vdepths)  #Determine best candidate
            # Register tracking information
            Tc[yc, xc] = True
            # Increase value of tracking space
            Tr[yc, xc] = Tr[yc, xc] + 1
            # Move tracking point
            xc = Nc[index, 0]
            yc = Nc[index, 1]

    img_veins = Tr

    # Binarise the vein image
    md = numpy.median(img_veins[img_veins>0])
    img_veins_bin = img_veins > md
    img_veins_bin = scipy.ndimage.binary_closing(img_veins_bin, structure=numpy.ones((2,2))).astype(int)

    return img_veins_bin.astype(numpy.float64)


  def skeletonize(self, img):
    import scipy.ndimage.morphology as m
    h1 = numpy.array([[0, 0, 0],[0, 1, 0],[1, 1, 1]])
    m1 = numpy.array([[1, 1, 1],[0, 0, 0],[0, 0, 0]])
    h2 = numpy.array([[0, 0, 0],[1, 1, 0],[0, 1, 0]])
    m2 = numpy.array([[0, 1, 1],[0, 0, 1],[0, 0, 0]])
    hit_list = []
    miss_list = []
    for k in range(4):
        hit_list.append(numpy.rot90(h1, k))
        hit_list.append(numpy.rot90(h2, k))
        miss_list.append(numpy.rot90(m1, k))
        miss_list.append(numpy.rot90(m2, k))
    img = img.copy()
    while True:
        last = img
        for hit, miss in zip(hit_list, miss_list):
            hm = m.binary_hit_or_miss(img, hit, miss)
            img = numpy.logical_and(img, numpy.logical_not(hm))
        if numpy.all(img == last):
            break
    return img


  def __call__(self, image):
    """Reads the input image, extract the features based on Maximum Curvature
    of the fingervein image, and writes the resulting template"""

    finger_image = image[0]    #Normalized image with or without histogram equalization
    finger_mask = image[1]

    return self.repeated_line_tracking(finger_image, finger_mask)
