import numpy as np
import matplotlib.pyplot as plt
import photutils
import pdb
plt.ion()

def photometry(ax, image,pos,ap_size=10,r_in=20,r_out=30,back_photo=True):

    '''
    Create apertures around specified list of stars

    Parameters:
    -----------
    ax : axis class
        axis of a subplot.
    image : ndarray
        Image for aperture photometry to be performed on.
    pos : 2darray
        A list of positions in x,y pixel coordinates for each star.
        Needs to be as [[0,0],[1,1]...]
    ap_size : int
        The radius of a circular aperture in pixel size
    r_in : int
        The inner radius of background aperture in pixel size
        (Ignore if back_photo=False)
    r_out : int
        The outer radius of background aperture in pixel size
        (Ignore if back_photo=False)
    back_photo : bool
        Set to True if want to return an array of background values, False
        to ignore anything to do with background

    Returns
    -------
    photometry of each star : array
    average background pixel value around each star : array (If back_photo=True)
    plots image with the aperture and centroids located for each star
    '''

    nstars = np.arange(0,np.shape(pos)[0],1)
    name_stars = []
    for i in nstars:
        name_stars.append('Star {}'.format(i))
    #print name_stars

    aperture = photutils.CircularAperture(pos,r=ap_size)

    if back_photo == True:
        back_aperture = photutils.CircularAnnulus(pos,r_in,r_out)

    pos = np.array(pos)


    #plt.imshow(image,origin='lower')

    for i in range(len(name_stars)):
        circle1 = plt.Circle((pos[i,0], pos[i,1]), ap_size, color='black',fill=False,zorder=100)
        ax.add_artist(circle1)
        plt.axhline(pos[i,1],xmin=pos[i,0]/100.-.01,xmax=pos[i,0]/100.+.02,color='black')
        plt.axvline(pos[i,0],ymin=pos[i,1]/100.-.01,ymax=pos[i,1]/100.+.02,color='black')
        plt.text(pos[i,0]+ap_size+1, pos[i,1], name_stars[i],zorder=11)
        #print pos[i,1]
        #print pos[i,0]

        if back_photo == True:
            circle2 = plt.Circle((pos[i,0], pos[i,1]), r_in, color='cyan',fill=False,zorder=10)
            circle3 = plt.Circle((pos[i,0], pos[i,1]), r_out, color='cyan',fill=False,zorder=10)
            ax.add_artist(circle2)
            ax.add_artist(circle3)
    #aperture.plot(origin=(0,0),indices=None,ax=ax,fill=False)
    #plt.ion()




    phot_table = photutils.aperture_photometry(image,aperture)
    flux_values = phot_table['aperture_sum'].data #gets a list of the total flux in specified aperture for each star

    if back_photo == True:
        back_table = photutils.aperture_photometry(image,back_aperture)
        area = np.pi*(r_out**2-r_in**2)
        a = np.ones((np.shape(image)[0],np.shape(image)[1]))
        area = photutils.aperture_photometry(a,back_aperture)
        back_values = back_table['aperture_sum'].data/area['aperture_sum'].data
        return flux_values,back_values*np.pi*ap_size**2
    else:
        return flux_values
