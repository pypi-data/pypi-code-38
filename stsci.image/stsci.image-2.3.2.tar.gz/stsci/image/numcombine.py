#   PROGRAM: numcombine.py
#   AUTOHOR: Christopher Hanley
#   DATE:    December 12, 2003
#   PURPOSE: --- We want to reproduce limited imcombine functionality ---
#
#   License: http://www.stsci.edu/resources/software_hardware/pyraf/LICENSE
#
#   HISTORY:
#      Version 0.0.0: Initial Development -- CJH -- 12/30/03
#      Version 0.1.0: Added the ability to apply an upper and lower threshold
#                     to the values of pixels used in the computation of the
#                     median image.  -- CJH -- 12/31/03
#      Version 0.2.0: Added error checking to ensure that for min/max clipping,
#                     more values are not being eliminated than are avilable in
#                     the image stack. Also, a list of masks can now be accepted
#                     as input and applied to the imput image list in addition
#                     to any internal clipping that occurs.-- CJH -- 01/12/04
#      Version 0.2.1: Added the nkeep parameter.  This parameter defines the
#                     minimum number of pixels to be kept in the calculation
#                     after clipping the high and low pixels.
#      Version 0.2.2: Added support for creating a "sum" array.
#                     -- CJH -- 05/17/04
#      Version 0.2.3: Fixed syntax error in _createMaskList method.
#                     -- CJH -- 06/01/04
#      Version 0.2.4: Removed diagnostic print statements.  -- CJH -- 06/28/04
#      Version 0.3.0: Added support for a computing a clipped minimum array.
#                     This is based upon the minimum function in
#                     numarray.images.combine that Todd Miller has implemented
#                     for numarray 1.3. -- CJH -- 03/30/05
#      Version 0.4.0: Modified numcombine to use the numerix interface.  This
#                     allows for the use of either the numarray or numpy array
#                     packages. -- CJH -- 08/18/06
#
#      Version 0.5.0: Added imedian and iaverage functions. -- WJH -- 01/20/12
#
#      Version 0.5.1: changed variable names from numarray* to arr* and removed
#                     use of numerixenv to reflect sole support for numpy
#      Version 0.6.0: Modernized code: replacing numCombine class with
#                     num_combine function.
from __future__ import (absolute_import, division, unicode_literals,
                        print_function)
import warnings
import numpy as np
import stsci.image as image

__version__ = '0.6.0'


