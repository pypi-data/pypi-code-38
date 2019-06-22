import numpy as np
import scipy as sp
import librosa, sys
from pathlib import Path
from pysndfx import AudioEffectsChain
from librosa import load
from scipy import fftpack as fp

WINDOW_LENGTH = 2048
HOP_SIZE = 1024
ALPHA = 0.98
START_FRAME = 12
SLOPE = 0.9
THRESHOLD = 10
MAX_SIGNAL_LENGTH = 400_000

np.seterr(divide='ignore', invalid='ignore')

def filter(audio, sr, filename="jack-audio.wav", signal_length=MAX_SIGNAL_LENGTH):
    """
    Performs Wiener Filtering on a file located at filepath
    :param clean_signal: 1D numpy array containing the signal of a clean audio file
    :param sr: sample rate of audio
    :param filename: string of the audio file name
    :param signal_length: int representing # of samples to cut audio down to; defaults to 400000
    """
    if len(audio) > signal_length:
        audio = audio[:signal_length]
    write_name = filename.split(".")[0]

    stft_noisy, DD_gains, noise_est = DD(audio)
    TSNR_sig, TSNR_gains = TSNR(stft_noisy, DD_gains, noise_est)
    signal_est = HRNR(stft_noisy, TSNR_sig, TSNR_gains, noise_est)
    signal_est = highpass(signal_est, sr)

    new_path = "audio/test_audio_results/" + write_name + "_reduced.wav"
    wavwrite(new_path, signal_est, sr)

def DD(noisy_signal, alpha=ALPHA, start_frame=START_FRAME):
    """
    Reconstructs the signal by re-adding phase components to the magnitude estimate
    :param noisy_signal: 1D numpy array containing the noisy signal in the time domain
    :param alpha: smoothing constant, defaults to 0.98
    :param start_frame: last frame of sound to consider as noise sample
    :return:
        stft_noisy: stft of original noisy signal
        DD_gains: ndarray containing gain for each bin in the signal
        noise_estimation: 1D numpy array containing average noise up to start_frame
    """

    #make stft of time-domain noisy signal
    stft_noisy = librosa.stft(noisy_signal, win_length=WINDOW_LENGTH, hop_length=HOP_SIZE)

    #calculate average noise over the first n frames of the signal
    noise_estimation = np.mean(np.abs(stft_noisy[:, :start_frame-1]), axis=1)

    #initialization
    filter_gain = np.ones(noise_estimation.shape)
    last_prior_snr = np.zeros(filter_gain.shape)
    last_post_snr = np.zeros(filter_gain.shape)
    num_frames = stft_noisy.shape[1]
    DD_gains = []

    new_sig = np.ones(stft_noisy.shape)

    for frame_number in range(num_frames):
        noisy_frame = np.abs(stft_noisy[:, frame_number])

        #calculate current bin's SNR_post
        post_snr = np.divide(np.square(noisy_frame), noise_estimation)

        #calculate current bin's SNR_prior
        prior_snr = (alpha * last_prior_snr) + (1 - alpha) * post_snr

        #store SNR_post and SNR_prior for next bin
        last_post_snr = post_snr.copy()
        last_prior_snr = prior_snr.copy()

        #calculate the current bin's gain
        filter_gain = np.divide(prior_snr, prior_snr + 1)
        DD_gains.append(filter_gain)
        new_sig[:, frame_number] = filter_gain * new_sig[:, frame_number]

    return stft_noisy, np.asarray(DD_gains).T, noise_estimation

