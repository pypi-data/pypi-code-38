import numpy


def to_lin(data):
    return 10 ** (data / 10.)


def from_lin(data):
    return 10 * numpy.log10(data)


def mean(data):
    return from_lin(numpy.mean(to_lin(data)))


def subtract(signal, noise):
    return from_lin(to_lin(signal) - to_lin(noise))


def average(datasets):
    lin = to_lin(datasets)
    average = numpy.sum(lin, 0) / len(lin)
    return from_lin(average)

def dBm2Vrms(dbm, R=50.0):
    return numpy.sqrt(0.001*R)*10**(dbm/20)
