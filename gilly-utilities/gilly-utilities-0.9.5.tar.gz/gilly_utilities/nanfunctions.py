import sys
import warnings 

import numpy as np
from datetime import datetime

from .system import iszero, isval, isarray
from .manipulation import array, flatten
from .datetime64 import isnat, dt2hours, hours2dt

# Compatability for python3
if getattr(sys.version_info, 'major') == 3:
    xrange = range

def _simple_slice(arr, inds, axis):
    """
    This does the same as np.take() except only supports simple slicing, 
    not advanced indexing, and thus is much faster.
    
    References
    ----------
    https://stackoverflow.com/a/37729566
    """

    sl = [slice(None)] * arr.ndim
    sl[axis] = inds

    return arr[tuple(sl)]

def _antiany(arr, func, axis=1, how='any', unpack=False, sortby=False, return_mask=False):
    """
    Worker function to remove any value specified using func along a
    specific axis.
    
    Parameters
    ----------
    
    arr : tuple of 1D array_like or non-tuple array_like
        If arr is a tuple, it is assumed that each element is a 
        column and will be transposed before any processing is 
        performed. Otherwise arr is treated "as is" and will be 
        processed directly.
    func : module
        A module definition used to specify the type of values to 
        remove. Examples are func=np.isnan, func=np.isinf. Be careful 
        on specifying the polarity for these functions. For example 
        func=np.isnan will remove all nan values despite np.isnan will
        return True for any values that are nan. Issue might occur if 
        you specify np.isfinite, which would remove all finite values, 
        despite the usual use would be to remove both np.nan and np.inf 
        values simultaneously. In this specific case you want to 
        specify func=lambda x: ~np.isfinite(x).
    axis : int, optional
        The axis you want to remove an np.nan values from. Here is a 
        help guide to picking the correct axis values:
            
            axis = 0 : column wise
            axis = 1 : row wise (DEFAULT)
    how : str, optional
        Test whether the entire axis contains an invalid value or whether
        only 1 invalid value allows removal. Only works on 2D data and
        uses the axis parameter. Default is 'any'.
    unpack : boolean, optional
        Determines whether to unpack the array into individual columns,
        useful if you originally had N column arrays which you want to 
        temporarily merge for invalid values.
    sortby : int, default is False
        Specify if you want to sort the data by a particular column. 
        Default is false and does not sort data, but other options are 
        to specify the column which you want to sort by.
    return_mask : bool, optionl, default is False
        Specify if you want to return the mask of invalid values along 
        the correct axis you specified, instead of the corrected arr.
        
    Returns
    -------
    
    arr_nonan : ndarry of floats or list of arrays dependent upon andxor
        The finalised ndarray with all nans removed will be returned 
        unless andxor is False where a list of column arrays will be 
        returned.
    
    Examples
    --------
    
    >>> x = np.array([1,2,np.nan,4,5])
    >>> y = np.array([20,30,40,np.nan,np.nan])
    
    >>> xy_new = antinan(np.array([x,y])
    
    >>> xy_new
    array([[1., 2.],
           [20., 30.]])

    References
    -------
    http://stackoverflow.com/questions/27532503/remove-nan-row-from-x-array-and-also-the-corresponding-row-in-y
    https://www.w3resource.com/python-exercises/numpy/python-numpy-exercise-91.php
    https://stackoverflow.com/a/37729566
    
    """

    # Force arr to be a numpy array
    if isinstance(arr, tuple):
        arr = np.asarray(arr).T
    else:   
        arr = np.asarray(arr)
    
    # Check if arr has any data
    if arr.size == 0:
        return np.array([])
    
    # For 1D arrays
    if arr.ndim == 1:

        # Calculate mask of invalid values
        mask = ~func(arr)

        # Return mask if necessary
        if return_mask:
            return mask

        # Sort data if necessary 
        if sortby is not False:
            return np.sort(arr[mask], kind='mergesort')
        else:
            return arr[mask]

    # For ND arrays
    elif arr.ndim > 0:

        # Determine index for all nan values in each column
        if how == 'any':
            mask = ~func(arr).any(axis=axis)
        elif how == 'all':
            mask = ~func(arr).all(axis=axis)
        else:
            raise ValueError("how parameter can only be either 'all' or 'any'")

        # Return mask if necessary
        if return_mask:
            return mask

        # Remove all rows with a nan
        arr_noany = _simple_slice(arr.T, mask, axis=axis).T

    else:
        return arr

    # Sort array by column if necessary
    if sortby is not False: 
        arr_noany = arr_noany[arr_noany[:,int(sortby)].argsort(kind='mergesort')]

    if unpack:
        return tuple(arr_noany.reshape(-1, arr_noany.shape[1]).T)
    else:
        return arr_noany

