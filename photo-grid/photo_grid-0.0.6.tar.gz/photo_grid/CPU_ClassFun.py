def get_peak(img, map, n_smooth=50, axis=0):
    '''
    '''
    from scipy.signal import find_peaks
    import numpy as np
    # compute signal
    ls_mean = img.mean(axis=(not axis)*1) # 0:nrow
    # gaussian smooth signal
    for i in range(n_smooth):
        ls_mean = np.convolve(np.array([1, 2, 4, 2, 1])/10, ls_mean, mode='same')
    peaks, _ = find_peaks(ls_mean)
    if map is not None:
        if len(peaks) > map.shape[axis]:
            while len(peaks) > map.shape[axis]:
                ls_diff = [peaks[i+1]-peaks[i] for i in range(len(peaks)-1)]
                idx_diff = np.argmin(ls_diff)
                idx_kick = idx_diff if (ls_mean[peaks[idx_diff]] < ls_mean[peaks[idx_diff+1]]) else (idx_diff+1)
                peaks = np.delete(peaks, idx_kick)
        elif len(peaks) < map.shape[axis]:
            while len(peaks) < map.shape[axis]:
                ls_diff = [peaks[i+1]-peaks[i] for i in range(len(peaks)-1)]
                idx_diff = np.argmax(ls_diff)
                peak_insert = (peaks[idx_diff]+peaks[idx_diff+1])/2
                peaks = np.sort(np.append(peaks, int(peak_insert)))
    return peaks, ls_mean

def read_jpg(filename):
    import numpy as np
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = 1e+9
    img = np.array(Image.open(filename)).astype(np.uint8)
    return img

def read_tiff(filename, bands=None, xBSize=5000, yBSize=5000):
    '''import'''
    import gdal
    import numpy as np
    from tqdm import tqdm_gui
    '''program'''
    ds = gdal.Open(filename)
    gdal.UseExceptions()
    nrow = ds.RasterYSize
    ncol = ds.RasterXSize
    if bands==None:
        bands = range(ds.RasterCount)
    data = np.zeros((nrow, ncol, len(bands)))
    for b in bands:
        band = ds.GetRasterBand(b+1)
        for i in tqdm_gui(range(0, nrow, yBSize), desc="Channel %d/%d"%(b, len(bands)-1), leave=False):
            if i + yBSize < nrow:
                numRows = yBSize
            else:
                numRows = nrow - i
            for j in range(0, ncol, xBSize):
                if j + xBSize < ncol:
                    numCols = xBSize
                else:
                    numCols = ncol - j
                data[i:(i+numRows), j:(j+numCols), b] = band.ReadAsArray(j, i, numCols, numRows)
    return data.astype(np.uint8)

def write_tiff(array, outname):
    driver = gdal.GetDriverByName("GTiff")
    out_info = driver.Create(outname+".tif",
                   array.shape[1], # x
                   array.shape[0], # y
                   array.shape[2], # channels
                   gdal.GDT_Byte)
    for i in range(array.shape[2]):
        out_info.GetRasterBand(i+1).WriteArray(array[:,:,i])
