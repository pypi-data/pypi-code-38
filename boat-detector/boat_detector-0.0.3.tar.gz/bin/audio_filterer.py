import datetime
import numpy as np
import pandas as pd
import os
import matplotlib

viz = os.environ.get('DISABLE_VIZ')
if viz is not None:
    if int(viz) == 1:
        matplotlib.use('Agg')

import matplotlib.pyplot as plt
import json
import argparse
import ketos.data_handling.parsing as pa
from ketos.audio_processing.audio import AudioSignal, TimeStampedAudioSignal
from ketos.audio_processing.spectrogram import MagSpectrogram
from ketos.data_handling.data_handling import AudioSequenceReader
from ketos.audio_processing.spectrogram_filters import FrequencyFilter, WindowFilter, WindowSubtractionFilter, CroppingFilter, HarmonicFilter, FAVFilter, FAVThresholdFilter
import time
from collections import namedtuple
from pint import UnitRegistry # SI units
from enum import Enum
import math

batch_no = 0

ureg = UnitRegistry() # for parsing values with units

def parse_config(path):
    with open(path, "r") as read_file:
        data = json.load(read_file)

        # date-time format
        fmt = '*HMS_%H_%M_%S__DMY_%d_%m_%y*'
        if data.get('date_time_format') is not None:
            fmt = data['date_time_format']
        
        # ensure string has asterisks on both sides
        if fmt[0] != '*':
            fmt = '*' + fmt
        if fmt[-1] != '*':
            fmt = fmt + '*'

        # max batch size
        batch_size = 5E6
        if data.get('batch_size') is not None:
            batch_size = int(float(data['batch_size']))

        # filters
        filters = list()
        if data.get('filters') is not None:
            for x in data['filters']:
                if x == 'FREQUENCY':
                    bands, names = parse_frequency_config(data)
                    f = FrequencyFilter(bands=bands, names=names)
                    filters.append(f)
                elif x == 'MEDIAN':
                    window_size, step_size = parse_window_config(data, 'median_config')
                    f = WindowFilter(window_size=window_size, step_size=step_size, filter_func=np.ma.median)
                    filters.append(f)
                elif x == 'MEDIAN_SUBTRACTION':
                    window_size, _ = parse_window_config(data, 'median_subtraction_config')
                    f = WindowSubtractionFilter(window_size=window_size, filter_func=np.ma.median)
                    filters.append(f)
                elif x == 'AVERAGE':
                    window_size, step_size = parse_window_config(data, 'average_config')
                    f = WindowFilter(window_size=window_size, step_size=step_size, filter_func=np.ma.average)
                    filters.append(f)
                elif x == 'AVERAGE_SUBTRACTION':
                    window_size, _ = parse_window_config(data, 'average_subtraction_config')
                    f = WindowSubtractionFilter(window_size=window_size, filter_func=np.ma.average)
                    filters.append(f)
                elif x == 'CROPPING':
                    flow, fhigh = parse_cropping_config(data)
                    f = CroppingFilter(flow=flow, fhigh=fhigh)
                    filters.append(f)
                elif x == 'HARMONIC':
                    f = HarmonicFilter()
                    filters.append(f)
                elif x == 'FAV':
                    f = FAVFilter()
                    filters.append(f)
                elif x == 'FAV_THRESHOLD':
                    threshold = 3.0
                    if data.get('fav_config') is not None:
                        threshold = float(data['fav_config'].get('threshold'))
                    f = FAVThresholdFilter(threshold=threshold)
                    filters.append(f)
                else:
                    print('Warning: Unknown filter {0} will be ignored'.format(x))

        # spectrogram
        spectr_config = pa.parse_spectrogram_configuration(data['spectrogram'])

        return spectr_config, filters, batch_size, fmt

def parse_frequency_config(data):
    bands, names = list(), None
    if data.get('frequency_config') is not None:
        names, bands = pa.parse_frequency_bands(data['frequency_config'])
    return bands, names

def parse_window_config(data, name):
    window_size = math.inf
    step_size = None

    if data.get(name) is not None:

        d = data[name]
        Q = ureg.Quantity

        if d.get('window_size') is not None:
            window_size = Q(d['window_size'])
            window_size = window_size.m_as("s")

        if d.get('step_size') is not None:
            step_size = Q(d['step_size'])
            step_size = step_size.m_as("s")

    return window_size, step_size

def parse_cropping_config(data):
    flow, fhigh = None, None

    if data.get('crop_config') is not None:

        d = data['crop_config']
        Q = ureg.Quantity

        if d.get('min_frequency') is not None:
            flow = Q(d['min_frequency'])
            flow = flow.m_as("Hz")

        if d.get('max_frequency') is not None:
            fhigh = Q(d['max_frequency'])
            fhigh = fhigh.m_as("Hz")

    return flow, fhigh

