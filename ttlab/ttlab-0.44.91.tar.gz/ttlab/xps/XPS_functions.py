import numpy as np
from scipy import exp
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
from astropy.modeling import models, fitting
import matplotlib.pyplot as plt
from scipy.special import wofz
from scipy.optimize import curve_fit

DEBUG = False


class XPSFunctions:

    @staticmethod
    def find_carbon_peak(energy, counts, background_model,show_fit=False):
        return XPSFunctions.find_peak(energy=energy,
                                      counts=counts,
                                      range=[270, 310],
                                      background_model=background_model, orbital='C1s',show_fit=show_fit)

    @staticmethod
    def find_peak(energy, counts, range, background_model, show_fit=False, gaussian=False, orbital=None,return_all_fit_parameters=False, title='', xtol=None, xtol_init=None):
        x,y, background = XPSFunctions._prepare_data_for_fit(energy,counts,range=range,background_model=background_model)

        if orbital is 'C1s':
            popt,pcov = XPSFunctions._fit_C1s_peaks(x,y,background,show_fit=show_fit, title=title)
        elif orbital is 'Pd3d':
            popt,pcov = XPSFunctions._fit_Pd3d_peaks(x,y,background,show_fit=show_fit, title=title, xtol=xtol, xtol_init=xtol_init)
            if not return_all_fit_parameters:
                return [popt[1],popt[5],popt[9],popt[13],popt[17],popt[21]], [np.sqrt(np.diag(pcov)[1]),np.sqrt(np.diag(pcov)[5]),np.sqrt(np.diag(pcov)[9]),np.sqrt(np.diag(pcov)[13]),np.sqrt(np.diag(pcov)[17]),np.sqrt(np.diag(pcov)[21])]
        elif orbital is 'Pt4f':
            popt, pcov = XPSFunctions._fit_Pt4f_peaks(x, y, background, show_fit=show_fit, title=title, xtol=xtol, xtol_init=xtol_init)
        elif orbital is 'Ag3d':
            popt, pcov = XPSFunctions._fit_Ag3d_peaks(x, y, background, show_fit=show_fit, title=title, xtol=xtol, xtol_init=xtol_init)
        else:
            popt, pcov = XPSFunctions._fit_voigt_peak(x,y, background,show_fit=show_fit)
        if return_all_fit_parameters:
            return popt, pcov
        if return_all_fit_parameters:
            return popt, pcov
        return popt[1], np.sqrt(np.diag(pcov)[1])

    @staticmethod
    def plotly_orbitals(xps_data, orbital, offset=0, offset_multiplier=1):
        init_notebook_mode(connected=True)
        if not isinstance(xps_data,dict):
            xps_data = {'' : xps_data}
        traces = []
        for i, key in enumerate(xps_data):
            try:
                energy = xps_data[key].get_energy_multi(orbital)
                counts = xps_data[key].get_counts_multi(orbital) + offset * offset_multiplier * i
            except:
                energy = []
                counts = []

            traces.append(XPSFunctions._create_x_y_trace(x=energy, y=counts, name=key))

        layout = layout = XPSFunctions._get_plotly_layout(orbital)
        fig = dict(data=traces, layout=layout)
        return iplot(fig)

    @staticmethod
    def plotly_surveys(xps_data, offset=0, offset_multiplier=1):
        init_notebook_mode(connected=True)
        traces = []
        for i, key in enumerate(xps_data):
            try:
                energy = xps_data[key].get_energy_survey()
                counts = xps_data[key].get_counts_survey() + offset * offset_multiplier * i
            except:
                energy = []
                counts = []

            traces.append(XPSFunctions._create_x_y_trace(x=energy,y=counts,name=key))

        layout = XPSFunctions._get_plotly_layout()
        fig = dict(data=traces, layout=layout)
        return iplot(fig)

    @staticmethod
    def plotly_peak_position(xps_data, orbital, fit_range, background_model='shirley', show_fit=False):
        if not isinstance(xps_data, dict):
            xps_data = {'': xps_data}

        peak_position, peak_position_error = XPSFunctions._create_position_array(xps_data=xps_data, orbital=orbital,
                                                                                 fit_range=fit_range,
                                                                                 background_model=background_model,
                                                                                 show_fit=show_fit)

        init_notebook_mode(connected=True)
        traces = [XPSFunctions._create_x_y_error_trace(
            x=list(xps_data.keys()),
            y=peak_position,
            error=peak_position_error)]

        layout = XPSFunctions._get_plotly_errorbar_layout()
        fig = dict(data=traces, layout=layout)

        return iplot(fig)

    @staticmethod
    def _prepare_data_for_fit(energy,counts,range, background_model='shirley'):
        start_index = XPSFunctions._find_index_of_nearest(energy, range[0])
        end_index = XPSFunctions._find_index_of_nearest(energy, range[1])
        x = energy[end_index:start_index]
        y = counts[end_index:start_index]
        if background_model == 'shirley':
            background = XPSFunctions._calculate_shirley_background(x, y)
        else:
            background = XPSFunctions._calculate_linear_background(y)

        return x,y,background


    @staticmethod
    def _fit_C1s_peaks(x,y,background,show_fit=False, title=''):
        mean = x[np.argmax(y)]  # note this correction
        sigma = 1  # note this correction
        max = np.max(y - background)

        lower_boundaries = (0, 270, 0, 0)
        upper_boundaries = (np.inf, 310, np.inf, np.inf)
        initial_parameters = [max, mean, sigma, sigma]
        popt1, pcov1 = curve_fit(XPSFunctions._voigt, x, y - background, initial_parameters,
                                 bounds=(lower_boundaries, upper_boundaries))

        lower_boundaries = (0, 270, popt1[2] - 0.3, popt1[3] - 0.3,
                            0, popt1[1] + 0.5, popt1[2] - 0.3, popt1[3] - 0.3,
                            0, popt1[1] + 2, popt1[2] - 0.3, popt1[3] - 0.3)
        upper_boundaries = (np.inf, 310, popt1[2] + 0.3, popt1[3] + 0.3,
                            popt1[0] * 0.4, popt1[1] + 2, popt1[2] + 0.3, popt1[3] + 0.3,
                            popt1[0] * 0.4, popt1[1] + 5, popt1[2] + 0.3, popt1[3] + 0.3)
        initial_parameters = [popt1[0], popt1[1], popt1[2],popt1[3],
                              popt1[0] * 0.3, popt1[1] + 0.8, popt1[2],popt1[3],
                              popt1[0] * 0.3, popt1[1] + 3, popt1[2],popt1[3]]
        popt1, pcov1 = curve_fit(XPSFunctions._three_voigts, x, y - background, initial_parameters,
                                 bounds=(lower_boundaries, upper_boundaries), maxfev=200000, xtol=1e-4)

        lower_boundaries = (0, 270, popt1[2] - 0.2, popt1[3] - 0.2,
                            0, popt1[1] + 0.5, popt1[2] - 0.2, popt1[3] - 0.2,
                            0, popt1[1] + 2,   popt1[2] - 0.2, popt1[3] - 0.2)
        upper_boundaries = (np.inf, 310, popt1[2] + 0.2, popt1[3] + 0.2,
                            popt1[0] * 0.4, popt1[1] + 2, popt1[2] + 0.2, popt1[3] + 0.2,
                            popt1[0] * 0.4, popt1[1] + 5, popt1[2] + 0.2, popt1[3] + 0.2)
        initial_parameters = [popt1[0], popt1[1], popt1[2], popt1[3],
                              popt1[0] * 0.3, popt1[1] + 0.8, popt1[2], popt1[3],
                              popt1[0] * 0.3, popt1[1] + 3, popt1[2], popt1[3]]
        popt, pcov = curve_fit(XPSFunctions._three_voigts, x, y - background, initial_parameters,
                                 bounds=(lower_boundaries, upper_boundaries), maxfev=200000, ftol=1e-6)

        if show_fit:
            plt.plot(x, y, 'm')
            plt.plot(x, background, 'g')
            plt.plot(x, XPSFunctions._voigt(x, popt[0], popt[1], popt[2], popt[3]) + background,'b')
            plt.plot(x, XPSFunctions._voigt(x, popt[4], popt[5], popt[6], popt[7]) + background,'y')
            plt.plot(x, XPSFunctions._voigt(x, popt[8], popt[9], popt[10], popt[11]) + background,'r')
            plt.plot(x, XPSFunctions._three_voigts(x,*popt) + background,'g')
            plt.plot(x, XPSFunctions._three_voigts(x,*popt1) + background,'--g')
            plt.title(title)
            plt.gca().invert_xaxis()
            plt.show()
        return popt1, pcov1

    @staticmethod
    def _fit_Pd3d_peaks(x, y, background,show_fit=False, title='', xtol=None, xtol_init=None):
        if xtol is None:
            xtol=1e-7
        if xtol_init is None:
            xtol_init=1e-7
        #mean = x[np.argmax(y)]  # note this correction
        sigma = 1  # note this correction
        max = np.max(y - background)

        lower_boundaries = (0, 334.5, 0, 0,
                            0, 334.5+5.26, 0, 0)
        upper_boundaries = (np.inf, 335.5, np.inf, np.inf,
                            np.inf, 335.5+5.26, np.inf, np.inf)
        initial_parameters = [max, 335, sigma, sigma,
                              max*0.7, 335+5.26, sigma, sigma]
        popt1, pcov1 = curve_fit(XPSFunctions._two_voigts, x, y - background, initial_parameters,
                                 bounds=(lower_boundaries, upper_boundaries),xtol=xtol_init)
        plt.plot(x, XPSFunctions._two_voigts(x, *popt1) + background, 'p')

        lower_boundaries = (0, 334.5, popt1[2] - 2, 0,
                            popt1[0] * 0.1, 336.2,  0, 0,
                            popt1[0] * 0.1, 337.5, 0, 0,

                            0, 334.5+5.26 , 0, 0,
                            popt1[4] * 0.1, 336.2+5.26, 0, 0,
                            popt1[4] * 0.1, 337.5+5.26 , 0, 0
                            )

        upper_boundaries = (np.inf, 335.5, popt1[2] + 0.3, popt1[3] + 0.3,
                            popt1[0]*0.3, 337.2, popt1[2] + 0.3, popt1[3] + 0.3,
                            popt1[0]*0.5, 338.5, popt1[2] + 0.3, popt1[3] + 0.3,

                            np.inf, 335.5+5.26, popt1[6] + 0.3, popt1[7] + 0.3,
                            popt1[4]*0.5, 337.2+5.26 , popt1[6] + 0.3, popt1[7] + 0.3,
                            popt1[4]*0.5, 338.5+5.26 , popt1[6] + 0.3, popt1[7] + 0.3
                            )


        initial_parameters = [popt1[0], 335, popt1[2], popt1[3],
                              popt1[0] * 0.3, 336.7, popt1[2], popt1[3],
                              popt1[0] * 0.3, 338, popt1[2], popt1[3],

                              popt1[4], 335.+5.26, popt1[6], popt1[7],
                              popt1[4] * 0.3, 336.7+5.26, popt1[6], popt1[7],
                              popt1[4] * 0.3, 338+5.26, popt1[6], popt1[7]
                              ]

        popt1, pcov1 = curve_fit(XPSFunctions._six_voigts, x, y - background, initial_parameters,
                                 bounds=(lower_boundaries, upper_boundaries), maxfev=200000, xtol=xtol)

        if show_fit:
            plt.plot(x, y, 'm')
            plt.plot(x, background, 'g')
            plt.plot(x, XPSFunctions._six_voigts(x, *popt1) + background, 'k')
            plt.plot(x, XPSFunctions._voigt(x, popt1[0], popt1[1], popt1[2], popt1[3]) + background, 'b')
            plt.plot(x, XPSFunctions._voigt(x, popt1[4], popt1[5], popt1[6], popt1[7]) + background, 'y')
            plt.plot(x, XPSFunctions._voigt(x, popt1[8], popt1[9], popt1[10], popt1[11]) + background, 'r')
            plt.plot(x, XPSFunctions._voigt(x, popt1[12], popt1[13], popt1[14], popt1[15]) + background, 'b')
            plt.plot(x, XPSFunctions._voigt(x, popt1[16], popt1[17], popt1[18], popt1[19]) + background, 'y')
            plt.plot(x, XPSFunctions._voigt(x, popt1[20], popt1[21], popt1[22], popt1[23]) + background, 'r')
            plt.title(title)
            plt.gca().invert_xaxis()
            plt.show()
        return popt1, pcov1

    @staticmethod
    def _fit_Ag3d_peaks(x, y, background,xtol, xtol_init,show_fit=False, title=''):
        if xtol is None:
            xtol=1e-7
        if xtol_init is None:
            xtol_init=100
        mean = x[np.argmax(y)]  # note this correction
        sigma = 1  # note this correction
        max = np.max(y - background)

        lower_boundaries = (0, 364, 0, 0,
                            0, 364, 0, 0)
        upper_boundaries = (np.inf, 384, np.inf, np.inf,
                            np.inf, 384, np.inf, np.inf)
        initial_parameters = [max, mean, sigma, sigma,
                              max*(2/3), mean+6, sigma, sigma]

        popt1, pcov1 = curve_fit(XPSFunctions._two_voigts, x, y - background, initial_parameters, bounds=(lower_boundaries, upper_boundaries),xtol=xtol_init)

        lower_boundaries = (popt1[0] * 0.9, popt1[1] - 0.5,       0, 0,
                            popt1[0] * 0.05, popt1[1] - 0.5 + 1,   0, 0,

                            popt1[4] * 0.9, popt1[5] - 0.5 ,      0, 0,
                            popt1[4] * 0.05, popt1[5] - 0.5 + 1 ,  0, 0,
                            )

        upper_boundaries = (popt1[0] * 2.1, popt1[1] + 0.5,         popt1[2] + 0.3, popt1[3] + 0.3,
                            popt1[0] * 0.7, popt1[1] + 0.5 + 1,   popt1[2] + 0.3, popt1[3] + 0.3,

                            popt1[4] * 2.1, popt1[5] + 0.5,         popt1[6] + 0.3, popt1[7] + 0.3,
                            popt1[4] * 0.7, popt1[5] + 0.5 + 1 ,  popt1[6] + 0.3, popt1[7] + 0.3,
                            )

        initial_parameters = [popt1[0],         popt1[1],       popt1[2], popt1[3],
                              popt1[0] * 0.3,   popt1[1] + 1.4, popt1[2], popt1[3],

                              popt1[4],       popt1[5],         popt1[6], popt1[7],
                              popt1[4] * 0.3, popt1[5] + 1.4,   popt1[6], popt1[7],
                              ]

        popt1, pcov1 = curve_fit(XPSFunctions._four_voigts, x, y - background, initial_parameters,
                                 bounds=(lower_boundaries, upper_boundaries), maxfev=200000, xtol=xtol)

        if show_fit:
            plt.plot(x, y, 'm')
            plt.plot(x, background, 'g')
            plt.plot(x, XPSFunctions._four_voigts(x, *popt1) + background, 'k')
            plt.plot(x, XPSFunctions._voigt(x, popt1[0], popt1[1], popt1[2], popt1[3]) + background, 'b')
            plt.plot(x, XPSFunctions._voigt(x, popt1[4], popt1[5], popt1[6], popt1[7]) + background, 'r')
            plt.plot(x, XPSFunctions._voigt(x, popt1[8], popt1[9], popt1[10], popt1[11]) + background, 'b')
            plt.plot(x, XPSFunctions._voigt(x, popt1[12], popt1[13], popt1[14], popt1[15]) + background, 'r')
            plt.title(title)
            plt.gca().invert_xaxis()
            plt.show()

        return popt1, pcov1

    @staticmethod
    def _fit_Pt4f_peaks(x, y, background,show_fit=False, title='', xtol=None, xtol_init=None):
        if xtol is None:
            xtol=1e-5
        if xtol_init is None:
            xtol_init=1e-7
        mean = x[np.argmax(y)]  # note this correction
        sigma = 1  # note this correction
        max = np.max(y - background)

        lower_boundaries = (0, 66, 0, 0,
                            0, 66, 0, 0)
        upper_boundaries = (np.inf, 83, np.inf, np.inf,
                            np.inf, 83, np.inf, np.inf)
        initial_parameters = [max, mean, sigma, sigma,
                              max*0.7, mean+3.35, sigma, sigma]
        popt1, pcov1 = curve_fit(XPSFunctions._two_voigts, x, y - background, initial_parameters,
                                 bounds=(lower_boundaries, upper_boundaries),xtol=xtol_init)
        #plt.plot(x, XPSFunctions._two_voigts(x, *popt1) + background, 'p')
        #plt.gca().invert_xaxis()
        # print(popt1)

        lower_boundaries = (popt1[0] * 0.9, popt1[1] - 1,       0, 0,
                            popt1[0] * 0.05, popt1[1] - 1 + 1,   0, 0,
                            popt1[0] * 0.05, popt1[1] - 1 + 2.5, 0, 0,

                            popt1[4] * 0.9, popt1[5] - 1 ,      0, 0,
                            popt1[4] * 0.05, popt1[5] - 1 + 1 ,  0, 0,
                            popt1[4] * 0.05, popt1[5] - 1 + 2.5, 0, 0
                            )

        upper_boundaries = (popt1[0] * 1.1, popt1[1] + 0.5,         popt1[2] + 0.3, popt1[3] + 0.3,
                            popt1[0] * 0.7, popt1[1] + 0.5 + 1.9,   popt1[2] + 0.3, popt1[3] + 0.3,
                            popt1[0] * 0.7, popt1[1] + 0.5 + 3,     popt1[2] + 0.3, popt1[3] + 0.3,

                            popt1[4] * 1.1, popt1[5] + 0.5,         popt1[6] + 0.3, popt1[7] + 0.3,
                            popt1[4] * 0.7, popt1[5] + 0.5 + 1.9 ,  popt1[6] + 0.3, popt1[7] + 0.3,
                            popt1[4] * 0.7, popt1[5] + 0.5 + 3,     popt1[6] + 0.3, popt1[7] + 0.3
                            )


        initial_parameters = [popt1[0],         popt1[1],       popt1[2], popt1[3],
                              popt1[0] * 0.3,   popt1[1] + 1.4, popt1[2], popt1[3],
                              popt1[0] * 0.3,   popt1[1] + 2.9, popt1[2], popt1[3],

                              popt1[4],       popt1[5],         popt1[6], popt1[7],
                              popt1[4] * 0.3, popt1[5] + 1.4,   popt1[6], popt1[7],
                              popt1[4] * 0.3, popt1[5] + 2.9,   popt1[6], popt1[7]
                              ]
        # print(initial_parameters)
        popt1, pcov1 = curve_fit(XPSFunctions._six_voigts, x, y - background, initial_parameters,
                                 bounds=(lower_boundaries, upper_boundaries), maxfev=200000, xtol=xtol)

        if show_fit:
            plt.figure(figsize=(16, 9))
            plt.plot(x, y, 'm')
            plt.plot(x, background, 'g')
            plt.plot(x, XPSFunctions._six_voigts(x, *popt1) + background, 'k')
            plt.plot(x, XPSFunctions._voigt(x, popt1[0], popt1[1], popt1[2], popt1[3]) + background, 'b')
            plt.plot(x, XPSFunctions._voigt(x, popt1[4], popt1[5], popt1[6], popt1[7]) + background, 'y')
            plt.plot(x, XPSFunctions._voigt(x, popt1[8], popt1[9], popt1[10], popt1[11]) + background, 'r')

            plt.plot(x, XPSFunctions._voigt(x, popt1[12], popt1[13], popt1[14], popt1[15]) + background, 'b')
            plt.plot(x, XPSFunctions._voigt(x, popt1[16], popt1[17], popt1[18], popt1[19]) + background, 'y')
            plt.plot(x, XPSFunctions._voigt(x, popt1[20], popt1[21], popt1[22], popt1[23]) + background, 'r')
            plt.title(title)
            plt.gca().invert_xaxis()
        return popt1, pcov1


    @staticmethod
    def _fit_voigt_peak(x,y,background,show_fit=False):
        mean = x[np.argmax(y)]  # note this correction
        sigma = 1  # note this correction
        max = np.max(y - background)
        initial_parameters = [max, mean, sigma, sigma]
        popt, pcov = curve_fit(XPSFunctions._voigt, x, y - background, initial_parameters)

        if show_fit:
            plt.plot(x, y, 'm')
            plt.plot(x, background, 'g')
            plt.plot(x, XPSFunctions._voigt(x, *popt) + background, 'k')
            plt.gca().invert_xaxis()
            plt.show()

        return popt, pcov

    @staticmethod
    def _create_position_array(xps_data, orbital, fit_range, background_model, show_fit):
        position = []
        position_error = []
        for sample in xps_data.keys():
            [pos, err] = XPSFunctions.find_peak(xps_data[sample].get_energy_multi(orbital),
                                                xps_data[sample].get_counts_multi(orbital), fit_range, background_model,
                                                show_fit)
            if show_fit:
                print(sample)
            position.append(pos)
            position_error.append(err)
        return position, position_error

    @staticmethod
    def _voigt(x,amplitude, mean, fwhm_L, fwhm_G):
        v1 = models.Voigt1D(mean, amplitude, fwhm_L, fwhm_G)
        return v1(x)
        """ Return the Voigt line shape at x with Lorentzian component HWHM gamma
        and Gaussian component HWHM alpha."""
        sigma = alpha / np.sqrt(2 * np.log(2))
        return amplitude * np.real(wofz((x + 1j * gamma) / sigma / np.sqrt(2))) / sigma \
               / np.sqrt(2 * np.pi)

    @staticmethod
    def _gaussian(x, a, x0, sigma):
        return a * exp(-(x - x0) ** 2 / (2 * sigma ** 2))

    @staticmethod
    def _three_gaussians(x,a,x0,sigma,a1,x01,sigma1,a2,x02,sigma2):
        return XPSFunctions._gaussian(x,a,x0,sigma) + XPSFunctions._gaussian(x,a1,x01,sigma1) + XPSFunctions._gaussian(x,a2,x02,sigma2)

    @staticmethod
    def _two_voigts(x, a, x0, sigma_l, sigma_g, a1, x01, sigma_l1, sigma_g1):
        return XPSFunctions._voigt(x, a, x0, sigma_l, sigma_g) + XPSFunctions._voigt(x, a1, x01, sigma_l1,sigma_g1)

    @staticmethod
    def _three_voigts(x, a, x0, sigma_l,sigma_g, a1, x01, sigma_l1,sigma_g1, a2, x02, sigma_l2,sigma_g2):
        return XPSFunctions._voigt(x, a, x0, sigma_l, sigma_g)+XPSFunctions._voigt(x, a1, x01 ,sigma_l1, sigma_g1)+XPSFunctions._voigt(x, a2, x02, sigma_l2, sigma_g2)

    @staticmethod
    def _four_voigts(x, a, x0, sigma_l, sigma_g, a1, x01, sigma_l1, sigma_g1,a2, x02, sigma_l2,sigma_g2, a3, x03, sigma_l3,sigma_g3):
        return XPSFunctions._two_voigts(x, a, x0, sigma_l, sigma_g, a1, x01, sigma_l1, sigma_g1) + XPSFunctions._two_voigts(x, a2, x02, sigma_l2,sigma_g2, a3, x03, sigma_l3,sigma_g3)

    @staticmethod
    def _six_voigts(x, a, x0, sigma_l,sigma_g, a1, x01, sigma_l1,sigma_g1, a2, x02, sigma_l2,sigma_g2, a3, x03, sigma_l3,sigma_g3, a4, x04, sigma_l4,sigma_g4, a5, x05, sigma_l5,sigma_g5):
        return XPSFunctions._three_voigts(x, a, x0, sigma_l,sigma_g, a1, x01, sigma_l1,sigma_g1, a2, x02, sigma_l2,sigma_g2) + XPSFunctions._three_voigts(x, a3, x03, sigma_l3, sigma_g3, a4, x04, sigma_l4, sigma_g4, a5, x05, sigma_l5, sigma_g5)

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(array - value)).argmin()

    @staticmethod
    def _calculate_linear_background(counts):
        return np.linspace(counts[0], counts[-1], len(counts))

    @staticmethod
    def _create_x_y_error_trace(x, y, error, name=''):
        return go.Scatter(
            x=x,
            y=y,
            mode='markers+lines',
            name=name,
            error_y=dict(
                type='data',
                array=error,
                visible=True
            )
        )

    @staticmethod
    def _create_x_y_trace(x, y, name=''):
        return go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name=name
        )

    @staticmethod
    def _get_plotly_layout(title=''):
        return go.Layout(
            title=title,
            xaxis=dict(
                autorange='reversed',
                title='Energy [eV]',
            ),
            yaxis=dict(
                title='Counts [a.u.]',
                exponentformat='e',
                showexponent='all'
            )
        )

    @staticmethod
    def _get_plotly_errorbar_layout(title=''):
        return go.Layout(
            title=title,
            yaxis=dict(
                title='Peakposition [nm]'
            )
        )


    # https://github.com/kaneod/physics/blob/master/python/specs.py
    @staticmethod
    def _calculate_shirley_background(x, y, tol=1e-5, maxit=20):
        """ S = specs.shirley_calculate(x,y, tol=1e-5, maxit=10)
        Calculate the best auto-Shirley background S for a dataset (x,y). Finds the biggest peak
        and then uses the minimum value either side of this peak as the terminal points of the
        Shirley background.
        The tolerance sets the convergence criterion, maxit sets the maximum number
        of iterations.
        """

        # Make sure we've been passed arrays and not lists.
        x = np.array(x)
        y = np.array(y)

        # Sanity check: Do we actually have data to process here?
        if not (x.any() and y.any()):
            print("specs.shirley_calculate: One of the arrays x or y is empty. Returning zero background.")
            return np.zeros(x.shape)

        # Next ensure the energy values are *decreasing* in the array,
        # if not, reverse them.
        if x[0] < x[-1]:
            is_reversed = True
            x = x[::-1]
            y = y[::-1]
        else:
            is_reversed = False

        # Locate the biggest peak.
        maxidx = abs(y - np.amax(y)).argmin()

        # It's possible that maxidx will be 0 or -1. If that is the case,
        # we can't use this algorithm, we return a zero background.
        if maxidx == 0 or maxidx >= len(y) - 1:
            print("specs.shirley_calculate: Boundaries too high for algorithm: returning a zero background.")
            return np.zeros(x.shape)

        # Locate the minima either side of maxidx.
        lmidx = abs(y[0:maxidx] - np.amin(y[0:maxidx])).argmin()
        rmidx = abs(y[maxidx:] - np.amin(y[maxidx:])).argmin() + maxidx
        xl = x[lmidx]
        yl = y[lmidx]
        xr = x[rmidx]
        yr = y[rmidx]

        # Max integration index
        imax = rmidx - 1

        # Initial value of the background shape B. The total background S = yr + B,
        # and B is equal to (yl - yr) below lmidx and initially zero above.
        B = np.zeros(x.shape)
        B[:lmidx] = yl - yr
        Bnew = B.copy()

        it = 0
        while it < maxit:
            if DEBUG:
                print("Shirley iteration: ", it)
            # Calculate new k = (yl - yr) / (int_(xl)^(xr) J(x') - yr - B(x') dx')
            ksum = 0.0
            for i in range(lmidx, imax):
                ksum += (x[i] - x[i + 1]) * 0.5 * (y[i] + y[i + 1]
                                                   - 2 * yr - B[i] - B[i + 1])
            k = (yl - yr) / ksum
            # Calculate new B
            for i in range(lmidx, rmidx):
                ysum = 0.0
                for j in range(i, imax):
                    ysum += (x[j] - x[j + 1]) * 0.5 * (y[j] +
                                                       y[j + 1] - 2 * yr - B[j] - B[j + 1])
                Bnew[i] = k * ysum
            # If Bnew is close to B, exit.
            if np.linalg.norm(Bnew - B) < tol:
                B = Bnew.copy()
                break
            else:
                B = Bnew.copy()
            it += 1

        if it >= maxit:
            print("specs.shirley_calculate: Max iterations exceeded before convergence.")
        if is_reversed:
            return (yr + B)[::-1]
        else:
            return yr + B
