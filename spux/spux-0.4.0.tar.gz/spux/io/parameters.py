# # # # # # # # # # # # # # # # # # # # # # # # # #
# Parameters loading and saving using NumPy
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from collections import OrderedDict

def load(filename, names=None, dtypes=None):

    with open(filename, "r") as f:
        lines = f.readlines()

    records = OrderedDict()
    for line in lines:
        try:
            name, value = line.strip().split()
            records[name] = value
        except:
            pass
    return records


def save(data, filename, delimiter="\t"):

    with open(filename, "w") as f:
        f.writelines(
            "%s%s%s\n" % (str(name), delimiter, str(value))
            for name, value in data.items()
        )
