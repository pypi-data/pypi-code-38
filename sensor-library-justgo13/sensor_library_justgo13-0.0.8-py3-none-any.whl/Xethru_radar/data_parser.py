import numpy as np
import matplotlib.pyplot as plt
import csv


def iq_data(filename,csvname):
    """
    Takes binary data file and iterates through in-phase (real) and quadrature (imaginary) values.
    Data from range bins is taken and in-phase values are matched with quadrature values to be stored in a user defined .csv file.

    :parameter:

    filename: str
        The .dat binary file name.
    csvname: str
        User defined .csv file name

    :example:

    >>> iqdata(X4data.dat)
    >>> 'converted'

    :returns:

    In-phase and quadrature pairs stored together in a .csv file.
    """
    with open(filename, "rb") as f:
        data = np.fromfile(f, dtype=np.float32)
    for i in range(0, len(data) // 363 - 1):
        temp = data[3 * (i + 1) + 360 * i:3 * (i + 1) + 360 * (i + 1)]
        iqdata = []
        for j in range(0, 180):
            if temp[j + 180] > 0:
                iqdata.append(str(round(temp[j], 4)) + "+" + str(round(temp[j + 180], 4)) + "j")
            else:
                iqdata.append(str(round(temp[j], 4)) + str(round(temp[j + 180], 4)) + "j")

        with open(csvname+'.csv', 'a', newline="") as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(iqdata)
    f.close()
    csvFile.close()
    print('converted')


def raw_data(filename,csvname):
    """
    Takes raw data file and iterates through in-phase (real) and quadrature (imaginary) values.
    Data from range bins is taken, and in-phase value are put apart from quadrature in a user defined .csv file.

    :parameter

    filename: str
        The .dat binary file name.
    csvname: str
        User defined .csv file name

    :example:

    >>> raw_data(X4data.dat)
    >>> 'converted'

    :returns:

    In-phase and quadrature stored separately in a .csv file.
    """
    with open(filename, "rb") as f:
        data = np.fromfile(f, dtype=np.float32)
    for i in range(0, len(data) // 1473 - 1):
        temp = data[3 + 1470 * i:3 + 1470 * (i + 1)]

        with open(csvname+'.csv', 'a', newline="") as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(temp)
    f.close()
    csvFile.close()
    print('converted')
