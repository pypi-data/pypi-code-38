# coding: utf-8

import numpy as np
import scipy.io.wavfile as wav
import pylab as pl
import matplotlib.pyplot as plt
import pylab
from numpy.lib import stride_tricks
import wave

from scipy.signal import hilbert

""" short time fourier transform of audio signal """


def stft(sig, frameSize, overlapFac=0.5, window=np.hanning):
    # print frameSize
    win = window(frameSize)
    hopSize = int(frameSize - np.floor(overlapFac * frameSize))

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = np.append(np.zeros(int(np.floor(frameSize / 2.0))), sig)
    # cols for windowing
    cols = int(np.ceil((len(samples) - frameSize) / float(hopSize)) + 1)
    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(frameSize))
    # print samples, (cols, frameSize),(samples.strides[0] * hopSize, samples.strides[0])

    frames = stride_tricks.as_strided(samples, shape=(cols, frameSize),
                                      strides=(samples.strides[0] * hopSize, samples.strides[0])).copy()
    frames *= win

    return np.fft.rfft(frames)


""" scale frequency axis logarithmically """


def logscale_spec(spec, sr=44100, factor=20.):
    timebins, freqbins = np.shape(spec)

    scale = np.linspace(0, 1, freqbins) ** factor
    scale *= (freqbins - 1) / max(scale)
    scale = np.unique(np.round(scale))

    # create spectrogram with new freq bins
    newspec = np.complex128(np.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            newspec[:, i] = np.sum(spec[:, int(scale[i]):], axis=1)
        else:

            newspec[:, i] = np.sum(spec[:, int(scale[i]):int(scale[i + 1])], axis=1)

    # list center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins * 2, 1. / sr)[:freqbins + 1])
    freqs = []
    for i in range(0, len(scale)):
        if i == len(scale) - 1:
            freqs += [np.mean(allfreqs[int(scale[i]):])]
        else:
            freqs += [np.mean(allfreqs[int(scale[i]):int(scale[i + 1])])]

    return newspec, freqs


""" get spectrogram"""


def get_stft(audiopath, binsize=2 ** 10):
    samplerate, samples = wav.read(audiopath)
    s = stft(samples, binsize)
    sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)
    ims = 20. * np.log10(np.abs(sshow) / 10e-6)  # amplitude to decibel
    ims = ims / 255
    # timebins, freqbins = np.shape(ims)
    return ims


""" plot spectrogram"""


def plot_stft(audiopath, binsize=2 ** 10, plotpath=None, colormap="binary"):  # "jet" 'hot'
    '''
    plotstft('pop2.wav', plotpath='pop2.eps')
    :param audiopath:
    :param binsize:
    :param plotpath:
    :param colormap: "jet" ,'hot','binary'....
    :return:
    '''
    samplerate, samples = wav.read(audiopath)
    s = stft(samples, binsize)
    sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)
    ims = 20. * np.log10(np.abs(sshow) / 10e-6)  # amplitude to decibel
    ims = ims / 255

    timebins, freqbins = np.shape(ims)
    print(timebins, freqbins)
    plt.figure(figsize=(15, 7.5))
    plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")
    plt.colorbar()

    plt.xlabel("time (s)")
    plt.ylabel("frequency (hz)")
    plt.xlim([0, timebins - 1])
    plt.ylim([0, freqbins])

    xlocs = np.float32(np.linspace(0, timebins - 1, 5))
    plt.xticks(xlocs, ["%.02f" % l for l in ((xlocs * len(samples) / timebins) + (0.5 * binsize)) / samplerate])
    ylocs = np.int16(np.round(np.linspace(0, freqbins - 1, 10)))
    plt.yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])

    if plotpath:
        plt.savefig(plotpath, bbox_inches="tight")
    else:
        plt.show()

    plt.clf()


