class HyperOnly(object):

    def hyper_run(self, image, previous_results=None, mask=None):
        raise NotImplementedError()


class LensPlaneHyperPhase(LensPlanePhase):
    """
    Fit only the lens galaxy light.
    """

    lens_galaxies = PhasePropertyCollection("lens_galaxies")

    def __init__(self, lens_galaxies=None, optimizer_class=non_linear.MultiNest, sub_grid_size=2, image_psf_shape=None,
                 mask_function=default_mask_function, cosmology=cosmo.Planck15, phase_name="lens_only_hyper_phase",
                 auto_link_priors=False):

        super(LensPlaneHyperPhase, self).__init__(lens_galaxies=lens_galaxies, optimizer_class=optimizer_class,
                                                  image_psf_shape=image_psf_shape, sub_grid_size=sub_grid_size,
                                                  mask_function=mask_function, cosmology=cosmology,
                                                  phase_name=phase_name, auto_link_priors=auto_link_priors)

    class Analysis(LensPlanePhase.Analysis):

        def __init__(self, lensing_image, cosmology, phase_name, previous_results=None):
            super(LensPlanePhase.Analysis, self).__init__(lensing_image=lensing_image, cosmology=cosmology,
                                                          phase_name=phase_name, previous_results=previous_results)
            self.hyper_model_image = self.map_to_1d(previous_results.last.unmasked_model_images)
            self.hyper_galaxy_images = list(map(lambda galaxy_image: self.map_to_1d(galaxy_image),
                                                previous_results.last.lens_galaxy_padded_model_images))
            self.hyper_minimum_values = len(self.hyper_galaxy_images) * [0.0]

        # TODO : Can we make a HyperPhase class that overwrites these for all HyperPhases?

        def fast_likelihood_for_tracer(self, tracer):
            return lensing_fitters.fast_fit_from_lensing_image_and_tracer(lensing_image=self.lensing_image,
                                                                          tracer=tracer)

        def fit_for_tracers(self, tracer, padded_tracer):
            return lensing_fitters.fit_lensing_image_with_tracer(lensing_image=self.lensing_image, tracer=tracer,
                                                                 padded_tracer=padded_tracer)

        @classmethod
        def log(cls, instance):
            logger.debug(
                "\nRunning lens lens for... \n\nHyper Lens Galaxy::\n{}\n\n".format(instance.lens_galaxies))


class LensLightHyperOnlyPhase(LensPlaneHyperPhase, HyperOnly):
    """
    Fit only the lens galaxy light.
    """

    lens_galaxies = PhasePropertyCollection("lens_galaxies")

    def __init__(self, optimizer_class=non_linear.MultiNest, sub_grid_size=2, image_psf_shape=None,
                 mask_function=default_mask_function, cosmology=cosmo.Planck15, phase_name="lens_only_hyper_phase",
                 hyper_index=None, auto_link_priors=False):
        super(LensLightHyperOnlyPhase, self).__init__(lens_galaxies=[], optimizer_class=optimizer_class,
                                                      image_psf_shape=image_psf_shape,
                                                      sub_grid_size=sub_grid_size, mask_function=mask_function,
                                                      cosmology=cosmology,
                                                      phase_name=phase_name,
                                                      auto_link_priors=auto_link_priors)

        self.hyper_index = hyper_index

    def hyper_run(self, image, previous_results=None, mask=None):
        class LensGalaxyHyperPhase(LensLightHyperOnlyPhase):

            # noinspection PyShadowingNames
            def pass_priors(self, previous_results):
                use_hyper_galaxy = len(previous_results[-1].constant.lens_galaxies) * [None]
                # noinspection PyTypeChecker
                use_hyper_galaxy[self.hyper_index] = g.HyperGalaxy

                self.lens_galaxies = list(map(lambda lens_galaxy, use_hyper:
                                              gm.GalaxyModel.from_galaxy(lens_galaxy, hyper_galaxy=use_hyper),
                                              previous_results.last.constant.lens_galaxies, use_hyper_galaxy))

        hyper_result = previous_results[-1]

        for i in range(len(previous_results[-1].constant.lens_galaxies)):
            phase = LensGalaxyHyperPhase(optimizer_class=non_linear.MultiNest, sub_grid_size=self.sub_grid_size,
                                         mask_function=self.mask_function,
                                         phase_name=self.phase_name + '/lens_gal_' + str(i), hyper_index=i)

            phase.optimizer.n_live_points = 20
            phase.optimizer.sampling_efficiency = 0.8
            result = phase.run(image, previous_results, mask)
            hyper_result.constant.lens_galaxies[i].hyper_galaxy = result.constant.lens_galaxies[i].hyper_galaxy

        return hyper_result

    def make_analysis(self, image, previous_results=None, mask=None):
        """
        Create an lens object. Also calls the prior passing and lensing_image modifying functions to allow child
        classes to change the behaviour of the phase.

        Parameters
        ----------
        mask: Mask
            The default masks passed in by the pipeline
        image: im.CCD
            An lensing_image that has been masked
        previous_results: ResultsCollection
            The result from the previous phase

        Returns
        -------
        lens: Analysis
            An lens object that the non-linear optimizer calls to determine the fit of a set of values
        """
        mask = mask or self.mask_function(image)
        image = self.modify_image(image, previous_results)
        lensing_image = li.LensingImage(image, mask, sub_grid_size=self.sub_grid_size)
        self.pass_priors(previous_results)
        analysis = self.__class__.Analysis(lensing_image=lensing_image, phase_name=self.phase_name,
                                           previous_results=previous_results, hyper_index=self.hyper_index)
        return analysis

    class Analysis(LensPlaneHyperPhase.Analysis):

        def __init__(self, lensing_image, cosmology, phase_name, previous_results=None, hyper_index=None):
            super(LensPlaneHyperPhase.Analysis, self).__init__(lensing_image=lensing_image, cosmology=cosmology,
                                                               phase_name=phase_name, previous_results=previous_results)

            self.hyper_model_image = self.map_to_1d(previous_results.last.unmasked_model_images)
            self.hyper_galaxy_images = list(map(lambda galaxy_image: self.map_to_1d(galaxy_image),
                                                previous_results.last.lens_galaxy_padded_model_images))
            self.hyper_galaxy_images = [self.hyper_galaxy_images[hyper_index]]
            self.hyper_minimum_values = len(self.hyper_galaxy_images) * [0.0]


