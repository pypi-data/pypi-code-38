#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'cnheider'

audio_path = '/home/heider/Data/Datasets/Audio/y.wav'


def main2():
  # import the pyplot and wavfile modules

  import matplotlib.pyplot as plot

  from scipy.io import wavfile

  # Read the wav file (mono)

  samplingFrequency, signalData = wavfile.read(audio_path)

  # Plot the signal read from wav file

  plot.subplot(211)

  plot.title('Spectrogram of a wav file with piano music')

  plot.plot(signalData)

  plot.xlabel('Sample')

  plot.ylabel('Amplitude')

  plot.subplot(212)

  plot.specgram(signalData, Fs=samplingFrequency)

  plot.xlabel('Time')

  plot.ylabel('Frequency')

  plot.show()


def main():
  import matplotlib.pyplot as plt
  import numpy as np

  # Fixing random state for reproducibility
  np.random.seed(19680801)

  dt = 0.0005
  t = np.arange(0.0, 20.0, dt)
  s1 = np.sin(2 * np.pi * 100 * t)
  s2 = 2 * np.sin(2 * np.pi * 400 * t)

  # create a transient "chirp"
  mask = np.where(np.logical_and(t > 10, t < 12), 1.0, 0.0)
  s2 = s2 * mask

  # add some noise into the mix
  nse = 0.01 * np.random.random(size=len(t))

  x = s1 + s2 + nse  # the signal
  NFFT = 1024  # the length of the windowing segments
  Fs = int(1.0 / dt)  # the sampling frequency

  fig, (ax1, ax2) = plt.subplots(nrows=2)
  ax1.plot(t, x)
  Pxx, freqs, bins, im = ax2.specgram(x, NFFT=NFFT, Fs=Fs, noverlap=900)
  # The `specgram` method returns 4 objects. They are:
  # - Pxx: the periodogram
  # - freqs: the frequency vector
  # - bins: the centers of the time bins
  # - im: the matplotlib.image.AxesImage instance representing the data in the plot
  plt.show()


def main3():
  import matplotlib.pyplot as plt
  from scipy import signal
  from scipy.io import wavfile

  sample_rate, samples = wavfile.read(audio_path)
  frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)

  plt.pcolormesh(times, frequencies, spectrogram)
  plt.imshow(spectrogram)
  plt.ylabel('Frequency [Hz]')
  plt.xlabel('Time [sec]')
  plt.show()


def main4():
  import os
  import wave

  import pylab
  def graph_spectrogram(wav_file):
    sound_info, frame_rate = get_wav_info(wav_file)
    pylab.figure(num=None, figsize=(19, 12))
    pylab.subplot(111)
    pylab.title('spectrogram of %r' % wav_file)
    pylab.specgram(sound_info, Fs=frame_rate)
    pylab.savefig('spectrogram.png')

  def get_wav_info(wav_file):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = pylab.frombuffer(frames, 'int16')
    frame_rate = wav.getframerate()
    wav.close()
    return sound_info, frame_rate

  graph_spectrogram(audio_path)


