import numpy as np
from .dsp_tools import cal_symbols_qam
from .dsp_tools import cal_scaling_factor_qam
from .dsp_tools import normal_sample
import numba


def biterror(order, receive_msg, tx_msg):
    assert receive_msg.ndim == 1
    assert tx_msg.ndim == 1
    assert len(receive_msg) == len(tx_msg)
    bitnumber = int(np.log2(order))

    cnt = 0

    index = receive_msg != tx_msg
    to_find_recv = receive_msg[index]
    to_find_tx = tx_msg[index]

    for i in range(len(to_find_recv)):
        temp_recv = np.binary_repr(to_find_recv[i], bitnumber)
        temp_tx = np.binary_repr(to_find_tx[i], bitnumber)
        for index in range(len(temp_recv)):
            if temp_recv[index] != temp_tx[index]:
                cnt = cnt + 1
    return cnt / len(receive_msg) / bitnumber


def Q(biterr):
    pass


def evm(receive_symbol, tx_symbol):
    pass


def theory_ber_from_snr(M, is_pdm):
    pass


def snr2osnr(is_pdm):
    pass


def osnr2snr(is_pdm, signal_bandwidth):
    pass


def estimate_snr_using_tx(recive_symbol, tx_symbol, to_normalize=True, head=1024):
    recive_symbol = np.atleast_2d(recive_symbol)
    pol_number = recive_symbol.shape[0]

    tx_symbol = np.atleast_2d(tx_symbol)
    assert recive_symbol.shape == tx_symbol.shape

    recive_symbol = recive_symbol[:, head:-head]
    tx_symbol = tx_symbol[:, head:-head]

    snr = []

    noise_powers = []
    if to_normalize:
        for i in range(pol_number):
            recive_symbol[i, :] = normal_sample(recive_symbol[i, :])
            tx_symbol[i, :] = normal_sample(tx_symbol[i, :])
    else:
        print("please ensure the rx and tx are normalized")

    noise = recive_symbol - tx_symbol

    for i in range(pol_number):
        noise_power = noise[i, :].real ** 2 + noise[i, :].imag ** 2
        noise_power = np.mean(noise_power)

        noise_powers.append(noise_power)

        snr.append(10 * np.log10(1 / noise_power))

    if pol_number == 2:
        total_noise_power = np.sum(noise_powers)
        total_snr = 2 / total_noise_power

        total_snr = 10 * np.log10(total_snr)
        snr.append(total_snr)
        return snr[0], snr[1], snr[2]

    else:
        return snr[0]


def estimate_snr(E, M):
    """Calculate the signal to noise ratio SNR according to formula given in
    _[1]

    Parameters:
    ----------
    E   : array_like
      input field
    M:  : int
      order of the QAM constallation

    Returns:
    -------
    S0/N: : float
        linear SNR estimate

    References:
    ----------
    ...[1] Gao and Tepedelenlioglu in IEEE Trans in Signal Processing Vol 53,
    pg 865 (2005).

    """
    gamma = _cal_gamma(M)
    r2 = np.mean(abs(E) ** 2)
    r4 = np.mean(abs(E) ** 4)
    S1 = 1 - 2 * r2 ** 2 / r4 - np.sqrt(
        (2 - gamma) * (2 * r2 ** 4 / r4 ** 2 - r2 ** 2 / r4))
    S2 = gamma * r2 ** 2 / r4 - 1
    return S1 / S2


def _cal_gamma(M):
    """Calculate the gamma factor for SNR estimation."""
    A = abs(cal_symbols_qam(M)) / np.sqrt(cal_scaling_factor_qam(M))
    uniq, counts = np.unique(A, return_counts=True)
    return np.sum(uniq ** 4 * counts / M)