class LensSourcePlaneHyperPhase(LensSourcePlanePhase):
    """
    Fit a simple source and lens system.
    """

    lens_galaxies = PhasePropertyCollection("lens_galaxies")
    source_galaxies = PhasePropertyCollection("source_galaxies")

    @property
    def phase_property_collections(self):
        return [self.lens_galaxies, self.source_galaxies]

    def __init__(self, lens_galaxies=None, source_galaxies=None, optimizer_class=non_linear.MultiNest,
                 sub_grid_size=2, positions=None, image_psf_shape=None, mask_function=default_mask_function,
                 cosmology=cosmo.Planck15, phase_name="source_lens_phase", auto_link_priors=False):
        """
        A phase with a simple source/lens model

        Parameters
        ----------
        lens_galaxies : [g.Galaxy] | [gm.GalaxyModel]
            A galaxy that acts as a gravitational lens
        source_galaxies: [g.Galaxy] | [gm.GalaxyModel]
            A galaxy that is being lensed
        optimizer_class: class
            The class of a non-linear optimizer
        sub_grid_size: int
            The side length of the subgrid
        """
        super(LensSourcePlaneHyperPhase, self).__init__(lens_galaxies=lens_galaxies,
                                                        source_galaxies=source_galaxies,
                                                        optimizer_class=optimizer_class, sub_grid_size=sub_grid_size,
                                                        positions=positions, image_psf_shape=image_psf_shape,
                                                        mask_function=mask_function, cosmology=cosmology,
                                                        phase_name=phase_name,
                                                        auto_link_priors=auto_link_priors)
        self.lens_galaxies = lens_galaxies
        self.source_galaxies = source_galaxies

    class Analysis(LensSourcePlanePhase.Analysis):

        def __init__(self, lensing_image, cosmology, phase_name, previous_results=None):
            super(LensSourcePlanePhase.Analysis, self).__init__(cosmology=cosmology, lensing_image=lensing_image,
                                                                phase_name=phase_name,
                                                                previous_results=previous_results)

            self.hyper_model_image = self.map_to_1d(previous_results.last.model_data)
            self.hyper_galaxy_images = list(map(lambda galaxy_image: self.map_to_1d(galaxy_image),
                                                previous_results.last.source_galaxies_blurred_image_plane_images))
            self.hyper_minimum_values = len(self.hyper_galaxy_images) * [0.0]

        def fast_likelihood_for_tracer(self, tracer):
            return lensing_fitters.fast_fit_from_lensing_image_and_tracer(lensing_image=self.lensing_image,
                                                                          tracer=tracer)

        def fit_for_tracer(self, tracer):
            return lensing_fitters.fit_lensing_image_with_tracer(lensing_image=self.lensing_image, tracer=tracer)

        @classmethod
        def log(cls, instance):
            logger.debug(
                "\nRunning lens/source lens for... \n\nLens Galaxy:\n{}\n\nSource Galaxy:\n{}\n\n".format(
                    instance.lens_galaxies, instance.source_galaxies))


