from ..base import FitsFile, HDFFile, DataFile, YamlFile, FileValidationError


class NOfZFile(HDFFile):
    # Must have at least one bin in
    required_datasets = ['n_of_z/z', 'n_of_z/bin_0']

    def validate(self):
        super().validate()
        # Check that 
        nbin = self.get_nbin()


        for b in range(nbin):
            col_name = 'bin_{}'.format(b)
            if not col_name in self.file['n_of_z']:
                raise FileValidationError(f"Expected to find {nbin} bins in NOfZFile but was missing at least {col_name}")

    def get_nbin(self):
        return self.file['n_of_z'].attrs['nbin']

    def get_n_of_z(self, bin_index):
        group = self.file['n_of_z']
        z = group['z'][:]
        nz = group[f'bin_{bin_index}'][:]
        return (z, nz)

    def get_n_of_z_spline(self, bin_index, kind='cubic', **kwargs):
        import scipy.interpolate
        z, nz = self.get_n_of_z(bin_index)
        spline = scipy.interpolate.interp1d(z, nz, kind=kind, **kwargs)
        return spline

    def save_plot(self, filename, **fig_kw):
        import matplotlib.pyplot as plt
        plt.figure(**fig_kw)
        self.plot()
        plt.legend()
        plt.savefig(filename)
        plt.close()

    def plot(self):
        import matplotlib.pyplot as plt
        for b in range(self.get_nbin()):
            z, nz = self.get_n_of_z(b)
            plt.plot(z, nz, label=f'Bin {b}')
