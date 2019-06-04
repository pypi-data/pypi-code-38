import numpy as np
from plotly.offline import init_notebook_mode, iplot, plot
import plotly.graph_objs as go
from astropy.modeling import models, fitting
import matplotlib.pyplot as plt


class Cary5000Functions:

    @staticmethod
    def find_peak(wavelength, transmission, range, show_fit=False, absorption=False):
        start_index = Cary5000Functions._find_index_of_nearest(wavelength, range[0])
        end_index = Cary5000Functions._find_index_of_nearest(wavelength, range[1])
        x = wavelength[end_index:start_index]
        if absorption:
            y = transmission[end_index:start_index]
        else:
            y = -transmission[end_index:start_index]
        background = Cary5000Functions._find_background(y)
        n = len(x)  # the number of data
        mean = x[np.argmax(y)]  # note this correction
        sigma = 1  # note this correction
        max = np.max(y - background)
        t_init = models.Gaussian1D(mean=mean, amplitude=max, stddev=sigma)
        fit_t = fitting.LevMarLSQFitter()
        t = fit_t(t_init, x, y - background, maxiter=10000)

        if show_fit == True:
            plt.figure()
            plt.plot(x, y, 'ko')
            plt.plot(x, t(x) + background, label='gauss')
            plt.show()

        if fit_t.fit_info['ierr'] > 4:  # An integer flag. If it is equal to 1, 2, 3 or 4, the solution was found. Otherwise, the solution was not found. In either case, the optional output variable ‘mesg’ gives more information.
            fitted_position = 0
            error = 0
            print(fit_t.fit_info['message'])
        else:
            fitted_position = t.mean.value
            error = np.sqrt(np.diag(fit_t.fit_info['param_cov']))[0]

        return fitted_position, error

    @staticmethod
    def _create_min_peak_array(data, range, filter=False, energy=False):
        bla = []
        error = []
        for key in data.get_samples():
            if key == 'Baseline 100%T':
                continue

            transmission = data.get_transmission(key)
            if energy:
                wavelength = data.get_energy(key)
            else:
                wavelength = data.get_wavelength(key)
            start_index = Cary5000Functions._find_index_of_nearest(wavelength, range[0])
            end_index = Cary5000Functions._find_index_of_nearest(wavelength, range[1])
            wavelength = wavelength[end_index:start_index]
            transmission = transmission[end_index:start_index]

            if data.is_absorption():
                amin = np.argmax(np.array(transmission))
                bla.append(wavelength[amin])
            else:
                amin = np.argmin(np.array(transmission))
                bla.append(wavelength[amin])
            error.append(float(0.5))

        return bla, error


    @staticmethod
    def plotly_peakposition(spectras, range, method='gauss', multi=1, show_fit=False):

        if not isinstance(spectras,dict):
            spectras = {'' : spectras}

        init_notebook_mode(connected=True)
        trace = []
        for i, (name, data) in enumerate(spectras.items()):
            if method == 'gauss':
                x, error = Cary5000Functions._create_peak_array(data,range, show_fit=show_fit)
            elif method == 'min':
                x, error = Cary5000Functions._create_min_peak_array(data, range)
            else:
                print('Method unknown ¯\_(ツ)_/¯')
                return None
            y = []
            for key in data.get_samples():
                if key == 'Baseline 100%T':
                    continue
                y.append(key)
            yax='y'+ str(i+1)
            if multi!=1:
                trace.append(Cary5000Functions._create_x_y_trace_multi_y(y, x, error, name,yax))
            else:
                trace.append(Cary5000Functions._create_x_y_trace(y, x, error, name))

        if multi!=1:
            layout = Cary5000Functions._get_plotly_layout_multi_y(multi=multi)
        else:
            layout = Cary5000Functions._get_plotly_layout()

        fig = go.Figure(data=trace, layout=layout)
        return iplot(fig)


    @staticmethod
    def _create_peak_array(data, range, show_fit=False):
        peaks = []
        error = []
        for key in data.get_samples():
            if key == 'Baseline 100%T':
                continue
            tmp_peak, tmp_error = Cary5000Functions.find_peak(data.get_wavelength(key), data.get_transmission(key), range, show_fit=show_fit, absorption=data.is_absorption())
            peaks.append(tmp_peak)
            error.append(tmp_error)
        return peaks, error

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(array - value)).argmin()

    @staticmethod
    def _find_background(counts):
        return np.linspace(counts[0],counts[-1],len(counts))

    @staticmethod
    def _create_x_y_trace(x, y, error,name):
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
    def _create_x_y_trace_multi_y(x, y, error, name, yax):
        return go.Scatter(
            x=x,
            y=y,
            mode='markers+lines',
            name=name,
            yaxis=yax,
            error_y=dict(
                type='data',
                array=error,
                visible=True
            )
        )

    @staticmethod
    def _get_plotly_layout_multi_y(title='', multi=1):

        layout= go.Layout(
            title = title,
            xaxis=dict(
                title='Sample'
            ),
            yaxis=dict(
                title='Peak Position [nm]'
            )
        )
        for i in range(multi):
            pos = 1 - ((i-1)*0.05)
            y = dict(
                title='Peak Position [nm]',
                # titlefont=dict(
                #     color='#ff7f0e'
                # ),
                # tickfont=dict(
                #     color='#ff7f0e'
                # ),
                anchor='free',
                overlaying='y',
                position= pos,
                side='right',
            )
            yax = 'yaxis' + str(i+1)
            layout[yax].update(y)

        return layout

    @staticmethod
    def _get_plotly_layout(title=''):
        return go.Layout(
            title = title,
            xaxis=dict(
                title='Sample'
            ),
            yaxis=dict(
                title='Peak Position [nm]'
            )
        )

