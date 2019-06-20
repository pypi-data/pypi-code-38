from DataProcessing import Preprocessor
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def parse_trial(trial):
    Ax = trial.data['x'].tail(1).values[0] - trial.data['x'].head(1).values[0]  # for 1 J
    Ay = trial.data['y'].tail(1).values[0] - trial.data['y'].head(1).values[0]  # for 1 J
    Vx = np.array(trial.data['Vx'])
    Vy = np.array(trial.data['Vy'])
    posx = np.array(trial.data['x'])
    posy = np.array(trial.data['y'])
    t = np.array(trial.data.index)
    D = max(t) - min(t)  # for 1 J
    t0 = 0.
    return Ax, Ay, Vx, Vy, posx, posy, t, D, t0


def func(t, *params):
    """Creates the cost jerk function for x and y"""
    Y = np.zeros_like(t)
    for i in range(0, len(params), 3):
        t0 = params[i]
        D = params[i+1]
        A = params[i+2]

        nt = (t - t0) / D
        Y = Y + A / D * (-60 * nt ** 3 + 30 * nt ** 4 + 30 * nt ** 2)

    return Y


def optimize_jerk(trial, plot_fit):
    ###
    # Creates the cost jerk function for x and y
    # TODO: add support for all dimensions (currently fits only X data
    ###

    params = parse_trial(trial)
    Ax = params[0]
    Ay = params[1]
    Vx = params[2]
    Vy = params[3]
    posx = params[4]
    posy = params[5]
    t = params[6]
    D = params[7]
    t0 = params[8]

    n = 3

    guess_x = [0, 0.9, 180]
    for n in range(1,n):
        guess_x += [t0, D/n, 180]


    # TODO: calculate bounds
    #  bounds_low = [0, 0.1, -50, -50]
    #  bounds_high = [t.max(), t.max()-t.min(), 200, 200]

    popt_x, pcov_x = curve_fit(func, t, Vx, p0=guess_x)
    perr_x = np.sqrt(np.diag(pcov_x))

    print(popt_x)
    print(perr_x)

    fit = func(t, *popt_x)

    if plot_fit:
        plt.plot(t, Vx)
        plt.plot(t, fit, 'r-')
        plt.show()


    return fit, popt_x, perr_x

if __name__ == '__main__':
    path_to_raw_data = '..\\data\\results\\simonvisual\\1'
    path_to_trials = '..\\data\\trials'

    pproc = Preprocessor()
    raw_data_gen = pproc.load_df_from_directory_gen(dir_path=path_to_raw_data, cols=('x', 'y'))

    # demo for a single trial:
    for trial in raw_data_gen:
        trial.preprocess(pproc)
        trial.save_df(trial.data, path_to_trials)
        res = optimize_jerk(trial, True)
        print(f'Parameters: {res[1]}')
        print(f'Parameter errors: {res[2]}')
        break
