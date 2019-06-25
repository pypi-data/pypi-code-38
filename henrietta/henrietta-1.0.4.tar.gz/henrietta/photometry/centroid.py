from numpy import *
import pdb
import matplotlib.pyplot as plt

def mean_centroid(image, center, boxsize=60.):

	'''
    Determines the weighted mean centroid for multiple stars

    Parameters:
    -----------
    image : ndarray
        Image for aperture photometry to be performed on.
    center : 2darray
        A list of positions in x,y pixel coordinates for each star.
        Needs to be as [[0,0],[1,1]...]
		Basically is a best guess to the center
    boxsize : int, even number
        The size of the box to crop around star, needs to be even
    num_stars : int
        Number of stars to look at

    Returns
    -------
    centroid position for each star : array
    '''

	# figure out the number of stars from the list of centers
	num_stars = len(center)
	centroid = zeros((num_stars,2)) #setting up the centroid array
	L = boxsize #size of the box to isolate the star


	for k in range(num_stars):
		c = center[k] #get the approximate star location

		x = arange((c[0]-L/2.),(c[0]+L/2.),1)
		y = arange((c[1]-L/2.),(c[1]+L/2.),1)
		cropped_images = image[int(c[0]-L/2.):int(c[0]+L/2.),int(c[1]-L/2.):int(c[1]+L/2.)]
		cropped_images = where(isfinite(cropped_images),cropped_images,0)
		plt.imshow(cropped_images)
		plt.show()
		print k




		im = cropped_images
		Ii = []
		Jj = [] #keeps track of the row and column sums
		for i in range(int(L)):
			Ii.append(sum(im[i,:]))
			Jj.append(sum(im[:,i]))
		Ii=array(Ii)
		Jj=array(Jj)
		Imean = 1./L*sum(Ii)
		Jmean = 1./L*sum(Jj)

		Ii_red = Ii[where(Ii>Imean)]
		Jj_red = Jj[where(Jj>Jmean)]
		x_red = x[where(Ii>Imean)]
		y_red = y[where(Jj>Jmean)]
		xc = sum((Ii_red-Imean)*x_red)/sum(Ii_red-Imean)
		yc = sum((Jj_red-Jmean)*y_red)/sum(Jj_red-Jmean)
		x_center = xc #put back in normal coordinates
		y_center = yc

		centroid[k] = [x_center,y_center]

	return centroid
