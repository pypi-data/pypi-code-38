""" tools for conerting atoms objects to json representations """

import son

def backup(file):
    """ back up a file"""
    if Path(file).exists():
        if "traj" in str(file):
            raise Exception("Possibly overwriting a trajectory, please check")
        Path(file).rename(f"{file}.bak")


def last_from_yaml(file):
    """ return last entry from yaml file """

    _, data = son.load(file)

    return data[-1]

