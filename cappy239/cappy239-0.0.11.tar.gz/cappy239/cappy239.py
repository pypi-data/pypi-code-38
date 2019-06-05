import numpy as np
import math
import matplotlib.pyplot as plt

# class Cappy239(object):
# def __init__(self): 
#     print('Instance created...')

def normalize(x):
    return ((x - min(x)) / (max(x) - min(x)) - 0.5) * 2


def powernoise(beta, N, varargin='normalize'):
    N2 = int(N / 2 - 1)
    f = np.arange(2, (N2 + 1) + 1, 1)
    A2 = 1.0 / (f ** (beta / 2.0))

    if varargin == 'normalize':
        p2 = (np.random.uniform(0, 1, N2) - 0.5) * 2 * math.pi
        d2 = A2 * np.exp(1j * p2)
    else:
        p2 = np.random.rand(N2) + 1j * np.random.rand(N2)
        d2 = A2 * p2

    d = np.concatenate(([1], d2, [1.0/((N2 + 2.0) ** beta)], np.flipud(np.conjugate(d2))))
    x = np.real(np.fft.ifft(d))

    if varargin == 'normalize':
        x = normalize(x)

    return x

def plot_noise(serie, beta=0, save=False):

    title, color, width, height = '', '', 17, 5
    
    if beta == 0:
        title = 'White Noise β=0'
        color = '#0100FF'
    elif beta == 1:
        title = 'Pink Noise β=1'
        color = 'hotpink'
    elif beta == 2:
        title = 'Red Noise β=2'
        color = 'red' 

    plt.figure(figsize=(width, height))
    plt.title(title, fontdict={'fontsize': '25'}, y=1.03)
    plt.xlabel('Time', fontdict={'fontsize': '15'})
    plt.ylabel('Amplitude', fontdict={'fontsize': '15'})
    plt.plot(serie, color=color)
    if save:
        plt.savefig('./images/s2.png', format='png', dpi=400)
    plt.show()

def plot_chaotic(serie, save=False):   
    plt.figure(figsize=(17, 5))
    plt.title('Logistic Map ', fontdict={'fontsize': '25'}, y=1.03)
    plt.xlabel('N', fontdict={'fontsize': '25'})
    plt.plot(serie, color='#0000FF')
    
    if save:
        plt.savefig('./images/s4.png', format='png', dpi=400)
    
    plt.show()




def logistic_map(rho, a0, n):
    a = np.zeros(n)
    a[0] = a0
    for n in range(0, n-1, 1):
        a[n+1] = rho * a[n] * (1 - a[n])
    return a

def pmodel(noValues=256, p=0.375, slope=None):

    noOrders = math.ceil(math.log2(noValues))
    noValuesGenerated = math.pow(2, noOrders)

    y = np.array([1])
    for n in range(noOrders):
        y = next_step_1d(y, p)

    if slope:
        fourierCoeff = fractal_spectrum_1d(noValues, slope / 2)
        meanVal = np.mean(y)
        stdy = np.std(y)
        x = np.fft.ifft(y - meanVal)
        phase = np.angle(x)
        x = fourierCoeff * np.exp(1j * phase)
        x = np.real(np.fft.fft(x))
        x = x * stdy / np.std(x)
        x = x + meanVal
    else:
        x = y

    y = y[0:noValues + 1]
    x = x[0:noValues + 1]

    # return x
    return np.round(x, decimals=8)

def next_step_1d(y, p):
    len_ = len(y)
    y2 = np.zeros(len_ * 2)

    sign = np.random.uniform(0, 1, len_) - 0.5
    sign /= abs(sign)
    y2[::2] = y + sign * (1 - 2 * p) * y
    y2[1::2] = y - sign * (1 - 2 * p) * y

    return y2


def fractal_spectrum_1d(noValues, slope):
    ori_vector_size = noValues
    ori_half_size = ori_vector_size // 2

    a = np.zeros(ori_vector_size)

    for t2 in range(1, (ori_half_size + 1) + 1, 1):
        index = t2 - 1
        t4 = 2 + ori_vector_size - t2
    
        if t4 > ori_vector_size:
            t4 = t2
    
        if index == 0:
            coeff = 1
        else:
            coeff = index ** slope
        a[t2 - 1] = coeff
        a[t4 - 1] = coeff

    a[0] = 0
    return a
