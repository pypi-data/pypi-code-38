from numbers import Real
import numpy as np


def beep(frequency, duration, sample_rate=44100, hanning=True):
    """Generates a sine wave.

    Args:
        frequency (int or float): The frequency of the sine wave.
        duration (int or float): Duration of the beep in seconds.

    Kwargs:
        sample_rate (int or float): Sampling rate for the wave.

    Returns:
        A 1-dimensional numpy array.

    Example:
        Generate a sine wave at 440 Hz and duration of 0.5 seconds:

        >>> my_beep = beep(440, 0.5, 44100)
    """
    sample = np.sin(2 * np.pi * frequency * (np.arange(0, int(duration * sample_rate))) / sample_rate)
    if hanning:
        apply_hanning(sample, sample_rate)
    return sample


def apply_hanning(sample, sample_rate):
    hw_size = int(min(sample_rate // 100, len(sample) // 15))
    hw = np.hanning(2 * hw_size + 1)
    sample[:hw_size] *= hw[:hw_size]
    sample[-hw_size:] *= hw[hw_size + 1:]


def beep_sequence(click_freq=(440, 660, 880, 1220),
                  inter_click_interval=0.5,
                  dur_clicks=0.04,
                  lead_in=0.1,
                  sample_rate=44100,
                  stereo=True):
    """Generate a series of sine waves, similar to a metronome.

    Kwargs:
        click_freq (number, list, tuple, or 1d numpy array): The frequency of each beep.
        inter_click_interval (int or float): The period between the beep midpoints.
        dur_clicks (int or float): Float or int, duration of each beep in seconds.
        lead_in (float): Amount of time in seconds before the center of the first beep.
        sample_rate (int or float): Sampling rate for the wave.
        stereo (bool): Generate audio for two channels.

    Returns:
        A numpy array, 1-dimensional if mono, 2-dimensional (n by 2) if stereo.

    Example:
        To generate four beeps of different frequency and spaced by half a second,

        >>> my_train = beep_sequence([1220, 400, 410, 620], inter_click_interval=0.5)
    """
    if isinstance(click_freq, Real):
        click_freq = [click_freq]
    beeps = [beep(n, duration=dur_clicks, sample_rate=sample_rate) for n in click_freq]
    space = np.zeros(int((inter_click_interval * sample_rate) - len(beeps[0])))
    out = np.zeros((int(sample_rate * lead_in - len(beeps[0]) / 2)))
    out = np.append(out, beeps[0])
    for i in range(len(click_freq) - 1):
        out = np.append(out, space)
        out = np.append(out, beeps[i + 1])
    if stereo:
        out = np.transpose(np.vstack((out, out)))
    return out
