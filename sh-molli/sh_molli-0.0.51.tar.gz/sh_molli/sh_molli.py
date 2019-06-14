import pydicom
import os
import numpy as np
#from sh_molli_fit import *
import tqdm
import PIL

def do_fitting(x,y):
	try:
		return exp_fit(x,y)
	except np.linalg.LinAlgError as e:
		return [-1, -1, -1, -1]

def process_folder(path):
	files = os.listdir(path)
	time = np.zeros((len(files)))
	inv_time = np.zeros((len(files)))
	img_comments = np.zeros((len(files)))
	for i, file in enumerate(files):
		dcm = pydicom.read_file(os.path.join(path,file))
		if i == 0:
			images = np.zeros((dcm.pixel_array.shape[0], dcm.pixel_array.shape[0], len(files)))
		images[:,:,i] = dcm.pixel_array
		time[i] = dcm.TriggerTime
		inv_time[i] = dcm.InversionTime
		img_comments[i] = float(dcm.ImageComments.split()[1])
	
	rngs = [time.max() - time.min(), inv_time.max() - inv_time.min(), img_comments.max() - img_comments.min()]
	ind = rngs.index(max(rngs))
	if ind == 0:
		print('time')
		inv_time = time
	elif ind == 1:
		print('inv_time')
		inv_time = inv_time
	elif ind == 2:
		print('img_comments')
		inv_time = img_comments
		
	sort_inds = np.argsort(inv_time)
	sorted_images = np.zeros(images.shape)
	sorted_images[:,:,range(len(sort_inds))] = images[:,:,sort_inds]
	inv_time.sort()
	
	mask0 = np.ones(len(inv_time))
	mask0[0:0] = -1 # For some symmetry
	
	mask1 = np.ones(len(inv_time))
	mask1[0:1] = -1
	
	mask2 = np.ones(len(inv_time))
	mask2[0:2] = -1
	
	mask3 = np.ones(len(inv_time))
	mask3[0:3] = -1
	
	x_size, y_size, _ = images.shape
	out_array = np.zeros((x_size,y_size))
	for x in tqdm.tqdm(range(x_size)):
		for y in range(y_size):
			#print(x)
			#print(y)
			vals = sorted_images[x,y,:]
			if (vals.max() - vals.min()) > 100:
				out0 = do_fitting(inv_time, mask0 * vals)
				out1 = do_fitting(inv_time, mask1 * vals)
				out2 = do_fitting(inv_time, mask2 * vals)
				out3 = do_fitting(inv_time, mask3 * vals)
				sse = [out0[3], out1[3], out2[3], out3[3]]
				best_fit_ind = sse.index(min(sse))
				if best_fit_ind == 0:
					out_array[x][y] = out0[2] * ((out0[1] / out0[0]) - 1)
				elif best_fit_ind == 1:
					out_array[x][y] = out1[2] * ((out1[1] / out1[0]) - 1)
				elif best_fit_ind == 2:
					out_array[x][y] = out2[2] * ((out2[1] / out2[0]) - 1)
				elif best_fit_ind == 3:
					out_array[x][y] = out3[2] * ((out3[1] / out3[0]) - 1)
	return out_array

def write_image(t1map, filename):
	img = PIL.Image.fromarray(t1map)
	img.save(filename)

def display(t1map):
	from matplotlib import pyplot as plt
	plt.imshow(t1map)
	plt.show()

def __help_string():
	return 'process_sh_molli_series.py -i <inputfolder> -o <outputfilename> -p <plot_flag>'

def __main__():
	import sys
	import getopt
	
	inputfolder = None
	outputfilename = None
	showImage = False
		
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hi:o:p:",["inputfolder=","outputfilename=","plot="])
	except getopt.GetoptError:
		print(__help_string())
		sys.exit(2)
	
	if len(opts) == 0:
		print(__help_string())
		return
	else:
		for opt, arg in opts:
			if opt == '-h':
				print(__help_string())
				sys.exit()
			elif opt in ("-i", "--inputfolder"):
				inputfolder = arg
			elif opt in ("-o", "--outputfilename"):
				outputfilename = arg
			elif opt in ("-p", "--plot"):
				showImage = arg
	
	if inputfolder is not None:
		t1map = process_folder(inputfolder)
	if outputfilename is not None:
		write_image(t1map, outputfilename)
	if showImage:
		display(t1map)

