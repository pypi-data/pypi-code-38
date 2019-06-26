import autofit as af
from autolens.data import simulated_ccd
from autolens.data import ccd
from autolens.data.array import grids
from autolens.lens import ray_tracing
from autolens.data.plotters import ccd_plotters


class Instrument(object):

    def __init__(self, shape, pixel_scale, psf, exposure_time, background_sky_level):
        """A classs representing a type of observation, for example the shape of the image, the pixel scale,
        psf, exposure time, etc.

        Parameters
        ----------
        shape : (int, int)
            The shape of the observation. Note that we do not simulate a full CCD frame (e.g. 2000 x 2000 pixels for \
            Hubble imaging), but instead just a cut-out around the strong lens.
        pixel_scale : float
            The size of each pixel in arc seconds.
        psf : PSF
            An array describing the PSF kernel of the image.
        exposure_time : float
            The exposure time of an observation using this instrument.
        background_sky_level : float
            The level of the background sky of an observationg using this instrument.
        """
        self.shape = shape
        self.pixel_scale = pixel_scale
        self.psf = psf
        self.exposure_time = exposure_time
        self.background_sky_level = background_sky_level

    def simulate_ccd_data_from_lens_and_source_galaxy(self, lens_galaxies, source_galaxies, sub_grid_size=16,
                                                      add_noise=True, noise_if_add_noise_false=0.1, noise_seed=-1,
                                                      should_plot_ccd_data=False):
        """Simulate CCD data for this instrument, as follows:

        1)  Setup the image-plane grid stack of the CCD array, which defines the coordinates used for the ray-tracing.

        2) Use this grid and the lens and source galaxies to setup a tracer, which generates the image-plane image of \
           the simulated CCD data.

        3) Simulate the CCD data, using a special image-plane image which ensures edge-effects don't
           degrade simulation of the telescope optics (e.g. the PSF convolution).

        4) Plot the image using Matplotlib, if the plot_ccd bool is True.

        5) Output the data to .fits format if a data_path and data_name are specified. Otherwise, return the simulated \
           ccd data instance."""

        image_plane_grid_stack = grids.GridStack.grid_stack_for_simulation(
            shape=self.shape, pixel_scale=self.psf.pixel_scale, psf_shape=self.psf.shape, sub_grid_size=sub_grid_size)

        tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=lens_galaxies, source_galaxies=source_galaxies,
                                                     image_plane_grid_stack=image_plane_grid_stack)

        simulated_ccd_data = simulated_ccd.SimulatedCCDData.from_image_and_exposure_arrays(
            image=tracer.profile_image_plane_image_2d_for_simulation, pixel_scale=self.pixel_scale,
            exposure_time=self.exposure_time,psf=self.psf, background_sky_level=self.background_sky_level,
            add_noise=add_noise, noise_if_add_noise_false=noise_if_add_noise_false, noise_seed=noise_seed)

        if should_plot_ccd_data:
            ccd_plotters.plot_ccd_subplot(ccd_data=simulated_ccd_data)

        return simulated_ccd_data

    def simulate_ccd_data_from_lens_and_source_galaxy_and_write_to_fits(self, lens_galaxies, source_galaxies,
                                                                        data_path, data_name, sub_grid_size=16,
                                                                        add_noise=True, noise_if_add_noise_false=0.1,
                                                                        noise_seed=-1, should_plot_ccd_data=False):
        """Simulate CCD data for this instrument, as follows:

        1)  Setup the image-plane grid stack of the CCD array, which defines the coordinates used for the ray-tracing.

        2) Use this grid and the lens and source galaxies to setup a tracer, which generates the image-plane image of \
           the simulated CCD data.

        3) Simulate the CCD data, using a special image-plane image which ensures edge-effects don't
           degrade simulation of the telescope optics (e.g. the PSF convolution).

        4) Plot the image using Matplotlib, if the plot_ccd bool is True.

        5) Output the data to .fits format if a data_path and data_name are specified. Otherwise, return the simulated \
           ccd data instance."""

        simulated_ccd_data = self.simulate_ccd_data_from_lens_and_source_galaxy(
            lens_galaxies=lens_galaxies, source_galaxies=source_galaxies, sub_grid_size=sub_grid_size,
            add_noise=add_noise, noise_if_add_noise_false=noise_if_add_noise_false,  noise_seed=noise_seed,
            should_plot_ccd_data=should_plot_ccd_data)

        data_output_path = \
            af.path_util.make_and_return_path_from_path_and_folder_names(path=data_path, folder_names=[data_name])

        ccd.output_ccd_data_to_fits(ccd_data=simulated_ccd_data,
                                    image_path=data_output_path + 'image.fits',
                                    psf_path=data_output_path + 'psf.fits',
                                    noise_map_path=data_output_path + 'noise_map.fits',
                                    exposure_time_map_path=data_output_path + 'exposure_time_map.fits',
                                    background_noise_map_path=data_output_path + 'background_noise_map.fits',
                                    poisson_noise_map_path=data_output_path + 'poisson_noise_map.fits',
                                    background_sky_map_path=data_output_path + 'background_sky_map.fits',
                                    overwrite=True)

    @classmethod
    def lsst(cls, shape=(101, 101), pixel_scale=0.2, psf_shape=(31,31), psf_sigma=0.5, exposure_time=100.0,
             background_sky_level=1.0):
        """Default settings for an observation with the Large Synotpic Survey Telescope.

        This can be customized by over-riding the default input values."""
        psf = ccd.PSF.from_gaussian(shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale)
        return Instrument(shape=shape, pixel_scale=pixel_scale, psf=psf, exposure_time=exposure_time,
                          background_sky_level=background_sky_level)

    @classmethod
    def euclid(cls, shape=(151, 151), pixel_scale=0.1, psf_shape=(31,31), psf_sigma=0.1, exposure_time=565.0,
               background_sky_level=1.):
        """Default settings for an observation with the Euclid space satellite.

        This can be customized by over-riding the default input values."""
        psf = ccd.PSF.from_gaussian(shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale)
        return Instrument(shape=shape, pixel_scale=pixel_scale, psf=psf, exposure_time=exposure_time,
                          background_sky_level=background_sky_level)

    @classmethod
    def hst(cls, shape=(251, 251), pixel_scale=0.05, psf_shape=(31,31), psf_sigma=0.05, exposure_time=2000.0,
            background_sky_level=1.0):
        """Default settings for an observation with the Hubble Space Telescope.

        This can be customized by over-riding the default input values."""
        psf = ccd.PSF.from_gaussian(shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale)
        return Instrument(shape=shape, pixel_scale=pixel_scale, psf=psf, exposure_time=exposure_time,
                          background_sky_level=background_sky_level)

    @classmethod
    def hst_up_sampled(cls, shape=(401, 401), pixel_scale=0.03, psf_shape=(31,31), psf_sigma=0.05,
                       exposure_time=2000.0, background_sky_level=1.0):
        """Default settings for an observation with the Hubble Space Telescope which has been upscaled to a higher \
        pixel-scale to better sample the PSF.

        This can be customized by over-riding the default input values."""
        psf = ccd.PSF.from_gaussian(shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale)
        return Instrument(shape=shape, pixel_scale=pixel_scale, psf=psf, exposure_time=exposure_time,
                          background_sky_level=background_sky_level)
    @classmethod
    def keck_adaptive_optics(cls, shape=(751, 751), pixel_scale=0.01, psf_shape=(31, 31), psf_sigma=0.025,
                             exposure_time=1000.0, background_sky_level=1.0):
        """Default settings for an observation using Keck Adaptive Optics imaging.

        This can be customized by over-riding the default input values."""
        psf = ccd.PSF.from_gaussian(shape=psf_shape, sigma=psf_sigma, pixel_scale=pixel_scale)
        return Instrument(shape=shape, pixel_scale=pixel_scale, psf=psf, exposure_time=exposure_time,
                          background_sky_level=background_sky_level)