def antifinite(arr, axis=1, how='any', andxor=True, unpack=False, sortby=False, 
        return_mask=False, oldmethod=False):
    """
    Removes any np.inf and np.nan values from arr along axis.
    
    See _antiany for __doc__
    
    oldmethod : bool, optional
        Specifiy to use the old method for removing nan and inf values 
        (used for backwards compatability, or False to use new method
    
    Update (For oldmethod)
    ------
    Added support for python datetime and numpy datetime64 objects automatically. This
    is achieved by converting any column with datetimes into floating point numbers.
    Run antifinite as normal and then convert back to datetime objects again automatically.
    """

    if oldmethod:
        #For 1D arrays
        if len(np.shape(arr)) == 1 and np.array(arr).dtype != 'O':
            
            #Check array does not contain datetime function. If so convert to number temporarily
            arr, check, dtype = dt2hours(arr, epoch=np.datetime64("1900-01-01"), checkback=True)

            if sortby is not False:
                if check is False:
                    return np.sort(arr[np.isfinite(arr)], kind='mergesort')
                else: 
                    return hours2dt(np.sort(arr[np.isfinite(arr)], kind='mergesort'), epoch=np.datetime64("1900-01-01"), dtype=dtype)
            else:
                if check is False:
                    return arr[np.isfinite(arr)]  
                else:
                    return hours2dt(arr[np.isfinite(arr)], epoch=np.datetime64("1900-01-01 00:00:00"), dtype=dtype)

        #For ND arrays
        if np.shape(arr)[0] > 0:
            
            #Convert datetime columns to hours
            array_has_datetime     = np.zeros(np.shape(arr)[0], dtype=bool)
            array_dtype            = np.zeros(np.shape(arr)[0], dtype='S25')
            for i in xrange(np.shape(arr)[0]): 
                if isinstance(arr[i][0], np.datetime64) or isinstance(arr[i][0], datetime):
                    array_has_datetime[i] = True
                    array_dtype[i] = arr[i][0].dtype
                else:
                    array_has_datetime[i] = False
                    array_dtype[i] = arr[i][0].dtype
            arr = np.asarray(arr, dtype=float)    

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                arr[arr <= -10e+17] = np.nan

            if andxor == True:
                #Determine index for all nan values in each column
                x_mask = np.any(np.isfinite([arr[0]]), axis=0)
                
                for i in xrange(1, arr.shape[0]): x_mask &= np.any(np.isfinite([arr[i]]), axis=0)
                
                #Remove all rows with a nan
                x_nonan = arr.T[x_mask]

            else:
                #Split x into column arrays
                x_arrays      = zip(np.zeros([arr.shape[0]]))
                x_nonan = zip(np.zeros([arr.shape[0]]))
                for i in xrange(arr.shape[0]): x_arrays[i] = arr[i]
                
                #Remove nans from each column individually
                for i in xrange(arr.shape[0]): x_nonan[i] = x_arrays[i][np.any(np.isfinite([x_arrays[i]]), axis=0)]
        else:
            #return np.split(arr.T, arr.shape[0])
            return arr

        #Sort array by column if specified
        if sortby is not False: x_nonan = x_nonan[x_nonan[:,int(sortby)].argsort(kind='mergesort')]

        #Return original dtype
        out_data = zip(np.zeros(len(arr)))
        for i in xrange(len(arr)):
            out_data[i] = x_nonan[:,i].astype(np.float64).astype(array_dtype[i])

        if unpack:
            return out_data    
        else:
            return np.vstack(out_data)

        # #Convert arrays that contained datetimes
        # if not np.all(array_dtype == array_dtype[0]): x_nonan = x_nonan.astype(object)
        # for i in xrange(arr.shape[0]): x_nonan[:,i] = x_nonan[:,i].astype(np.float64).astype(array_dtype[i])

        # x_nonan[:,1] = x_nonan[:,1].astype(np.float64)
        # print("x_nonan[:,1]", x_nonan[:,1].dtype)
        # if unpack == True:
            # return flatten(np.split(x_nonan.T, arr.shape[0]))
        # else:

            # return x_nonan

    else:
        return _antiany(arr, lambda x: ~np.isfinite(x), axis=axis,
                how=how, unpack=unpack, sortby=sortby, 
                return_mask=return_mask)

