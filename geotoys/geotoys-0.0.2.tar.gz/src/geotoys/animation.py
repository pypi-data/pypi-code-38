def video(path_data, product_ids, fp_output):
    """Create movie from plotting function that iterates over files (e.g. jpeg images)

    References
    ==========
    https://matplotlib.org/examples/animation/moviewriter.html
    https://stackoverflow.com/a/12470959/943773
    """
    import numpy
    import matplotlib.pyplot as plt
    import matplotlib
    import cartopy.crs as ccrs
    import matplotlib

    matplotlib.use("Agg")

    from congo.ingest import product_img_bands, stack_bands, true_color, normalize

    FFMpegWriter = matplotlib.animation.writers["mencoder"]
    metadata = dict(title="Movie Test", artist="Matplotlib",
                    comment="Movie support!")
    writer = FFMpegWriter(fps=15, metadata=metadata)

    ax1 = plt.subplot(121, frameon=False, projection=ccrs.PlateCarree())
    ax2 = plt.subplot(122, frameon=False)

    # Read first image as example
    bands, profile = product_img_bands(path_data, product_id[0], res="10m",
                                             img_type="false_color_infared")

    # Make RGB image plot with empty data (3,n,n)
    bands_zero = numpy.zeros_like(bands)
    x0,y0 = profile['transform']*(0,0)
    x1,y1 = profile['transform']*(profile['width'], profile['height'])
    extent = (x0, x1, y0, y1)
    img = ax1.imshow(bands_zero, transform=profile['crs'], extent=extent, origin="upper")
    ax1.coastlines(resolution="10m")

    # TODO blank histo
    #data = [[]*256, []*256, []*256]
    #hist = ax2.

    # Write frame for each product
    with writer.saving(fig, fp_output, dpi=100):
        for i, product_id in enumerate(product_ids):
            bands, profile = product_img_bands(path_data, product_id, res="10m",
                                             img_type="false_color_infared")
            img.set_data(stack_bands(bands))
            img.autoscale() # or img.set_clim(vmin, vmax)
            writer.grab_frame()


def save_plots(path_data, product_ids, fp_output):
    """Create movie from plotting function that iterates over files (e.g. jpeg images)

    References
    ==========
    https://matplotlib.org/examples/animation/moviewriter.html
    https://stackoverflow.com/a/12470959/943773
    """
    import numpy
    import matplotlib.pyplot as plt
    import matplotlib
    import cartopy.crs as ccrs
    import matplotlib
    import pyepsg # needed by ccrs.epsg

    matplotlib.use("Agg")

    from congo.ingest import product_img_bands, stack_bands, true_color, normalize

    # TODO blank histo
    #data = [[]*256, []*256, []*256]
    #hist = ax2.

    # Write frame for each product
    for i, product_id in enumerate(product_ids):

        ax1 = plt.subplot(121, frameon=False, projection=ccrs.PlateCarree())
        ax2 = plt.subplot(122, frameon=False)

        bands, profile = product_img_bands(path_data, product_id, res="10m",
                                         img_type="false_color_infrared")

        # Make RGB image plot with empty data (3,n,n)
        x0,y0 = profile['transform']*(0,0)
        x1,y1 = profile['transform']*(profile['width'], profile['height'])
        extent = (x0, x1, y0, y1)

        crs = ccrs.epsg(profile['crs'].to_epsg())

        bands = stack_bands([normalize(true_color(b), 0, 256) for b in bands])
        ax1.imshow(bands, transform=crs, extent=extent, origin="upper")

        #ax1.coastlines(resolution="10m")
