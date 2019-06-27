from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import pandas as pd
import numpy as np
from typing import *
from ...fluq import *


def default_ax(ax):
    if ax is None:
        _, ax = plt.subplots(1,1)
    return ax
