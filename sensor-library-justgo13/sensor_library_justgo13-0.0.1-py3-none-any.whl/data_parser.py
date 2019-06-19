import numpy as np
import matplotlib.pyplot as plt
import csv


def iq_data(filename):
    """
    Takes binary data file and iterates through in-phase and quadrature values, real and imaginary.
    Data from 180 range bins is taken and in-phase value are matched with their quadrature values.

    :example:

    >>> iqdata(filename)
    >>> 1

    :returns:

    In-phase and quadrature pairs stored together in a .csv file.
    """
    with open('data.dat', "rb") as f:
        data = np.fromfile(f, dtype=np.float32)
    for i in range(0, len(data) // 363 - 1):
        temp = data[3 * (i + 1) + 360 * i:3 * (i + 1) + 360 * (i + 1)]
        iqdata = []
        for j in range(0, 180):
            if temp[j + 180] > 0:
                iqdata.append(str(round(temp[j], 4)) + "+" + str(round(temp[j + 180], 4)) + "j")
            else:
                iqdata.append(str(round(temp[j], 4)) + str(round(temp[j + 180], 4)) + "j")

        with open('iqdata.csv', 'a', newline="") as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(iqdata)
    f.close()
    csvFile.close()
    return 1


def raw_data(filename):
    """
    Takes raw data file and iterates through in-phase and quadrature values, real and imaginary.
    Data from 180 range bins is taken and in-phase value are put apart from quadrature matches.

    :example:

    >>> raw_data(filename)
    >>> 1

    :returns:

    In-phase and quadrature stored separately in a .csv file.
    """
    with open('data.dat', "rb") as f:
        data = np.fromfile(f, dtype=np.float32)
    for i in range(0, len(data) // 1473 - 1):
        temp = data[3 + 1470 * i:3 + 1470 * (i + 1)]

        with open('rawdata.csv', 'a', newline="") as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(temp)
    f.close()
    csvFile.close()
    return 1
