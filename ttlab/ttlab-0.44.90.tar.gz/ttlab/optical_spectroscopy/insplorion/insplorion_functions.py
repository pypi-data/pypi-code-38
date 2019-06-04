from astropy.modeling import models, fitting
import numpy as np

class InsplorionFunctions:

    @staticmethod
    def find_peak_position(wavelength, intensity):
        #return wavelength[np.argmax(intensity)]
        mean = wavelength[np.argmax(intensity)]  # note this correction
        sigma = 1  # note this correction
        max = np.max(intensity)
        t_init = models.Voigt1D(x_0=mean, amplitude_L=max, fwhm_L=sigma, fwhm_G=sigma)
        # t_init = models.Gaussian1D(mean=mean, amplitude=max, stddev=sigma)
        fit_t = fitting.LevMarLSQFitter()
        t = fit_t(t_init, wavelength, intensity, maxiter=10000)
        if fit_t.fit_info['ierr'] > 4:      # An integer flag. If it is equal to 1, 2, 3 or 4, the solution was found. Otherwise, the solution was not found. In either case, the optional output variable ‘mesg’ gives more information.
            fitted_position = 0
            error = 0
            print(fit_t.fit_info['message'])
        else:
            fitted_position = t.x_0.value
            error = np.sqrt(np.diag(fit_t.fit_info['param_cov']))[0]

        return fitted_position, error

    @staticmethod
    def _gaussian(x, a, x0, sigma):
        return a * exp(-(x - x0) ** 2 / (2 * sigma ** 2))