# python module to fit (sh)MOLLI data
#
# exp_fit function based on pull request to scipy
# https://github.com/scipy/scipy/pull/9158/files
# Added return of sum-squared error with the fitted parameters

import numpy as np
from numpy import (
    argsort, asfarray, cumsum, diff, empty, empty_like, exp, log,
    square,
)
from numpy.linalg import inv

import math
from scipy.optimize import curve_fit
from scipy import array
    
# Define fit function
# This will fit the T1 curve to the data
def fit_shmolli(x, a, b, t):
    return ( a - b*pow(math.e, -x/t) )

def my_fit(x,y,ff=fit_shmolli):
    guess = [1000, 1000, 1000]
    params = curve_fit(ff, x, y , p0=guess, method='trf', bounds=(0, 10000), maxfev=10000)
    [a,b,t] = params[0]
    sse = (sum(pow(array(y) - [ff(xi,a,b,t) for xi in array(x)], 2)))
    return [a,b,t,sse]

def exp_fit(x, y, sorted=True):
    """
    Fit an exponential curve to raveled 1D data.

    This algorithm does not require any a-priori knowledge of the data,
    such as the intercept. The fitting parameters are comptued for:

    .. math::

       y = A + Be^{Cx}

    Parameters
    ----------
    x : array-like
        The x-values of the data points. The fit will be performed on a
        raveled version of this array.
    y : array-like
        The y-values of the data points corresponding to `x`. Must be
        the same size as `x`. The fit will be performed on a raveled
        version of this array.
    sorted : bool
        Set to True if `x` is already monotonically increasing or
        decreasing. If False, x will be sorted into increasing order,
        and y will be sorted along with it.

    Return
    ------
    a, b, c : array
        A 3-element array of optimized fitting parameters. The first
        element is the additive bias, the second the multiplicative, and
        the third the exponential.

    Notes
    -----
    The fit is computed non-iteratively in a single pass. It can be used
    to initialize other regression methods based on different
    optimization criteria. The algorithm and the theory behind it is
    presented in the paper below.

    References
    ----------
    Jacquelin, Jean. REGRESSIONS Et EQUATIONS INTEGRALES 14 Jan. 2009, pp. 1518., https://www.scribd.com/doc/14674814/Regressions-et-equations-integrales
    """
    x = asfarray(x).ravel()
    y = asfarray(y).ravel()
    if x.size != y.size:
        raise ValueError('x and y must be the same size')
    if not sorted:
        # Is there a better way to do this in scipy?
        ind = argsort(x)
        x = x[ind]
        y = y[ind]

    s = empty_like(y)
    s[0] = 0
    s[1:] = cumsum(0.5 * (y[1:] + y[:-1]) * diff(x))
    # This might be better: Needs a benchmark
    #s[1:] = y[:-1]
    #s[1:] += y[1:]
    #s[1:] *= np.diff(x)
    #s *= 0.5
    #s = np.cumsum(s)

    xn = x - x[0]
    yn = y - y[0]

    sx2 = square(xn).sum()
    sxs = (xn * s).sum()
    sys = (yn * s).sum()
    ss2 = square(s).sum()
    sxy = (xn * yn).sum()

    out = empty(3, dtype=float)

    _, out[2] = inv([[sx2, sxs], [sxs, ss2]]).dot([[sxy], [sys]])

    ex = exp(out[2] * x)

    se1 = ex.sum()
    se2 = square(ex).sum()
    sy0 = y.sum()
    sye = (y * ex).sum()

    out[0], out[1] = inv([[x.size, se1], [se1, se2]]).dot([[sy0], [sye]])
    
    sse = sum(square(out[0] + out[1]*exp(out[2]*x) - y))

    #return out, sse
    return [out[0],-1*out[1],-1/out[2],sse]

if __name__ == "__main__":
	__main__()
