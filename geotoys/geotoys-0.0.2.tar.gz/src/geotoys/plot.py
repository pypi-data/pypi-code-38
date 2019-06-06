"""
Methods for generating simple plots of data from NetCDF and GeoTIFF data
"""

def plot_polys(ax, geoms, **kwargs):
    from descartes import PolygonPatch
    from matplotlib.collections import PatchCollection

    # TODO add color gradient arg, linear over values in list == len geoms
    collection = PatchCollection([PolygonPatch(geom, **kwargs) for geom in geoms])
    ax.add_collection(collection)
    return ax


def plot_poly(geom, **kwargs):
    from descartes import PolygonPatch

    ax.add_patch(PolygonPatch(geom, **kwargs))
    return ax


# TODO check that iterates first of multiple scenes in tiff if present
def add_geotiff_ax(ax, fp, band_ind, ix_t, crs):
    """
    Add a projected GeoTIFF raster to the Axes instance
    """
    import rasterio

    src = rasterio.open(fp)

    extent = (src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top)
    for ix_b in band_ind:
        ax.imshow(src.read(ix_b)[ix_t], transform=crs, extent=extent, origin="upper")

    return ax


def add_netcdf_ax(ax, fp, var_name, ix_t, crs):
    """
    Add a projected plot of the first timestep in a NetCDF to the Axes instance
    """
    import netCDF4

    nc = netCDF4.Dataset(fp)

    var = nc[var_name][ix_t,:,:]
    lons, lats = get_lons_lats(nc)

    ax.contourf(lons, lats, var, 60, transform=crs)

    return ax


def quickplot(fp, band, crs=None, coast_res="50m"):
    """
    Generate a projected plot the first timestep of data for a NetCDF or GeoTIFF file
    """
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import os

    ext = os.path.splitext(fp)[1]

    # Set plotting function
    if "nc" in ext:
        plt_func = add_netcdf_ax
    elif "tif" in ext:
        plt_func = add_geotiff_ax
    else:
        raise ValueError(f"File extensions {ext} not recognized")

    # Set CRS
    if crs is None:
        crs = ccrs.PlateCarree()

    ax = plt.axes(projection=crs)
    ax = plt_func(ax, fp, band, 0, crs)
    ax.coastlines(resolution=coast_res, color="black", linewidth=1)

    plt.show()


def get_plottables(src, bands=None):
    """
    Get georeferenced image information for plotting using imshow
    """
    import cartopy.crs as ccrs
    import numpy

    x0,y0 = src.profile['transform']*(0,0)
    x1,y1 = src.profile['transform']*(src.profile['width'], src.profile['height'])
    extent = (x0, x1, y0, y1)

    if not bands:
        bands = [1,]

    data = numpy.array([src.read(i) for i in bands])
    # TODO automate this
    data = numpy.moveaxis(data, 0, -1)

    # Query online for CRS
    transform = src.profile['crs'].to_epsg()
    if transform is 4326 :
        transform = ccrs.PlateCarree()
    else:
        transform = ccrs.epsg(transform)

    return data, transform, extent


def add_location(ax, name, lon, lat, crs, text_color=None):
    """
    Add a geodesic location to the plot axis
    """
    import matplotlib.patheffects as pe

    xy_point = xy_text = (lon, lat)
    ax.plot(*xy_point, marker='o', markersize=8, color='white')

    color = 'white'
    path_effects = None
    if text_color:
        color = text_color
        ax.plot(*xy_point, marker='o', markersize=4, color=text_color)
        patheffects = [pe.withStroke(linewidth=3.0, foreground='white')]

    ax.annotate(name, xy=xy_text, xycoords=crs._as_mpl_transform(ax),
                color=color, ha='left', va='center',
                path_effects=patheffects
                )
    return ax


def lonlatlines(ax, crs, lats=None, lons=None, alpha=0.5):
    """
    Add longitude and latitude lines to plot axis

    References
    ==========
    https://scitools.org.uk/cartopy/docs/v0.13/matplotlib/gridliner.html
    """
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    import matplotlib.ticker

    gl = ax.gridlines(crs=crs, draw_labels=True,
                      linewidth=1.5, color='#e1e5ed', alpha=0.5, linestyle=':')

    gl.xlabels_top = False
    gl.ylabels_right = False
    #gl.xlines = False
    if lons:
        gl.xlocator = matplotlib.ticker.FixedLocator(lons)
    if lats:
        gl.ylocator = matplotlib.ticker.FixedLocator(lats)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    #gl.xlabel_style = {'size': 15, 'color': 'gray'}
    #gl.xlabel_style = {'color': 'red', 'weight': 'bold'}
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    return ax


# TODO automate data dimensions somehow, log it
def plot_src(data, crs, extent, locations=[], text_color=None, cbar_title='', **kwargs):
    """
    Plot rasterio image with optional locations

    Parameters
    ==========
    data: ndarray (n,n,3)
        Data for the 3 bands to be plotted as RGB
    crs: cartopy.CRS
        Coordinate reference system of data
    extent: tuple of float
        Extent of plot in crs values. (minx, maxx, miny, maxy)
    locations: list of tuple
        Tuples of name, lon, lat for locations to plot points and names of
    text_color: matplotlib color name
        Name of text label color, bordered by white. Defualt is `None`, resulting in
        white text label.
    cbar_title: str
        Title of value colorbar
    **kwargs: dict
        Matplotlib.pyplot.imshow kwargs
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(subplot_kw={'projection':crs})
    img = ax.imshow(data, transform=crs, extent=extent, origin="upper", **kwargs)
    ax = lonlatlines(ax, crs)

    if any(locations):
        for name, lon, lat in locations:
            add_location(ax, name, lon, lat, crs, text_color=text_color)

    cbar = fig.colorbar(img, shrink=0.7, orientation='vertical')
    cbar.ax.set_title(cbar_title)
    plt.show()


def rgb_histogram(ax, fp):
    """Plot a histogram of the RGB bands of common raster images
    """
    import cv2
    import numpy
    import matplotlib.pyplot as plt
    from PIL import Image
    import cartopy.crs as ccrs

    ax1 = plt.subplot(121, frameon=False, projection=ccrs.PlateCarree())
    ax2 = plt.subplot(122, frameon=False)

    with Image.open(fp) as img:
        ax1.imshow(change_contrast(img, 100), origin='upper')

    img = cv2.imread(fp)

    color = ("b","g","r")
    for i,col in enumerate(color):
        histr = cv2.calcHist(
            images=[img],
            channels=[i],
            mask=None,
            histSize=[256],
            ranges=[0,256]
            )

        ax2.plot(histr, color=col)
        ax2.set_xlim([0,256])
        ax2.set_ylabel('Percentage')
        ax2.title.set_text('Band histogram')

    plt.show()

    return ax


def get_src_mask(src):
    #from copy import deepcopy

    #mask = deepcopy(src[0])
    #mask[src[0] >= 251] = 1
    #mask[src[0] < 251] = 0

    #return mask
    raise NotImplementedError


def change_contrast(img, level):
    """
    https://stackoverflow.com/a/42054155/943773
    """
    #factor = (259 * (level + 255)) / (255 * (259 - level))
    #def contrast(c):
    #    value = 128 + factor * (c - 128)
    #    return max(0, min(255, value))
    #return img.point(contrast)
    raise NotImplementedError


def tiff_histogram():
    # TODO https://www.hatarilabs.com/ih-en/sentinel2-images-explotarion-and-processing-with-python-and-rasterio
    raise NotImplementedError