def parse_harmonic_config(data):
    fsep = None

    if data.get('harmonic_config') is not None:

        d = data['harmonic_config']
        Q = ureg.Quantity

        if d.get('frequency_separation') is not None:
            fsep = Q(d['frequency_separation'])
            fsep = fsep.m_as("Hz")

    return fsep

def make_spec(signal, config):

    hamming = False
    if config.window_function == pa.WinFun.HAMMING:
        hamming = True

    # make spectrogram
    spec = MagSpectrogram(audio_signal=signal, winlen=config.window_size, winstep=config.step_size,\
            hamming=hamming, timestamp=signal.begin(), decibel=True)

    return spec

def apply_filters(spec, filters):

    # apply filters
    for f in filters:
        #print('  -',f.name)
        f.apply(spec)

    # dataframe for output data
    t = spec.time_labels()
    f = spec.frequency_labels()
    df = pd.DataFrame({'time': t})
    for i in range(len(f)):
        df[f[i]] = spec.image[:,i]

    # use date-time column as index
    df = df.set_index('time')
    df = df.sort_index(ascending=True)

    return df

def process(signal, config, filters):

    global batch_no
    batch_no += 1

    # make spectrogram
    spec = make_spec(signal=signal, config=config)

    # apply filters
    filtered_data = apply_filters(spec=spec, filters=filters)

    return filtered_data

def parse_args():

    # configure parser
    parser = argparse.ArgumentParser(description='Split audio signal into frequency bands and produce a time series of the noise magnitude in each band.')
    parser.add_argument('-c', '--config_file', type=str, help='path to .json config file.', default='filter_analyzer_config.json')
    parser.add_argument('-i', '--input', type=str, help='path to the .wav file to be analyzed or directory containing multiple .wav files.', default='./')
    parser.add_argument('-o', '--output_file', type=str, help='path to output .csv file', default='out.csv')
    parser.add_argument('-s', '--show_graph', action='store_true', help='Show graph of filtered data')
    parser.add_argument('-a', '--save_graph', action='store_true', help='Save graph of filtered data')
    parser.add_argument('-r', '--recursive_search', action='store_true', help='Include subdirectories in search for .wav files')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print progress updates during processing')

    # parse command-line args
    args = parser.parse_args()

    return args


def main(config_file=None, input_dir=None, output_file=None, show_graph=None, save_graph=None, recursive=None, verbose=None):

    start_time = time.time()

    # parse command-line args
    args = parse_args()

    if config_file is None:        
        config_file = args.config_file
    if input_dir is None:        
        input_dir = args.input
    if output_file is None:        
        output_file = args.output_file
    if show_graph is None:        
        show_graph = args.show_graph
    if save_graph is None:        
        save_graph = args.save_graph
    if recursive is None:        
        recursive = args.recursive_search
    if verbose is None:        
        verbose = args.verbose

    # parse json
    spectr_config, filters, batch_size, fmt = parse_config(config_file)

    # create reader 
    reader = AudioSequenceReader(source=input_dir, recursive_search=recursive, rate=spectr_config.rate, datetime_fmt=fmt, verbose=verbose)

    if verbose:
        print(" Found {0} files".format(len(reader.files)))

    # loop over batches
    outputs = list()
    filtered_data = None
    while not reader.finished():

        if verbose:
            global batch_no
            print(" Processing batch #{0} ...".format(batch_no+1))

        batch = reader.next(size=batch_size) # read next chunk of data
        o = process(batch, spectr_config, filters) # process data
        outputs.append(o) # collect output

        # log of file names and times
        time_table = reader.log()

        # concatenate
        if filtered_data is None:
            filtered_data = pd.concat(outputs, ignore_index=False)
        else:
            filtered_data = pd.concat([filtered_data, outputs[-1]], ignore_index=False)

        # save to .csv files
        rounded = filtered_data.round(3)
        rounded.to_csv(output_file)
        tt_file = output_file[:output_file.rfind('.')] + '_tt.csv'
        time_table.to_csv(tt_file)

    print(" Processed data saved to: {0}".format(output_file))
    print(" Time table saved to: {0}".format(tt_file))

    # your script
    elapsed_time = time.time() - start_time
    print(time.strftime(" Elapsed time: %H:%M:%S", time.gmtime(elapsed_time)))

    # number of columns
    N = len(filtered_data.columns)

    # plot
    if save_graph or show_graph:
        ax = plt.gca()
        ax.set_xlabel('Time')
        ax.set_ylabel('Filtered signal')
        if N < 10:        
            filtered_data.plot(y=filtered_data.columns, ax=ax)
        else:
            img = np.log10(filtered_data.to_numpy())
            img_plot = ax.imshow(img.T, aspect='auto', origin='lower', extent=(0, 1, 0, 1))

        if save_graph:
            fname = output_file[:output_file.rfind('.')] + '.png'
            plt.savefig(fname)
            print(" Figure saved to: {0}".format(fname))
        if show_graph:
            plt.show()

    print('')

if __name__ == '__main__':
   main()