def antinan(arr, axis=1, how='any', unpack=False, sortby=False, 
        return_mask=False):
    """
    Removes any np.nan values from arr along axis.
    
    See _antiany for __doc__
    """

    return _antiany(arr, np.isnan, axis=axis, how=how, unpack=unpack, 
            sortby=sortby, return_mask=return_mask)

def antiinf(arr, axis=1, how='any', unpack=False, sortby=False, 
        return_mask=False):
    """
    Removes any np.inf values from arr along axis.
    
    See _antiany for __doc__
    """

    return _antiany(arr, np.isinf, axis=axis, how=how, unpack=unpack, 
            sortby=sortby, return_mask=return_mask)

def antinat(arr, axis=1, how='any', unpack=False, sortby=False, 
        return_mask=False):
    """
    Removes any NaT datetimes from arr along axis.
    
    See _antiany for __doc__
    """

    return _antiany(arr, isnat, axis=axis, how=how, unpack=unpack, 
            sortby=sortby, return_mask=return_mask)      

def antizero(arr, axis=1, how='any', unpack=False, sortby=False, 
        return_mask=False):
    """
    Removes any zero values from arr along axis.
    
    See _antiany for __doc__
    """

    return _antiany(arr, iszero, axis=axis, how=how, unpack=unpack, 
            sortby=sortby, return_mask=return_mask)      

def antival(arr, val, axis=1, how='any', unpack=False, sortby=False, 
        return_mask=False):
    """
    Removes any values from arr along axis.
    
    See _antiany for __doc__
    """

    return _antiany(arr, lambda x: isval(x, val), axis=axis, how=how, 
            unpack=unpack, sortby=sortby, return_mask=return_mask)      

def conditional(arr, conditions, operators=None, verbose=False):
    """
    Returns a boolean array of the conditions on arr, taking into account
    invalid values.
    
    conditions needs to be an array_like containing string of conditions
    
    e.g. conditions = ("> 2", "< 10")
    
    operators needs to be an array_like containing string of operations
    
    e.g. operators = ("&",)
    
    with length 1 less than conditions.
    
    Overall this follows a conditions as so

    Reference
    ---------
    https://stackoverflow.com/a/25346972
    """
    
    if not isarray(arr):
        raise ValueError("arr needs to be array_like")
    if len(conditions) > 1 and operators is None:
        raise ValueError("need to specifiy operators if more than 1 conditions is specified")
    if len(conditions) - len(operators) != 1:
        raise ValueError("operators needs to have a length 1 less than conditions")
    
    # Convert arr to numpy if required
    arr = np.atleast_1d(arr)
    conditions = np.atleast_1d(conditions)
    operators = np.atleast_1d(operators)
    
    if (conditions.ndim > 1) or (operators.ndim > 1): 
        raise ValueError("conditions and operators must be 1 dimensional")
    
    # Determine invalid values
    mask = np.isfinite(arr)
    
    # Loop through each conditional
    if conditions.size > 1:
        full_conditions = ''
        for cond, op in zip(conditions, operators):
            full_conditions += '(arr[mask] ' + cond + ') ' + op + ' '
            
        full_conditions += '(arr[mask] ' + conditions[-1] + ')'
    else:
        full_conditions = 'arr[mask] ' + cond
    
    if verbose:
        print("full_conditions", full_conditions)
    
    # Perform conditions
    mask[mask] &= eval(full_conditions)
    
    # Return mask
    return mask
    
def nan_helper(y):
    """
    Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    
    References
    ----------
    https://stackoverflow.com/a/6520696
    """

    return np.isnan(y), lambda z: z.nonzero()[0]    