class LensMassAndSourceProfileHyperOnlyPhase(LensSourcePlaneHyperPhase, HyperOnly):
    """
    Fit only the lens galaxy light.
    """

    lens_galaxies = PhasePropertyCollection("lens_galaxies")
    source_galaxies = PhasePropertyCollection("source_galaxies")

    def __init__(self, optimizer_class=non_linear.MultiNest, sub_grid_size=2, image_psf_shape=None,
                 mask_function=default_mask_function, cosmology=cosmo.Planck15, phase_name="source_and_len_hyper_phase",
                 hyper_index=None, auto_link_priors=False):
        super(LensMassAndSourceProfileHyperOnlyPhase, self).__init__(lens_galaxies=[], source_galaxies=[],
                                                                     optimizer_class=optimizer_class,
                                                                     sub_grid_size=sub_grid_size,
                                                                     image_psf_shape=image_psf_shape,
                                                                     mask_function=mask_function, cosmology=cosmology,
                                                                     phase_name=phase_name,
                                                                     auto_link_priors=auto_link_priors)
        self.hyper_index = hyper_index

    def hyper_run(self, image, previous_results=None, mask=None):
        class SourceGalaxyHyperPhase(LensMassAndSourceProfileHyperOnlyPhase):
            # noinspection PyShadowingNames
            def pass_priors(self, previous_results):
                use_hyper_galaxy = len(previous_results[-1].constant.source_galaxies) * [None]
                # noinspection PyTypeChecker
                use_hyper_galaxy[self.hyper_index] = g.HyperGalaxy

                self.lens_galaxies = previous_results[-1].variable.lens_galaxies
                self.lens_galaxies[0].sie = previous_results[0].constant.lens_galaxies[0].sie
                self.source_galaxies = list(map(lambda source_galaxy, use_hyper:
                                                gm.GalaxyModel.from_galaxy(source_galaxy, hyper_galaxy=use_hyper),
                                                previous_results.last.constant.source_galaxies, use_hyper_galaxy))

        overall_result = previous_results[-1]

        for i in range(len(previous_results[-1].constant.source_galaxies)):
            phase = SourceGalaxyHyperPhase(optimizer_class=non_linear.MultiNest,
                                           sub_grid_size=self.sub_grid_size, mask_function=self.mask_function,
                                           phase_name=self.phase_name + '/src_gal_' + str(i), hyper_index=i)

            phase.optimizer.n_live_points = 20
            phase.optimizer.sampling_efficiency = 0.8
            result = phase.run(image, previous_results, mask)
            overall_result.constant.source_galaxies[i].hyper_galaxy = result.constant.source_galaxies[i].hyper_galaxy

        return overall_result

    def make_analysis(self, image, previous_results=None, mask=None):
        """
        Create an lens object. Also calls the prior passing and lensing_image modifying functions to allow child
        classes to change the behaviour of the phase.

        Parameters
        ----------
        mask: Mask
            The default masks passed in by the pipeline
        image: im.CCD
            An lensing_image that has been masked
        previous_results: ResultsCollection
            The result from the previous phase

        Returns
        -------
        lens: Analysis
            An lens object that the non-linear optimizer calls to determine the fit of a set of values
        """
        mask = mask or self.mask_function(image)
        image = self.modify_image(image, previous_results)
        lensing_image = li.LensingImage(image, mask, sub_grid_size=self.sub_grid_size)
        self.pass_priors(previous_results)
        analysis = self.__class__.Analysis(lensing_image=lensing_image, phase_name=self.phase_name,
                                           previous_results=previous_results, hyper_index=self.hyper_index)
        return analysis

    class Analysis(LensSourcePlaneHyperPhase.Analysis):

        def __init__(self, lensing_image, cosmology, phase_name, previous_results=None, hyper_index=None):
            super(LensSourcePlaneHyperPhase.Analysis, self).__init__(cosmology=cosmology, lensing_image=lensing_image,
                                                                     phase_name=phase_name,
                                                                     previous_results=previous_results)

            self.hyper_model_image = self.map_to_1d(previous_results.last.model_data)
            self.hyper_galaxy_images = list(map(lambda galaxy_image: self.map_to_1d(galaxy_image),
                                                previous_results.last.source_galaxies_blurred_image_plane_images))
            self.hyper_galaxy_images = [self.hyper_galaxy_images[hyper_index]]
            self.hyper_minimum_values = len(self.hyper_galaxy_images) * [0.0]