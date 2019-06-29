from autolens.data import instrument as ins
from autolens.data import simulated_ccd as sim_ccd
from autolens.data import ccd
from autolens.data.array import grids
from autolens.lens import ray_tracing
from autolens.model.galaxy import galaxy as g
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp

import numpy as np
import os
import shutil

test_data_dir = "{}/../test_files/array/".format(os.path.dirname(os.path.realpath(__file__)))

class TestInstrument:

    def test__constructor_and_specific_instrument_class_methods(self):

        psf = ccd.PSF.from_gaussian(shape=(11, 11), sigma=0.1, pixel_scale=0.1)

        instrument = ins.Instrument(shape=(51, 51), pixel_scale=0.1, psf=psf, exposure_time=20.0,
                                       background_sky_level=10.0)

        assert instrument.shape == (51, 51)
        assert instrument.pixel_scale == 0.1
        assert instrument.psf == psf
        assert instrument.exposure_time == 20.0
        assert instrument.background_sky_level == 10.0

        lsst = ins.Instrument.lsst()
        
        lsst_psf = ccd.PSF.from_gaussian(shape=(31, 31), sigma=0.5, pixel_scale=0.2)

        assert lsst.shape == (101, 101)
        assert lsst.pixel_scale == 0.2
        assert lsst.psf == lsst_psf
        assert lsst.exposure_time == 100.0
        assert lsst.background_sky_level == 1.0

        euclid = ins.Instrument.euclid()

        euclid_psf = ccd.PSF.from_gaussian(shape=(31, 31), sigma=0.1, pixel_scale=0.1)

        assert euclid.shape == (151, 151)
        assert euclid.pixel_scale == 0.1
        assert euclid.psf == euclid_psf
        assert euclid.exposure_time == 565.0
        assert euclid.background_sky_level == 1.0

        hst = ins.Instrument.hst()

        hst_psf = ccd.PSF.from_gaussian(shape=(31, 31), sigma=0.05, pixel_scale=0.05)

        assert hst.shape == (251, 251)
        assert hst.pixel_scale == 0.05
        assert hst.psf == hst_psf
        assert hst.exposure_time == 2000.0
        assert hst.background_sky_level == 1.0

        hst_up_sampled = ins.Instrument.hst_up_sampled()

        hst_up_sampled_psf = ccd.PSF.from_gaussian(shape=(31, 31), sigma=0.05, pixel_scale=0.03)

        assert hst_up_sampled.shape == (401, 401)
        assert hst_up_sampled.pixel_scale == 0.03
        assert hst_up_sampled.psf == hst_up_sampled_psf
        assert hst_up_sampled.exposure_time == 2000.0
        assert hst_up_sampled.background_sky_level == 1.0

        adaptive_optics = ins.Instrument.keck_adaptive_optics()

        adaptive_optics_psf = ccd.PSF.from_gaussian(shape=(31, 31), sigma=0.025, pixel_scale=0.01)

        assert adaptive_optics.shape == (751, 751)
        assert adaptive_optics.pixel_scale == 0.01
        assert adaptive_optics.psf == adaptive_optics_psf
        assert adaptive_optics.exposure_time == 1000.0
        assert adaptive_optics.background_sky_level == 1.0
        
    def test__simulate_ccd_data_from_lens_and_source_galaxy__compare_to_manual_ccd_data(self):

        lens_galaxy = g.Galaxy(redshift=0.5, mass=mp.EllipticalIsothermal(centre=(0.0, 0.0), einstein_radius=1.6, axis_ratio=0.7,
                                                            phi=45.0))

        source_galaxy = g.Galaxy(redshift=0.5, light=lp.EllipticalSersic(centre=(0.1, 0.1), axis_ratio=0.8, phi=60.0,
                                                           intensity=0.3, effective_radius=1.0, sersic_index=2.5))

        image_plane_grid_stack = grids.GridStack.grid_stack_for_simulation(shape=(11, 11), pixel_scale=0.2,
                                                                           psf_shape=(7, 7), sub_grid_size=1)

        tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy],
                                                     image_plane_grid_stack=image_plane_grid_stack)

        shape = (11, 11)
        pixel_scale = 0.2
        psf = ccd.PSF.from_gaussian(shape=(7, 7), sigma=0.1, pixel_scale=0.2)
        exposure_time = 100.0
        background_sky_level = 1.0

        simulated_ccd = sim_ccd.SimulatedCCDData.from_image_and_exposure_arrays(image=tracer.profile_image_plane_image_2d_for_simulation, pixel_scale=pixel_scale,
                                                                                exposure_time=exposure_time, psf=psf,
                                                                                background_sky_level=background_sky_level, add_noise=False,
                                                                                noise_if_add_noise_false=0.2)

        instrument = ins.Instrument(shape=shape, pixel_scale=pixel_scale, psf=psf, exposure_time=exposure_time,
                                    background_sky_level=background_sky_level)

        instrument_ccd = instrument.simulate_ccd_data_from_lens_and_source_galaxy(
            lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy], sub_grid_size=1, add_noise=False,
            noise_if_add_noise_false=0.2)

        assert (simulated_ccd.image == instrument_ccd.image).all()
        assert (simulated_ccd.psf == instrument_ccd.psf).all()
        assert (instrument_ccd.noise_map == 0.2*np.ones((11,11)))
        assert simulated_ccd.noise_map == instrument_ccd.noise_map
        assert simulated_ccd.background_noise_map == instrument_ccd.background_noise_map
        assert simulated_ccd.poisson_noise_map == instrument_ccd.poisson_noise_map
        assert (simulated_ccd.exposure_time_map == instrument_ccd.exposure_time_map).all()
        assert (simulated_ccd.background_sky_map == instrument_ccd.background_sky_map).all()

        simulated_ccd = sim_ccd.SimulatedCCDData.from_image_and_exposure_arrays(image=tracer.profile_image_plane_image_2d_for_simulation, pixel_scale=pixel_scale,
                                                                                exposure_time=exposure_time, psf=psf,
                                                                                background_sky_level=background_sky_level, add_noise=True,
                                                                                noise_seed=1)

        instrument_ccd = instrument.simulate_ccd_data_from_lens_and_source_galaxy(
            lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy], sub_grid_size=1, add_noise=True,
            noise_seed=1)

        assert (simulated_ccd.image == instrument_ccd.image).all()
        assert (simulated_ccd.psf == instrument_ccd.psf).all()
        assert (simulated_ccd.noise_map == instrument_ccd.noise_map).all()
        assert (simulated_ccd.background_noise_map == instrument_ccd.background_noise_map).all()
        assert (simulated_ccd.poisson_noise_map == instrument_ccd.poisson_noise_map).all()
        assert (simulated_ccd.exposure_time_map == instrument_ccd.exposure_time_map).all()
        assert (simulated_ccd.background_sky_map == instrument_ccd.background_sky_map).all()

    def test__simulate_ccd_data_from_lens_and_source_galaxy__and_write_to_fits(self):
        
        lens_galaxy = g.Galaxy(redshift=0.5, mass=mp.EllipticalIsothermal(centre=(0.0, 0.0), einstein_radius=1.6, axis_ratio=0.7,
                                                            phi=45.0))

        source_galaxy = g.Galaxy(redshift=0.5, light=lp.EllipticalSersic(centre=(0.1, 0.1), axis_ratio=0.8, phi=60.0,
                                                           intensity=0.3, effective_radius=1.0, sersic_index=2.5))

        image_plane_grid_stack = grids.GridStack.grid_stack_for_simulation(shape=(11, 11), pixel_scale=0.2,
                                                                           psf_shape=(7, 7), sub_grid_size=1)

        tracer = ray_tracing.TracerImageSourcePlanes(lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy],
                                                     image_plane_grid_stack=image_plane_grid_stack)

        shape = (11, 11)
        pixel_scale = 0.2
        psf = ccd.PSF.from_gaussian(shape=(7, 7), sigma=0.1, pixel_scale=0.2)
        exposure_time = 100.0
        background_sky_level = 1.0

        simulated_ccd = sim_ccd.SimulatedCCDData.from_image_and_exposure_arrays(image=tracer.profile_image_plane_image_2d_for_simulation, pixel_scale=pixel_scale,
                                                                                exposure_time=exposure_time, psf=psf,
                                                                                background_sky_level=background_sky_level, add_noise=False,
                                                                                noise_if_add_noise_false=0.2)

        instrument = ins.Instrument(shape=shape, pixel_scale=pixel_scale, psf=psf, exposure_time=exposure_time,
                                    background_sky_level=background_sky_level)

        output_data_dir = "{}/../test_files/array/output_test/".format(os.path.dirname(os.path.realpath(__file__)))
        if os.path.exists(output_data_dir):
            shutil.rmtree(output_data_dir)

        os.makedirs(output_data_dir)

        instrument.simulate_ccd_data_from_lens_and_source_galaxy_and_write_to_fits(
            lens_galaxies=[lens_galaxy], source_galaxies=[source_galaxy], data_path=output_data_dir, 
            data_name='instrument',  sub_grid_size=1, add_noise=False, noise_if_add_noise_false=0.2)

        output_data_dir += 'instrument/'
        
        instrument_ccd_loaded = ccd.load_ccd_data_from_fits(image_path=output_data_dir + 'image.fits', pixel_scale=0.2,
                                               psf_path=output_data_dir + 'psf.fits',
                                               noise_map_path=output_data_dir + 'noise_map.fits',
                                               background_noise_map_path=output_data_dir + 'background_noise_map.fits',
                                               poisson_noise_map_path=output_data_dir + 'poisson_noise_map.fits',
                                               exposure_time_map_path=output_data_dir + 'exposure_time_map.fits',
                                               background_sky_map_path=output_data_dir + 'background_sky_map.fits',
                                               renormalize_psf=False)

        assert (simulated_ccd.image == instrument_ccd_loaded.image).all()
        assert (simulated_ccd.psf == instrument_ccd_loaded.psf).all()
        assert (instrument_ccd_loaded.noise_map == 0.2*np.ones((11,11)))
        assert simulated_ccd.noise_map == instrument_ccd_loaded.noise_map
        assert simulated_ccd.background_noise_map == instrument_ccd_loaded.background_noise_map
        assert simulated_ccd.poisson_noise_map == instrument_ccd_loaded.poisson_noise_map
        assert (simulated_ccd.exposure_time_map == instrument_ccd_loaded.exposure_time_map).all()
        assert (simulated_ccd.background_sky_map == instrument_ccd_loaded.background_sky_map).all()