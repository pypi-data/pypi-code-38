import numpy as np
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

    >>> iq_data('X4data.dat','X4iq_data')
    >>> 'converted'

    :returns:

    Readable csv file containing complex values.
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
    return 'converted'


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

    >>> raw_data('X4data.dat','X4raw_data')
    >>> 'converted'

    :returns:

    Readable csv files containing raw data.
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
    return 'converted'