import librosa
import numpy as np


def calc_Spectral_Centroid(wav_path):
    y, sr = librosa.load(wav_path)
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    return cent


def calc_Spectral_Bandwidth(wav_path):
    y, sr = librosa.load(wav_path)
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)

    return spec_bw


def calacSpectral_Contrast(wav_path):
    y, sr = librosa.load(wav_path)
    S = np.abs(librosa.stft(y))
    contrast = librosa.feature.spectral_contrast(S=S, sr=sr)

    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.subplot(2, 1, 1)
    # librosa.display.specshow(librosa.amplitude_to_db(S, ref=np.max), y_axis='log')
    # plt.colorbar(format='%+2.0f dB')
    # plt.title('Power spectrogram')
    # plt.subplot(2, 1, 2)
    # librosa.display.specshow(contrast, x_axis='time')
    # plt.colorbar()
    # plt.ylabel('Frequency bands')
    # plt.title('Spectral contrast')
    # plt.tight_layout()
    return contrast


def calc_RMSE(wav_path):
    y, sr = librosa.load(wav_path)
    rmse = librosa.feature.rmse(y=y)
    return rmse


def calc_Spectral_Rolloff(wav_path):
    y, sr = librosa.load(wav_path)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    return rolloff


def calc_Poly_Features(wav_path, order=0):
    y, sr = librosa.load(wav_path)
    S = np.abs(librosa.stft(y))
    p = librosa.feature.poly_features(S=S, order=order)
    return p


def calc_Zero_crossing_rate(wav_path):
    y, sr = librosa.load(wav_path)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
    return zero_crossing_rate