class numCombine(object):
    """ **DEPRECATED.** A lite version of the imcombine IRAF task

    .. warn::
        This class has been deprecated since version 0.6.0 and it will be
        removed in a future release. Use `num_combine` instead of this
        class.

    Parameters
    ----------
    arrObjectList : list of ndarray
        A sequence of inputs arrays, which are nominally a stack of identically
        shaped images.

    numarrayMaskList : list of ndarray
        A sequence of mask arrays to use for masking out 'bad' pixels from the
        combination. The ndarray should be a numpy array, despite the
        variable name.

    combinationType : {'median','imedian','iaverage','mean','sum','minimum'}
        Type of operation should be used to combine the images.
        The 'imedian' and 'iaverage' types ignore pixels which have been
        flagged as bad in all input arrays and returns the value from the
        last image in the stack for that pixel.

    nlow : int [Default: 0]
        Number of low pixels to throw out of the median calculation.

    nhigh : int [Default: 0]
        Number of high pixels to throw out of the median calculation.

    nkeep : int [Default: 1]
        Minimun number of pixels to keep for a valid computation.

    upper : float, optional
        Throw out values >= to upper in a median calculation.

    lower: float, optional
        Throw out values < lower in a median calculation.

    Returns
    -------
    combArrObj : ndarray
        The attribute '.combArrObj' holds the combined output array.

    Examples
    --------
    This class can be used to create a median image from a stack of images
    with the following commands:

    >>> import numpy as np
    >>> from stsci.image import numcombine as nc
    >>> a = np.ones([5,5],np.float32)
    >>> b = a - 0.05
    >>> c = a + 0.1
    >>> result = nc.numCombine([a,b,c],combinationType='mean')
    >>> result.combArrObj
    array([[ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665],
           [ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665],
           [ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665],
           [ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665],
           [ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665]], dtype=float32)

    """
    def __init__(self,
        arrObjectList,         # Specifies a sequence of inputs arrays, which are nominally a stack of identically shaped images.
        numarrayMaskList = None,    #
        combinationType = "median", # What time of numarray object should be created?
        nlow = 0,                   # Number of low pixels to throw out of the median calculation
        nhigh = 0,                  # Number of high pixels to throw out of the median calculation
        nkeep = 1,                  # Minimun number of pixels to keep for a valid computation
        upper = None,               # Throw out values >= to upper in a median calculation
        lower = None                # Throw out values < lower in a median calculation
        ):
        warnings.warn("The 'numCombine' class is deprecated and may be removed"
                      " in a future version. Use 'num_combine()' instead.",
                      DeprecationWarning)
        # keep code with new variable name
        arrMaskList = numarrayMaskList

        # Convert the input arrays to the type of array used by the numerix layer
        for i in range(len(arrObjectList)):
            arrObjectList[i] = np.asarray(arrObjectList[i])

        if arrMaskList is not None:
            for i in range(len(arrMaskList)):
                arrMaskList[i] = np.asarray(arrMaskList[i])

        # define variables
        self.__arrObjectList = arrObjectList
        self.__arrMaskList = arrMaskList
        self.__combinationType = combinationType
        self.__nlow = nlow
        self.__nhigh = nhigh
        self.__nkeep = nkeep
        self.__upper = upper
        self.__lower = lower
        self.__masks = []

        # Get the number of objects to be combined
        self.__numObjs = len( self.__arrObjectList )

        # Simple sanity check to make sure that the min/max clipping doesn't throw out all of the pixels.
        if ( (self.__numObjs - (self.__nlow + self.__nhigh)) < self.__nkeep ):
            raise ValueError("Rejecting more pixels than specified by the nkeep parameter!")

        # Create output numarray object
        self.combArrObj = np.zeros(self.__arrObjectList[0].shape,dtype=self.__arrObjectList[0].dtype )

        # Generate masks if necessary and combine them with the input masks (if any).
        self._createMaskList()

        # Combine the input images.
        if ( self.__combinationType.lower() == "median"):
            self._median()
        elif ( self.__combinationType.lower() == "imedian" ):
            self._imedian()
        elif ( self.__combinationType.lower() == "iaverage"  or
                self.__combinationType.lower() == "imean" ):
            self._iaverage()
        elif ( self.__combinationType.lower() == "mean" ):
            self._average()
        elif ( self.__combinationType.lower() == "sum" ):
            self._sum()
        elif ( self.__combinationType.lower() == "minimum"):
            self._minimum()
        else:
            print("Combination type not supported!!!")

    def _createMaskList(self):
        # Create the threshold masks
        if ( (self.__lower != None) or (self.__upper != None) ):
            __tmpMaskList =[]
            for imgobj in self.__arrObjectList:
                __tmpMask = image.threshhold(imgobj,low=self.__lower,high=self.__upper)
                __tmpMaskList.append(__tmpMask)
        else:
            __tmpMaskList = None

        # Combine the threshold masks with the input masks
        if ( (self.__arrMaskList == None) and (__tmpMaskList == None) ):
            self.__masks = None
        elif ( (self.__arrMaskList == None) and (__tmpMaskList != None) ):
            self.__masks = __tmpMaskList
        elif ( (self.__arrMaskList != None) and (__tmpMaskList == None) ):
            self.__masks = self.__arrMaskList
        else:
            for mask in range(len(self.__arrMaskList)):
                self.__masks.append(np.logical_or(__tmpMaskList[mask],self.__arrMaskList[mask]))
        del (__tmpMaskList)
        return None

    def _imedian(self):
        # Create a median image.
        #print "*  Creating a median array..."
        image.imedian(self.__arrObjectList,self.combArrObj,nlow=self.__nlow,nhigh=self.__nhigh,badmasks=self.__masks)
        return None

    def _iaverage(self):
        # Create an average image.
        #print "*  Creating a mean array..."
        image.iaverage(self.__arrObjectList,self.combArrObj,nlow=self.__nlow,nhigh=self.__nhigh,badmasks=self.__masks)
        return None

    def _median(self):
        # Create a median image.
        #print "*  Creating a median array..."
        image.median(self.__arrObjectList,self.combArrObj,nlow=self.__nlow,nhigh=self.__nhigh,badmasks=self.__masks)
        return None

    def _average(self):
        # Create an average image.
        #print "*  Creating a mean array..."
        image.average(self.__arrObjectList,self.combArrObj,nlow=self.__nlow,nhigh=self.__nhigh,badmasks=self.__masks)
        return None

    def _sum(self):
        # Sum the images in the input list
        #print "* Creating a sum array..."
        for imgobj in self.__arrObjectList:
            np.add(self.combArrObj,imgobj,self.combArrObj)
    def _minimum(self):
        # Nominally computes the minimum pixel value for a stack of
        # identically shaped images
        try:
            # Try using the numarray.images.combine function "minimum" that
            # is available as part of numarray version 1.3
            image.minimum(self.__arrObjectList,self.combArrObj,nlow=self.__nlow,nhigh=self.__nhigh,badmasks=self.__masks)
        except:
            # If numarray version 1.3 is not installed so that the "minimum" function is not available.  We will create our own minimum images but no clipping
            # will be available.
            errormsg =  "\n\n#################################################\n"
            errormsg += "#                                               #\n"
            errormsg += "# WARNING:                                      #\n"
            errormsg += "#  Cannot compute a clipped minimum because     #\n"
            errormsg += "#  NUMARRAY version 1.3 or later is not         #\n"
            errormsg += "#  installed.  A minimum image will be created  #\n"
            errormsg += "#  but no clipping will be used.                #\n"
            errormsg += "#                                               #\n"
            errormsg += "#################################################\n"
            print(errormsg)

            # Create the minimum image from the stack of input images.
            # Find the maximum pixel value for the image stack.
            _maxValue = -1e+9

            for imgobj in self.__arrObjectList:
                _newMax = imgobj.max()
                if (_newMax > _maxValue):
                    _maxValue = _newMax

            tmpList = []
            if (self.__arrMaskList != None):
                # Sum the weightMaskList elements
                __maskSum = self.__sumImages(self.__arrMaskList)

                # For each image, set pixels masked as "bad" to the "super-maximum" value.
                for imgobj in range(len(self.__arrObjectList)):
                    tmp = np.where(self.__arrMaskList[imgobj] == 1,_maxValue+1,self.__arrObjectList[imgobj])
                    tmpList.append(tmp)
            else:
                for imgobj in range(len(self.__arrObjectList)):
                  tmpList.append(imgobj)

            # Create the minimum image by computing a median array throwing out all but one of the pixels in the stack
            # starting from the top of the stack.
            image.median(tmpList,self.combArrObj,nlow=0,nhigh=self.__numObjs-1,badmasks=None)

            # If we have been given masks we need to reset the mask values to 0 in the image
            if (self.__arrMaskList != None):
                # Reset any pixl at _maxValue + 1 to 0.
                self.combArrObj = np.where(__maskSum == self.__numObjs, 0, self.combArrObj)


    def __sumImages(self,arrObjectList):
        """ Sum a list of numarray objects. """
        __sum = np.zeros(arrObjectList[0].shape,dtype=arrObjectList[0].dtype)
        for imgobj in arrObjectList:
            __sum += imgobj
        return __sum


