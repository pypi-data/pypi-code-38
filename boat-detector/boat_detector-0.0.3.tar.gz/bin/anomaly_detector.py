# Read more about scikit-learn outlier testing here: 
# http://scikit-learn.org/stable/modules/outlier_detection.html#outlier-detection

import numpy as np
import pandas as pd
import argparse
import json
from enum import Enum
from collections import namedtuple
import datetime
from pint import UnitRegistry
import math
import matplotlib.pyplot as plt
from ketos.utils import detect_peaks, get_member
from ketos.data_handling.parsing import str2bool

ureg = UnitRegistry()

PeakFindingConfig = namedtuple('PeakFindingConfig', 'separation size multiplicity height')
PeakFindingConfig.__new__.__defaults__ = (60, 3.0, 1, 0)
PeakFindingConfig.__doc__ = '''\
Configuration of peak finding algorithm

separation - Minimum temporal separation between neighboring peaks in seconds
size - Minimum peak height relative to baseline given in multiples of the signal standard devitation (float)
multiplicity - Minimum number of data series in which peak occurs
height - minimum absolute height of peak'''

SVMConfig = namedtuple('SVMConfig', 'nu kernel gamma degree training_data')
SVMConfig.__new__.__defaults__ = (0.01, "poly", 0.001, 2, "None")
SVMConfig.__doc__ = '''\
Configuration of One-class SVM model

See: http://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html
'''

class Detector(Enum):
    PEAK_FINDING = 1
    ELLIPTIC_ENVELOPE = 2
    LOCAL_OUTLIER_FACTOR = 3
    ISOLATION_FOREST = 4
    ONE_CLASS_SVM = 5

def parse_config(path):
    with open(path, "r") as read_file:

        # data series
        data = json.load(read_file)
        data_series = data['data_series']

        # detectors
        det_names = data['detectors'] # strings
        detectors = list() # enums
        for det_name in det_names:
            n = len(detectors)
            detectors.append(get_member(Detector, det_name))
                
        # configs
        configs = {}
        name, cfg = parse_peak_finding_config(data)
        configs[name] = cfg
        name, cfg = parse_svm_config(data)
        configs[name] = cfg

        # outlier fraction
        outlier_fraction = 0.1
        if data.get('outlier_fraction') is not None:
            outlier_fraction = float(data['outlier_fraction'])

        # minimum outlier separation in seconds
        min_sep = 1
        if data.get('anomaly_separation') is not None:
            Q = ureg.Quantity
            min_sep = Q(data['anomaly_separation'])
            min_sep = min_sep.m_as("s")

        return data_series, detectors, configs, outlier_fraction, min_sep

def parse_peak_finding_config(data):
    s = 'peak_finding_config'
    default = PeakFindingConfig()
    separation = default.separation
    size = default.size
    multiplicity = default.multiplicity
    if data.get(s) is not None:
        d = data[s]
        if d['separation'] is not None:
            Q = ureg.Quantity
            separation = Q(d['separation'])
            separation = separation.m_as("s")
        if d['prominence'] is not None:
            size = float(d['prominence'])
        if d['multiplicity'] is not None:
            multiplicity = int(d['multiplicity'])
        if d['height'] is not None:
            height = float(d['height'])
    res = PeakFindingConfig(separation=separation, size=size, multiplicity=multiplicity, height=height)
    return s, res

def parse_svm_config(data):
    s = 'svm_config'
    default = SVMConfig()
    nu = default.nu
    kernel = default.kernel
    gamma = default.gamma
    degree = default.degree
    training_data = default.training_data
    if data.get(s) is not None:
        d = data[s]
        if d['nu'] is not None:
            nu = float(d['nu'])
        if d['kernel'] is not None:
            kernel = d['kernel']
        if d['gamma'] is not None:
            gamma = float(d['gamma'])
        if d['degree'] is not None:
            degree = int(d['degree'])
        if d['training_data'] is not None:
            training_data = d['training_data']
    res = SVMConfig(nu=nu, kernel=kernel, gamma=gamma, degree=degree, training_data=training_data)
    return s, res

def extract_time_res(df):
    time_res = math.inf
    for i in range(1,len(df.index)):
        t0 = parse_time(df.index[i-1])
        t1 = parse_time(df.index[i])
        delta = 1E-6 * (t1 - t0).microseconds
        if delta < time_res and delta > 0:
            time_res = delta
    return time_res

def parse_time(s):
    fmt = "%Y-%m-%d %H:%M:%S"
    nofrag = s
    frag = None
    if s.find('.') >= 0:
        nofrag, frag = s.split('.')

    dt = datetime.datetime.strptime(nofrag, fmt)
    if frag is not None:
        dt = dt.replace(microsecond=int(1E3*int(frag)))

    return dt

def zeros_and_ones(x):
    x = ((-1)*x + 1) / 2
    x = x.astype(int)
    return x

