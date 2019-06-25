import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

def star_plot(image,pos,ap_size=10,centroid=np.array([0,0]),r_in=20,r_out=30,back_plot=False,centroid_plot=False):


    '''
    Creates a plot of the image and the zoomed in images of the stars

    Parameters:
    -----------
    image : ndarray
        Full image of the frame
    pos : 2darray
        A list of positions in x,y pixel coordinates for each star.
        Needs to be as [[0,0],[1,1]...]
    ap_size : int
        The radius of a circular aperture in pixel size
    centroid : 2darray
        The centroid pixel location for each star to be plotted.
         (Will only plot if centroid_plot is True)
         Needs to be as [[0,0],[0,1]]
    r_in : int
        The inner radius of background aperture in pixel size
        (Ignore if back_plot=False)
    r_out : int
        The outer radius of background aperture in pixel size
        (Ignore if back_plot=False)
    back_plot : bool
        Set to True if want to plot the background aperture, False otherwise
    centroid_plot : bool
        Set to True if want the centroid location to be plotted, False otherwise

    Returns
    -------
    plots of the full image plus all the stars
    '''
    pos = np.array(pos)
    centroid =  np.array(centroid)
    #to get the number of plots needed
    num_plots = np.shape(pos)[0]

    plt.figure(figsize=[num_plots*10,5])
    plt.subplot(1,num_plots+1,1)
    plt.imshow(image)

    for i in range(num_plots):
        #i is essentially the star number
        x1 = pos[i,0]
        y1 = pos[i,1]
        if back_plot == True:
            #use the rout aperture size for cropping
            crop_image = image[int(x1-r_out):int(x1+r_out)+1,int(y1-r_out):int(y1+r_out)+1]
        elif back_plot == False:
            #use the aperture size plus 2 pixels for cropping
            crop_image = image[int(x1-ap_size-2):int(x1+ap_size+2),int(y1-ap_size-2):int(y1+ap_size+2)]
        plot_size = np.shape(crop_image)[0]
        plt.subplot(1,num_plots+1,i+2)
        plt.imshow(crop_image)
        if centroid_plot==True:
            m = plt.Circle((centroid[i,0]-x1+plot_size/2.-.5,centroid[i,1]-y1+plot_size/2.-.5),ap_size,facecolor='none',edgecolor='black')
        else:
            m = plt.Circle((plot_size/2.-.5,plot_size/2.-.5),ap_size,facecolor='none',edgecolor='black')
        plt.figure(1).add_subplot(1,num_plots+1,(i+2)).add_artist(m)
        if back_plot == True:
            if centroid_plot==True:
                m1 = plt.Circle((centroid[i,0]-x1+plot_size/2.-.5,centroid[i,1]-y1+plot_size/2.-.5),r_out,facecolor='none',edgecolor='cyan')
                m2 = plt.Circle((centroid[i,0]-x1+plot_size/2.-.5,centroid[i,1]-y1+plot_size/2.-.5),r_in,facecolor='none',edgecolor='cyan')
            else:
                m1 = plt.Circle((r_out,r_out),r_out,facecolor='none',edgecolor='cyan')
                m2 = plt.Circle((r_out,r_out),r_in,facecolor='none',edgecolor='cyan')
            plt.figure(1).add_subplot(1,num_plots+1,(i+2)).add_artist(m1)
            plt.figure(1).add_subplot(1,num_plots+1,(i+2)).add_artist(m2)

        if centroid_plot == True:
            m3 = plt.Circle((centroid[i,0]-x1+plot_size/2.-.5,centroid[i,1]-y1+plot_size/2.-.5),.2,facecolor='black',edgecolor='black')
            plt.figure(1).add_subplot(1,num_plots+1,(i+2)).add_artist(m3)
    plt.show()