def num_combine(data, masks=None, combination_type="median",
                nlow=0, nhigh=0, upper=None, lower=None):
    """ A lite version of the imcombine IRAF task

    Parameters
    ----------
    data : list of 2D numpy.ndarray or a 3D numpy.ndarray
        A sequence of inputs arrays, which are nominally a stack of identically
        shaped images.

    masks : list of 2D numpy.ndarray or a 3D numpy.ndarray
        A sequence of mask arrays to use for masking out 'bad' pixels from the
        combination. The ndarray should be a numpy array, despite the variable
        name.

    combinationType : {'median', 'imedian', 'iaverage', 'mean', 'sum', 'minimum'}
        Type of operation should be used to combine the images.
        The 'imedian' and 'iaverage' types ignore pixels which have been
        flagged as bad in all input arrays and returns the value from the last
        image in the stack for that pixel.

    nlow : int, optional
        Number of low pixels to throw out of the median calculation.

    nhigh : int, optional
        Number of high pixels to throw out of the median calculation.

    upper : float, optional
        Throw out values >= to upper in a median calculation.

    lower : float, optional
        Throw out values < lower in a median calculation.

    Returns
    -------
    comb_arr : numpy.ndarray
        Combined output array.

    Examples
    --------
    This function can be used to create a median image from a stack of images
    with the following commands:

    >>> import numpy as np
    >>> from stsci.image import numcombine as nc
    >>> a = np.ones([5,5],np.float32)
    >>> b = a - 0.05
    >>> c = a + 0.1
    >>> result = nc.numcombine([a,b,c],combinationType='mean')
    >>> result
    array([[ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665],
           [ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665],
           [ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665],
           [ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665],
           [ 1.01666665,  1.01666665,  1.01666665,  1.01666665,  1.01666665]],
           dtype=float32)

    """
    data = np.asarray(data)
    if masks is not None:
        masks = np.asarray(masks)

    # Simple sanity check to make sure that the min/max clipping doesn't throw
    # out all of the pixels.
    if data.shape[0] - nlow - nhigh < 1:
        raise ValueError("Rejecting all pixels due to large 'nval' and/or "
                         "'nhigh'!")

    # Create output numarray object
    comb_arr = np.empty_like(data[0])

    # Create the threshold masks if necessary and combine them with the
    # input masks (if any).
    if lower is not None or upper is not None:
        thmasks = image.threshhold(data, low=lower, high=upper)
        if masks is None:
            masks = thmasks
        else:
            masks = np.logical_or(masks, thmasks)

    # Combine the input images.
    combination_type = combination_type.lower()

    if combination_type == 'median':
        image.median(data, comb_arr, comb_arr.dtype, nlow=nlow, nhigh=nhigh,
                     badmasks=masks)
    elif combination_type == 'imedian':
        image.imedian(data, comb_arr, comb_arr.dtype, nlow=nlow, nhigh=nhigh,
                      badmasks=masks)
    elif combination_type in ['iaverage', 'imean']:
        image.iaverage(data, comb_arr, comb_arr.dtype, nlow=nlow, nhigh=nhigh,
                       badmasks=masks)
    elif combination_type == 'mean':
        image.average(data, comb_arr, comb_arr.dtype, nlow=nlow, nhigh=nhigh,
                      badmasks=masks)
    elif combination_type == 'sum':
        np.sum(data, axis=0, out=comb_arr)
    elif combination_type == 'minimum':
        image.minimum(data, comb_arr, comb_arr.dtype, nlow=nlow, nhigh=nhigh,
                      badmasks=masks)
    else:
        comb_arr.fill(0)
        print("Combination type not supported!!!")

    return comb_arr
