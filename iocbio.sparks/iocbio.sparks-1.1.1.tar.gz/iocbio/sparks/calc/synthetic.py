# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#
import uuid
import hashlib
import numpy as np
from scipy import mgrid, ndimage

from iocbio.sparks.io.export import image_export


class SyntheticSpark(object):

    def __init__(self, dx, dt, time_half_raise, time_half_decay, space_half_width):
        """
        Generates synthetic spark

        Parameters:
            dx : pixel size in space in microns
            dt : pixel size in time in milliseconds
            time_half_raise: spark half raise time in milliseconds
            time_half_decay: spark half decay time in milliseconds
            space_half_width: spark half width in space in microns
        """
        self.dx = dx
        self.dt = dt
        self.traise = time_half_raise
        self.tdecay = time_half_decay
        self.swidth = space_half_width
        self.generate_spark()

        if 0: # For testing
            spark = self.spark
            mx0, my0 = self.spark_mx0, self.spark_my0

            fig = plt.figure()
            ax1 = fig.add_subplot(221)
            ax2 = fig.add_subplot(223)
            ax3 = fig.add_subplot(222)

            ax1.imshow(spark, interpolation='nearest')

            t = self.dt*np.arange(0, spark.shape[1])
            ax2.plot(t-t[my0], spark[spark.shape[0]//2,:])
            ax2.grid()

            x = self.dx*np.arange(0, spark.shape[0])
            ax3.plot(x-x[mx0], spark[:, int(np.ceil(4*self.traise/self.dt))])
            ax3.grid()
            plt.show()

    def generate_spark(self):
        sx = int(np.ceil(4*self.swidth/self.dx))
        h = [self.traise/self.dt, self.tdecay/self.dt]
        syL, syR = int(np.ceil(4*self.traise/self.dt)), int(np.ceil(4*self.tdecay/self.dt))
        syL, syR = [int(np.ceil(4*p)) for p in h]
        tau_yL, tau_yR = h
        tau_x = [self.swidth/self.dx]
        X, Y =  mgrid[-sx:sx+1, -syL:syR+1]
        spark = np.zeros(X.shape)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                x, y = X[i,j], Y[i,j]
                # spark[i,j] = 2**-((x/tau_x)**2 + (y/float(tau_yL if y < 0 else tau_yR))**2)
                spark[i,j] = np.exp(np.log(0.5) * ((x/tau_x)**2 + (y/float(tau_yL if y < 0 else tau_yR))**2))

        self.spark = spark
        self.spark_mx0, self.spark_my0 = ndimage.maximum_position(spark)


class SyntheticData(object):
    database_table = 'ground_truth_spark'

    @staticmethod
    def database_schema(db):
        db.query("CREATE TABLE IF NOT EXISTS " + db.table(SyntheticData.database_table) +
                 "(experiment_id text, spark_id text not null PRIMARY KEY, " +
                 "xm integer, ym integer, amplitude DOUBLE PRECISION, " +
                 "time_half_raise DOUBLE PRECISION, time_half_decay DOUBLE PRECISION, space_half_width DOUBLE PRECISION)")

    @staticmethod
    def calculate_nsparks(lx, lt, dx, dt, freq):
        """ Calculates number of sparks for given spark frequency
        Parameters:
            lx : experiment sizes in space in pixels
            lt : experiment sizes time in pixels
            dx : pixel size in space in microns
            dt : pixel size in time in milliseconds
            freq: sparks frequency in sparks per 100 microns per 1 second
        Returns:
            int: Number of sparks
        """
        return int(np.round((lx*dx*1.e-2)*(lt*dt*1.e-3) * freq, 0))

    @staticmethod
    def calculate_spark_freq(lx, lt, dx, dt, nsparks):
        """ Calculates number of sparks for given spark frequency
        Parameters:
            lx : experiment sizes in space in pixels
            lt : experiment sizes time in pixels
            dx : pixel size in space in microns
            dt : pixel size in time in milliseconds
            nsparks: number of sparks
        Returns:
            float: sparks frequency in sparks per 100 microns per 1 second
        """
        return nsparks / (lx*dx*1.e-2)*(lt*dt*1.e-3)

    def __init__(self, lenx, lent, dx, dt, f0, f_f0, time_half_raise=7.0, time_half_decay=18.0,
                 space_half_width=1.5, gain=None, offset=0):
        """
        Generates synthetic experiment

        Parameters:
            lenx : experiment sizes in space in pixels
            lent :  experiment sizes time in pixels
            dx : pixel size in space in microns
            dt : pixel size in time in milliseconds
            f0 : (float or int) fluorescence background
            f_f0 : (list or float or int) spark relative amplitude(s) respect to f0
            time_half_raise: spark half raise time in milliseconds
            time_half_decay: spark half decay time in milliseconds
            space_half_width: spark half width in space in microns
            gain : (float) gain of data (multiplicative)
            offset : (float) offset of data (additive)
        """

        self.lenx = lenx
        self.lent = lent
        self.dx = dx
        self.dt = dt
        self.traise = time_half_raise
        self.tdecay = time_half_decay
        self.swidth = space_half_width
        self.f0 = f0
        self.f_f0 = f_f0
        self.gain = gain
        self.offset = offset
        self.nsparks = None
        self.spark_freq = None
        self.data = None
        self.experiment_id = None
        self.data_stats = {}

    def generate_data(self, spark_freq=None, nsparks=None):
        if spark_freq is None and nsparks is None:
            print('Spark frequency is set to 1 spark per 100 micron per 1 second')
            self.spark_freq = 1
            self.nsparks = self.calculate_nsparks(self.lenx, self.lent, self.dx, self.dt, self.spark_freq)

        if spark_freq is not None:
            self.spark_freq = spark_freq
            self.nsparks = self.calculate_nsparks(self.lenx, self.lent, self.dx, self.dt, self.spark_freq)

        if spark_freq is None and nsparks is not None:
            self.nsparks = nsparks
            self.nsparks = calculate_spark_freq(self.lenx, self.lent, self.dx, self.dt, self.nsparks)

        sp = SyntheticSpark(self.dx, self.dt, self.traise, self.tdecay, self.swidth)

        self.data = self.f0*np.ones((self.lenx, self.lent), dtype=np.float)

        sp_sizex, sp_sizet = sp.spark.shape

        i_s = np.random.randint(sp_sizex, self.lenx-sp_sizex, size=(self.nsparks,), dtype=np.int32)
        j_s = np.random.randint(sp_sizet, self.lent-sp_sizet, size=(self.nsparks,), dtype=np.int32)

        if isinstance(self.f_f0, list):
            if len(self.f_f0) > self.nsparks:
                sp_mxs = self.f0*np.array(self.f_f0[:self.nsparks])
            else:
                nf = len(self.f_f0)
                sp_mxs = self.f0*np.array([self.f_f0[i%nf] for i in range(self.nsparks)])

        elif isinstance(self.f_f0, (float, int)):
            sp_mxs = self.f0*self.f_f0*np.ones((self.nsparks,))
        else:
            raise ValueError('f_f0 can be `list`, `float`, or `int` type %s is not supported.' % type(self.f_f0))

        np.random.shuffle(sp_mxs)

        if self.gain is None:
            a = self.f0 + sp_mxs.max()
            self.gain = (255-self.offset) / (a + 5*np.sqrt(a))

        for i, j, mx in zip(i_s, j_s, sp_mxs):
            self.data[i:i+sp_sizex, j:j+sp_sizet] += mx*sp.spark
            self.data_stats[str(uuid.uuid4())] = {
                'xm': int(j + sp.spark_my0),
                'ym': int(i + sp.spark_mx0),
                'amplitude': self.gain*mx,
                'time_half_raise': self.traise,
                'time_half_decay': self.tdecay,
                'space_half_width': self.swidth,
            }

        # self._data = self.data
        self.data = self.gain*np.random.poisson(self.data)+self.offset
        if self.data.max() > 255:
            print('Cannot convert synthetic image to uint8. Maximum value: %.f exceeds 255. ' +
                  'Consider changing function `synthetic_data` arguments. ' +
                  'Setting all pixel values > 255 to 255' % self.data.max())
            self.data[self.data>255] = 255

        self.data = self.data.astype(np.uint8)
        self.experiment_id = hashlib.sha256(self.data.tostring()).hexdigest()

    def update_database(self, database):
        for k, d in self.data_stats.items():
            database.query("INSERT INTO " + database.table(SyntheticData.database_table) +
                           "(experiment_id, spark_id, xm, ym, amplitude, time_half_raise, time_half_decay, space_half_width) " +
                           "VALUES (:eid, :sid, :xm, :ym, :amplitude, :time_half_raise, :time_half_decay, :space_half_width)",
                           eid=self.experiment_id, sid=k,
                           xm=d['xm'], ym=d['ym'], amplitude=d['amplitude'], time_half_raise=d['time_half_raise'],
                           time_half_decay=d['time_half_decay'], space_half_width=d['space_half_width'])

    def save_image(self, filename):
        image_export(self.data.T, filename)
        # image_export(self._data.T, filename+'gt.tiff')