def main5():
  import numpy as np
  import pyqtgraph as pg
  import pyaudio
  from PyQt4 import QtCore, QtGui

  FS = 44100  # Hz
  CHUNKSZ = 1024  # samples

  class MicrophoneRecorder():
    def __init__(self, signal):
      self.signal = signal
      self.p = pyaudio.PyAudio()
      self.stream = self.p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=FS,
                                input=True,
                                frames_per_buffer=CHUNKSZ)

    def read(self):
      data = self.stream.read(CHUNKSZ)
      y = np.fromstring(data, 'int16')
      self.signal.emit(y)

    def close(self):
      self.stream.stop_stream()
      self.stream.close()
      self.p.terminate()

  class SpectrogramWidget(pg.PlotWidget):
    read_collected = QtCore.pyqtSignal(np.ndarray)

    def __init__(self):
      super(SpectrogramWidget, self).__init__()

      self.img = pg.ImageItem()
      self.addItem(self.img)

      self.img_array = np.zeros((1000, CHUNKSZ / 2 + 1))

      # bipolar colormap
      pos = np.array([0., 1., 0.5, 0.25, 0.75])
      color = np.array(
          [[0, 255, 255, 255], [255, 255, 0, 255], [0, 0, 0, 255], (0, 0, 255, 255), (255, 0, 0, 255)],
          dtype=np.ubyte)
      cmap = pg.ColorMap(pos, color)
      lut = cmap.getLookupTable(0.0, 1.0, 256)

      # set colormap
      self.img.setLookupTable(lut)
      self.img.setLevels([-50, 40])

      # setup the correct scaling for y-axis
      freq = np.arange((CHUNKSZ / 2) + 1) / (float(CHUNKSZ) / FS)
      yscale = 1.0 / (self.img_array.shape[1] / freq[-1])
      self.img.scale((1. / FS) * CHUNKSZ, yscale)

      self.setLabel('left', 'Frequency', units='Hz')

      # prepare window for later use
      self.win = np.hanning(CHUNKSZ)
      self.show()

    def update(self, chunk):
      # normalized, windowed frequencies in data chunk
      spec = np.fft.rfft(chunk * self.win) / CHUNKSZ
      # get magnitude
      psd = abs(spec)
      # convert to dB scale
      psd = 20 * np.log10(psd)

      # roll down one and replace leading edge with new data
      self.img_array = np.roll(self.img_array, -1, 0)
      self.img_array[-1:] = psd

      self.img.setImage(self.img_array, autoLevels=False)

  app = QtGui.QApplication([])
  w = SpectrogramWidget()
  w.read_collected.connect(w.update)

  mic = MicrophoneRecorder(w.read_collected)

  # time (seconds) between reads
  interval = FS / CHUNKSZ
  t = QtCore.QTimer()
  t.timeout.connect(mic.read)
  t.start(1000 / interval)  # QTimer takes ms

  app.exec_()
  mic.close()


def main6():
  # !/usr/bin/env python
  # coding: utf-8
  """ This work is licensed under a Creative Commons Attribution 3.0 Unported License.
      Frank Zalkow, 2012-2013 """

  import numpy as np
  from matplotlib import pyplot as plt
  import scipy.io.wavfile as wav
  from numpy.lib import stride_tricks

  """ short time fourier transform of audio signal """

  def stft(sig, frameSize, overlapFac=0.5, window=np.hanning):
    win = window(frameSize)
    hopSize = int(frameSize - np.floor(overlapFac * frameSize))

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)
    samples = np.append(np.zeros(np.floor(frameSize / 2.0)), sig)
    # cols for windowing
    cols = np.ceil((len(samples) - frameSize) / float(hopSize)) + 1
    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(frameSize))

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
        newspec[:, i] = np.sum(spec[:, scale[i]:], axis=1)
      else:
        newspec[:, i] = np.sum(spec[:, scale[i]:scale[i + 1]], axis=1)

    # list center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins * 2, 1. / sr)[:freqbins + 1])
    freqs = []
    for i in range(0, len(scale)):
      if i == len(scale) - 1:
        freqs += [np.mean(allfreqs[scale[i]:])]
      else:
        freqs += [np.mean(allfreqs[scale[i]:scale[i + 1]])]

    return newspec, freqs

  """ plot spectrogram"""

  def plotstft(audiopath, binsize=2 ** 10, plotpath=None, colormap="jet"):
    samplerate, samples = wav.read(audiopath)
    s = stft(samples, binsize)

    sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)
    ims = 20. * np.log10(np.abs(sshow) / 10e-6)  # amplitude to decibel

    timebins, freqbins = np.shape(ims)

    plt.figure(figsize=(15, 7.5))
    plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")
    plt.colorbar()

    plt.xlabel("time (s)")
    plt.ylabel("frequency (hz)")
    plt.xlim([0, timebins - 1])
    plt.ylim([0, freqbins])

    xlocs = np.float32(np.linspace(0, timebins - 1, 5))
    plt.xticks(xlocs,
               ["%.02f" % l for l in ((xlocs * len(samples) / timebins) + (0.5 * binsize)) / samplerate])
    ylocs = np.int16(np.round(np.linspace(0, freqbins - 1, 10)))
    plt.yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])

    if plotpath:
      plt.savefig(plotpath, bbox_inches="tight")
    else:
      plt.show()

    plt.clf()

  plotstft("my_audio_file.wav")


if __name__ == '__main__':
  main()
