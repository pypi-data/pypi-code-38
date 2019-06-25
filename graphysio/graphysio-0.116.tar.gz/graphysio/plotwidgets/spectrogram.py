import numpy as np
import pandas as pd

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

class SpectroTimeAxisItem(pg.AxisItem):
    def __init__(self, initvalue, samplerate, chunksize, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initvalue = initvalue / 1e6   # ns to ms
        self.samplerate = samplerate
        self.chunksize = chunksize

    def tickStrings(self, values, scale, spacing):
        ret = []
        for value in values:
            value = 1e3*value # s to ms
            value = value * self.chunksize / self.samplerate + self.initvalue
            date = QtCore.QDateTime.fromMSecsSinceEpoch(value)
            date = date.toTimeSpec(QtCore.Qt.UTC)
            datestr = date.toString("dd/MM/yyyy\nhh:mm:ss.zzz")
            ret.append(datestr)
        return ret

#To set:
# chunksize
# levels
# color gradient
class SpectrogramWidget(pg.PlotWidget):
    def __init__(self, series, Fs, s_chunklen, parent=None):
        # s_chunklen in seconds
        self.fs = Fs
        self.data = series.values
        self.chunksize = int(s_chunklen * Fs)
        self.win = np.hanning(self.chunksize)

        axisItem = SpectroTimeAxisItem(
            initvalue = series.index[0],
            samplerate = Fs,
            chunksize = self.chunksize,
            orientation = 'bottom'
        )
        axisItems = {'bottom': axisItem}
        super().__init__(parent=parent, axisItems=axisItems)

        self.img = pg.ImageItem()
        self.addItem(self.img)

        # bipolar colormap
        pos = np.array([0., 0.25, 0.5, 0.75, 1.])
        color = np.array([[0, 0, 0, 255]
                         ,[0, 0, 255, 255]
                         ,[0, 255, 255, 255]
                         ,[255, 255, 0, 255]
                         ,[255, 0, 0, 255]
                         ], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        self.img.setLookupTable(lut)

        # TODO: Make adjustable
        self.img.setLevels([-10,10])

        self.img.scale(1, self.fs / self.chunksize)

        self.setLabel('left', 'Frequency', units='Hz')
        self.render()

    def render(self):
        nsplit = int(len(self.data) / self.chunksize)
        chunks = self.data[0:nsplit*self.chunksize]
        chunks = np.split(chunks, nsplit)
        chunks = np.vstack(chunks)

        # normalized, windowed frequencies in data chunk
        spec = np.fft.rfft(chunks*self.win) / self.chunksize

        # get magnitude 
        psd = np.real(spec)

        # convert to dB scale
        psd = 20 * np.log10(psd)

        psdnona = psd[~np.isnan(psd)]
        hi = np.percentile(psdnona, 95)
        lo = np.percentile(psdnona, 5)
        self.img.setLevels([lo,hi])
        self.img.setImage(psd, autoLevels=False)

    @property
    def menu(self):
        return {}