def parse_args():

    # configure parser
    parser = argparse.ArgumentParser(description='Perform outlier- and peak analysis of time-series data.')
    parser.add_argument('-c', '--config_file', type=str, help='path to .json config file.', default='anomaly_detector_config.json')
    parser.add_argument('-i', '--input_file', type=str, help='.csv file containing time-series data to be analyzed.', default='out.csv')
    parser.add_argument('-o', '--output_file', type=str, help='.csv file where analysis report will be outputted.', default='det.csv')
    parser.add_argument('-s', '--show_graph', action='store_true', help='Show time-series data')
    parser.add_argument('-t', '--time_table', type=str, help='path to .csv file with table of times and file names', default=None)

    # parse command-line args
    args = parser.parse_args()
    
    return args

def main():

    # parse command-line args
    args = parse_args()

    config_file = args.config_file
    input_file = args.input_file
    output_file = args.output_file
    show_graph = args.show_graph
    time_table = args.time_table

    # read input data into pandas dataframe
    df0 = pd.read_csv(input_file)

    assert df0.shape[0] >= 2, "Input data should have at least two rows of data"

    # read configuration file
    data_series, detectors, configs, outlier_fraction, min_sep = parse_config(config_file)

    # extract relevant columns
    data_series.append('time')
    X = df0[data_series]

    # use time column as index
    X = X.set_index('time')

    # dataframe for output data
    df = pd.DataFrame(X.index)
    df = df.set_index('time')


    #=================
    # peak detection #
    #=================

    if Detector.PEAK_FINDING in detectors:
        cfg = configs['peak_finding_config']
        time_res = extract_time_res(X)
        dist = max(1, int(cfg.separation / time_res))
        df['Peak Finding'] = detect_peaks(X, distance=dist, prominence=cfg.size, multiplicity=cfg.multiplicity, height=cfg.height)


    #====================
    # outlier detection #
    #====================

    # Robust covariance
    if Detector.ELLIPTIC_ENVELOPE in detectors:
        from sklearn.covariance import EllipticEnvelope
        ee = EllipticEnvelope(contamination=outlier_fraction)
        ee.fit(X) 
        df['Elliptic Envelope'] = pred = zeros_and_ones(ee.predict(X))

    # Local Outlier Factor
    if Detector.LOCAL_OUTLIER_FACTOR in detectors:
        from sklearn.neighbors import LocalOutlierFactor
        lof = LocalOutlierFactor(contamination=outlier_fraction)
        df['Local Outlier Factor'] = zeros_and_ones(lof.fit_predict(X))

    # Isolation Forest
    if Detector.ISOLATION_FOREST in detectors:
        from sklearn.ensemble import IsolationForest
        isofor = IsolationForest(contamination=outlier_fraction)
        isofor.fit(X) 
        df['Isolation Forest'] = zeros_and_ones(isofor.predict(X))


    #================
    # One-class SVM #
    #================

    if Detector.ONE_CLASS_SVM in detectors:
        from sklearn import svm
        cfg = configs['svm_config']
        clf = svm.OneClassSVM(nu=cfg.nu, kernel=cfg.kernel, degree=cfg.degree, gamma=cfg.gamma)
        df_train = pd.read_csv(cfg.training_data)
        X_train = df_train[data_series]
        X_train = X_train.set_index('time')
        # fit
        clf.fit(X_train)
        # predict
        df['One-class SVM'] = zeros_and_ones(clf.predict(X))


    #===================================================
    # Count time-separated anomalies and create output #
    #===================================================

    # count time-separated anomalies
    s = np.sum(df, axis=1)
    n = s.shape[0]
    sep = 0
    times = list()
    for i in range(0,n):
        tnow = parse_time(df.index[i])
        if i > 0:
            tprev = parse_time(df.index[i-1])
            delta = (tnow - tprev).total_seconds()
            sep += delta
        if (s[i] > 0 and (sep > min_sep or i == 0)):
            sep = 0
            times.append(tnow)

    df_out = pd.DataFrame(columns=['time'])
    df_out['time'] = np.array(times)

    # if time table exists, determine file name and 'local time'
    if time_table != None:
        df_tt = pd.read_csv(time_table)
        df_tt = df_tt.sort_index(ascending=False, axis=0)
        fnames = list()
        times = list()
        for t in df_out['time']:
            for _, row in df_tt.iterrows():
                t0 = parse_time(row['time'])
                f = row['file']
                dt = (t0 - t).total_seconds()
                if (dt < 0):
                    fnames.append(f)
                    times.append(-dt)
                    break
        df_out['file_name'] = np.array(fnames)
        df_out['seconds_from_start_of_file'] = np.array(times)

    # save detections file
    df_out.to_csv(output_file)
    print(' {0} anomalies detected'.format(len(times)))
    print(' Detection report saved to: {0}'.format(output_file))
    print('')


    # plot
    if show_graph:
        ax = plt.gca()
        ax.set_xlabel('Time')
        ax.set_ylabel('Filtered signal')
        n = len(X.index.values)
        xticks = [0, int(n/2), n-1]
        X.plot(y=X.columns, xticks=xticks, ax=ax)
        plt.show()


if __name__ == '__main__':
   main()