def HRNR(noisy_stft, TSNR_spectrum, TSNR_gains, noise_estimation, NL="max"):
    """
    Reconstructs the signal by re-adding phase components to the magnitude estimate
    :param noisy_stft: stft of original noisy signal
    :param TSNR_spectrum: clean stft returned by TSNR
    :param TSNR_gains: gains of each stft frame returned by TSNR
    :param noise_estimation: noise estimation average based on first n frames of noisy signal
    :param NL: string representing the non-linear function to be applied to TSNR_spectrum
    :return:
        signal_output: stft of signal after TSNR modification
        TSNR_gains: ndarray containing gain for each bin in signal_output
    """

    # applying non-linear function to TSNR_spectrum
    harmo_spectrum = TSNR_spectrum.copy()
    if NL == "abs":
        harmo_spectrum = np.abs(harmo_spectrum)
    else:
        harmo_spectrum[harmo_spectrum <= 0] = 0.01

    # initialization
    num_frames = TSNR_spectrum.shape[1]
    output_spectrum = np.zeros(TSNR_spectrum.shape, dtype=complex)

    for frame_number in range(num_frames):
        noisy_frame = np.abs(TSNR_spectrum[:, frame_number])
        harmo_frame = np.abs(harmo_spectrum[:, frame_number])
        gain_TSNR = TSNR_gains[:, frame_number]

        # calculate prior SNR
        A = gain_TSNR * (np.abs(noisy_frame) ** 2)
        B = (1 - gain_TSNR) * (np.abs(harmo_frame) ** 2)
        SNR_prior = (A + B) / noise_estimation

        # calculate new gain and apply
        HRNR_gain = np.divide(SNR_prior, SNR_prior + 1)
        output_spectrum[:, frame_number] = noisy_stft[:,
                                                      frame_number] * HRNR_gain

    return librosa.istft(output_spectrum, hop_length=HOP_SIZE, win_length=WINDOW_LENGTH)

def TSNR(noisy_stft, signal_gains, noise_estimation):
    """
    Reconstructs the signal by re-adding phase components to the magnitude estimate
    :param noisy_stft: stft of original noisy signal
    :param signal_gains: gains of each stft frame returned by DD
    :param noise_estimation: noise estimation average based on first n frames of noisy signal
    :return:
        signal_output: stft of signal after TSNR modification
        TSNR_gains: ndarray containing gain for each bin in signal_output
    """

    num_frames = noisy_stft.shape[1]
    signal_output = np.zeros(noisy_stft.shape, dtype=complex)
    TSNR_gains = []

    for frame_number in range(num_frames):
        noisy_frame = np.abs(noisy_stft[:, frame_number])

        #Calculating SNR_prior for current frame
        numerator = (signal_gains[:, frame_number] * noisy_frame) ** 2
        prior_SNR = numerator / noise_estimation

        #Calculating TSNR filter_gain for current frame
        TSNR_gain = np.divide(prior_SNR, prior_SNR + 1)
        TSNR_gains.append(TSNR_gain)

        signal_output[:, frame_number] = TSNR_gain * noisy_stft[:, frame_number]

    return signal_output, np.asarray(TSNR_gains).T

def highpass(sig, sr, high_thresh=THRESHOLD):
    """
    Passes signal through a highpass filter
    :param sig: signal to be highpassed
    :param sr: sample rate of the signal
    :param high_thresh: Threshold above which frequencies should be highpassed out
    :return:
        1d numpy array containing the filtered signal
    """

    spec_cent = librosa.feature.spectral_centroid(y=sig, sr=sr)
    spec_med = round(np.median(spec_cent))

    high_thresh *= spec_med
    if high_thresh > sr/2:
        high_thresh = sr/2
    rem_noise = AudioEffectsChain().highshelf(frequency=high_thresh, slope=SLOPE)

    return rem_noise(sig)

def wavwrite(filepath, data, sr, norm=True, dtype='int16'):
    if norm:
        data /= np.max(np.abs(data))
    data = data * np.iinfo(dtype).max
    data = data.astype(dtype)
    sp.io.wavfile.write(filepath, sr, data)

def snr(reduced_signal, original_signal):
    stft_original = librosa.stft(original_signal, win_length=WINDOW_LENGTH, hop_length=HOP_SIZE)
    stft_reduced = librosa.stft(reduced_signal, win_length=WINDOW_LENGTH, hop_length=HOP_SIZE)

    seg_snr = 0
    for frame in range(stft_original.shape[1]):
        original_slice = fp.ifft(stft_original[:, frame])
        reduced_slice = fp.ifft(stft_reduced[:, frame])
        numerator = np.sum(np.square(np.abs(original_slice)))
        denominator = np.sum(np.square(np.abs(reduced_slice) - np.abs(original_slice)))
        seg_snr += numerator / denominator

    seg_snr = (1 / stft_original.shape[1]) * seg_snr
    return str(seg_snr)