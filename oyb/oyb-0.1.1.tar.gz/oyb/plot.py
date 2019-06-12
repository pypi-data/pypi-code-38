"""Contains various plotting methods (both main plot functions and their
   specific rendering and annotation behaviors) for Orbit-derived objects in 2d
   (i.e., ground track) and 3d (i.e., orbital) plots.
"""

import numpy
from math import pi
from mpl_toolkits import mplot3d
from matplotlib import pyplot, image
from oyb import earth, data

def plot2d(o, r=None, hx=None):
    """Plots the given orbit for one period in a 2d ground track. Can
       alternatively use a predetermined ephermide (latitude, longitude,
       altitude, as formatted in a [3xn] numpy array). If an axis handle (hx) is
       provided, will add the ground track to the given plot; otherwise, a new
       figure will be created and the axis returned.
    """
    if r is None:
        r = o.track()
    if hx is None:
        hf = pyplot.figure()
        hx = hf.add_subplot(111)
        plotEarthSurf(hx)
        annotateEarthSurf(hx)
    lat_deg = r[:,0] * 180/pi
    lon_deg = r[:,1] * 180/pi
    breaks = numpy.where(abs(numpy.diff(lon_deg)) > 180)[0]
    ni = numpy.append(numpy.array([0]), breaks + 1)
    l0 = None
    for ndx, n0 in enumerate(ni):
        nf = ni[ndx+1] if ndx < len(ni) - 1 else r.shape[0]
        x = lon_deg[n0:nf]
        y = lat_deg[n0:nf]
        if ndx > 0:
            if x[0] < 0:
                dx = numpy.array([lon_deg[n0-1] - 360])
            else:
                dx = numpy.array([lon_deg[n0-1] + 360])
            dy = numpy.array([lat_deg[n0-1]])
            x = numpy.append(dx, x)
            y = numpy.append(dy, y)
        if ndx < len(ni) - 1:
            if x[-1] < 0:
                dx = numpy.array([lon_deg[nf] - 360])
            else:
                dx = numpy.array([lon_deg[nf] + 360])
            dy = numpy.array([lat_deg[nf]])
            x = numpy.append(x, dx)
            y = numpy.append(y, dy)
        if l0 is None:
            l0 = hx.plot(x, y)
        else:
            hx.plot(x, y, color=l0[0].get_color())
    hx.set_xlim((-180,180))
    hx.set_ylim((-90,90))
    return hx
        
def plotEarthSurf(hx):
    """Creates a new 2d earth surface plot, with a Blue Marble image in the
       background and scaled to (-180,180) degrees longitude on the x axis and
       (-90,90) degrees latitude on the y axis.
    """
    img = image.imread(data.get_path('blueMarble.png'))
    hx.imshow(img, aspect='equal', origin='upper', extent=(-180,180,-90,90), alpha=0.2)
    
def annotateEarthSurf(hx):
    """Annotates the given earth surface axis with axis labels and a dashed line
       along the equator.
    """
    hx.set_xlabel('Longitude [deg]')
    hx.set_ylabel('Latitude [deg]')
    hx.plot([-180,180], [0,0], '--', color=(0.5,0.5,0.5))
    
def plot3d(o, r=None, hx=None):
    """Plots the given orbit for one period in a 3d volume of earth-centered
       space. Can alternatively use a predetermined ephermide (XYZ [meters] in
       ECI, as formatted in a [3xn] numpy array). If an axis handle (hx) is
       provided, will add the orbit to the given plot; otherwise, a new figure
       will be created and the axis returned.
    """
    if r is None:
        r = 1e-3 * o.propagate()
    if hx is None:
        hf = pyplot.figure()
        hx = hf.add_subplot(111, projection='3d')
        plotEarthSphere(hx)
        annotateEarthSphere(hx)
    hx.plot(r[:,0], r[:,1], r[:,2])
    lim = (
        min(min(r[:,0]), min(r[:,1]), min(r[:,2])),
        max(max(r[:,0]), max(r[:,1]), max(r[:,2])) )
    hx.plot([0,lim[0]], [0,0], [0,0], c=(0.6,0.6,0.6,0.2))
    hx.plot([0,lim[1]], [0,0], [0,0], c=(1.0,0.0,0.0,0.2))
    hx.plot([0,0], [0,lim[0]], [0,0], c=(0.6,0.6,0.6,0.2))
    hx.plot([0,0], [0,lim[1]], [0,0], c=(0.0,1.0,0.0,0.2))
    hx.plot([0,0], [0,0], [0,lim[0]], c=(0.6,0.6,0.6,0.2))
    hx.plot([0,0], [0,0], [0,lim[1]], c=(0.0,0.0,1.0,0.2))
    return hx

def plotEarthSphere(hx):
    """Renders a 3d wireframe of the earth at the center of the given plot axis.
    """
    u, v = numpy.mgrid[0:2*numpy.pi:20j, 0:numpy.pi:10j]
    x = numpy.cos(u) * numpy.sin(v)
    y = numpy.sin(u) * numpy.sin(v)
    z = numpy.cos(v)
    r = 1e-3 * earth.eqRad_m
    hx.plot_wireframe(r * x, r * y, r * z, color=(0.5,0.5,0.5,0.5))

def annotateEarthSphere(hx):
    """Adds axis labels to the given 3d orbit plot axis.
    """
    hx.set_xlabel('X ECI [km]')
    hx.set_ylabel('Y ECI [km]')
    hx.set_zlabel('Z ECI [km]')