def plot_Envelope(signal, xlabel_string='Time (seconds)', ylabel_String='Amplitude',
                  fig_title='X, with calculated envelope', legend_signal_str='signal', legend_envelop_str='envelope',
                  plotpath=None):
    '''

    :param signal:
    :param xlabel_string:
    :param ylabel_String:
    :param fig_title:
    :param legend_signal_str:
    :param legend_envelop_str:
    :return:
    '''
    # t=linspace(0, 1, len(signal))
    # Calculate envelope, called m_hat via hilbert transform
    m_hat = abs(hilbert(signal))
    max_signal = max(signal)
    min_signal = min(signal)
    y_label = max(abs(min_signal), abs(max_signal))

    # Plot x
    plt.figure()
    plt.plot(signal)
    plt.plot(m_hat)
    plt.axis('tight')
    plt.xlabel(xlabel_string)
    plt.ylabel(ylabel_String)
    plt.title(fig_title)
    plt.legend([legend_signal_str, legend_envelop_str])
    plt.ylim(-y_label - 1, y_label + 1)
    plt.savefig(plotpath)
    return 0


# PLOTTING FUNCTIONS for RP_EXTRACT features and Audio Waveforms
def plotmatrix(features, xlabel=None, ylabel=None):
    pylab.figure()
    pylab.imshow(features, origin='lower', aspect='auto', interpolation='nearest')
    if xlabel: plt.xlabel(xlabel)
    if ylabel: pylab.ylabel(ylabel)
    pylab.show()


def plotrp(features, reshape=True, rows=24, cols=60):
    if reshape:
        features = features.reshape(rows, cols, order='F')
    plotmatrix(features, 'Modulation Frequency Index', 'Frequency Band [Bark]')


def plotssd(features, reshape=True, rows=24, cols=7):
    if reshape:
        features = features.reshape(rows, cols, order='F')

    pylab.figure()
    pylab.imshow(features, origin='lower', aspect='auto', interpolation='nearest')
    pylab.xticks(range(0, cols), ['mean', 'var', 'skew', 'kurt', 'median', 'min', 'max'])
    pylab.ylabel('Frequency [Bark]')
    pylab.show()


def plotrh(hist, showbpm=True):
    xrange = range(0, hist.shape[0])
    plt.bar(xrange, hist)  # 50, normed=1, facecolor='g', alpha=0.75)

    # plt.ylabel('Probability')
    plt.title('Rhythm Histogram')
    if showbpm:
        mod_freq_res = 1.0 / (2 ** 18 / 44100.0)
        # print type(xrange)
        plotrange = range(1, hist.shape[0] + 1, 5)  # 5 = step
        bpm = np.around(np.array(plotrange) * mod_freq_res * 60.0, 0)
        pylab.xticks(plotrange, bpm)
        plt.xlabel('bpm')
    else:
        plt.xlabel('Mod. Frequency Index')
    plt.show()


""" scale frequency axis logarithmically """


def plotMonoWav(mono_wav_path):
    # -*- coding: utf-8 -*-

    # 打开WAV文档
    f = wave.open(mono_wav_path, "rb")
    # 读取格式信息
    # (nchannels, sampwidth, framerate, nframes, comptype, compname)
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # print nchannels, sampwidth, framerate, nframes
    # 读取波形数据
    str_data = f.readframes(nframes)
    f.close()
    # 将波形数据转换为数组
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data.shape = -1, nchannels
    wave_data = wave_data.T
    time = np.arange(0, nframes) * (1.0 / framerate)
    # 绘制波形
    # pl.subplot(211)
    pl.plot(time, wave_data[0])
    # pl.subplot(212)
    # pl.plot(time, wave_data[1], c="g")
    pl.xlabel("time (seconds)")
    pl.show()

    return 0


def plotDuralWav(dural_wav_path):
    # 打开WAV文档
    f = wave.open(dural_wav_path, "rb")
    # 读取格式信息
    # (nchannels, sampwidth, framerate, nframes, comptype, compname)
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # print nchannels, sampwidth, framerate, nframes
    # 读取波形数据
    str_data = f.readframes(nframes)
    f.close()
    # 将波形数据转换为数组
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data.shape = -1, nchannels
    wave_data = wave_data.T
    time = np.arange(0, nframes) * (1.0 / framerate)
    # 绘制波形
    pl.subplot(211)
    pl.plot(time, wave_data[0])
    pl.subplot(212)
    pl.plot(time, wave_data[1], c="g")
    pl.xlabel("time (seconds)")
    pl.show()

    return 0


if __name__ == '__main__':
    plotDuralWav('/Users/zhangxulong/Desktop/_download_test.m4a')
