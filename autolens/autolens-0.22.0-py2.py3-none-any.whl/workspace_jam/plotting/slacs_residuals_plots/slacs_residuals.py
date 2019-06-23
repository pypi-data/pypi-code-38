from autolens.data.array.util import array_util
from autolens.data.array import scaled_array
from autolens.plotters import array_plotters

import os

path = '{}/'.format(os.path.dirname(os.path.realpath(__file__)))

lens_name = 'SLACSJ0252+0039'
lens_name = 'SLACSJ1250+0523'
# lens_name = 'SLACSJ1430+4105'

resi = array_util.numpy_array_2d_from_fits(file_path=path + '../data/slacs/slacs1250+0523/F814W_image.fits', hdu=0)
resi = scaled_array.ScaledSquarePixelArray(array=resi, pixel_scale=0.03)
resi = resi.resized_scaled_array_from_array(new_shape=(201, 201))
# resi = np.flipud(resi)
array_plotters.plot_array(array=resi, norm='log', norm_min=0.0, norm_max=1.0, title='Observed CCD',
                          output_path=path+'slacs_residuals_output/', output_filename=lens_name+'_Obs', output_format='png')

resi = array_util.numpy_array_2d_from_fits(file_path=path + 'slacs_residuals/' + lens_name + '_Decomp_Mass_x1Sersic.fits', hdu=0)
resi = scaled_array.ScaledSquarePixelArray(array=resi, pixel_scale=0.03)
resi = resi.resized_scaled_array_from_array(new_shape=(201, 201))
# resi = np.flipud(resi)
array_plotters.plot_array(array=resi, norm='symmetric_log', norm_min=-0.1, norm_max=0.1, linthresh=0.0005, linscale=0.01,
                          title='CCD Residuals (Sersic)',
                          output_path=path+'slacs_residuals_output/', output_filename=lens_name+'_x1Sersic', output_format='png')

resi = array_util.numpy_array_2d_from_fits(
    file_path=path + 'slacs_residuals/' + lens_name + '_Decomp_Mass_x2SersicOffset.fits', hdu=0)
resi = scaled_array.ScaledSquarePixelArray(array=resi, pixel_scale=0.03)
resi = resi.resized_scaled_array_from_array(new_shape=(201, 201))
# resi = np.flipud(resi)
array_plotters.plot_array(array=resi, norm='symmetric_log', norm_min=-0.1, norm_max=0.1, linthresh=0.0005, linscale=0.01,
                          title='CCD Residuals (Sersic + Exp)',
                          output_path=path + 'slacs_residuals_output/', output_filename=lens_name + '_x2Sersic', output_format='png')

# Put in array plotters

# cb = plt.colorbar(fraction=cb_fraction, pad=cb_pad, ticks=[0.1, 0.05, 0.01, 0.001, 0.0, -0.001, -0.01, -0.05, -0.1])
# cb.ax.tick_params(labelsize=cb_ticksize)
# cb.ax.set_yticklabels(['< -0.1', '0.05', '0.01', '0.001', '0.0', '-0.001', '-0.01', '-0.05', '> 0.0'])