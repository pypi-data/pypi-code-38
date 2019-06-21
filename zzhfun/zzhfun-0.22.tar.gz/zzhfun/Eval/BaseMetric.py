# coding=utf-8
from .CfMetric import CfMetric
from .PSI import calc_psi_list
#from Tools.ListTools import *
import numpy as np
import sys
sys.dont_write_bytecode = True

# 入参是array，不是pandas
class BaseMetric:
    def __init__(self, score):
        assert isinstance(score, (list, np.ndarray)), "support list_like score only (for now)"
        self.score = np.array(score)

    def get_ks(self, label, list_=False,  bad_rate=False):
        assert isinstance(label, (list, np.ndarray)), "support list_like score only (for now), current label type=" + str(type(label))
        assert len(self.score) == len(label), "label dimension is not matching.."
        label = np.array(label)
        re = CfMetric(y_true=label, y_score=self.score)
        if list_:
            print(re.ks_list)
        if bad_rate:
            tot_bad = sum(label == 0)
            tot_good = sum(label == 1)
            bad_rate = tot_bad * 1.0 / len(self.score)
            return re.ks, bad_rate, tot_bad, tot_good
        return re.ks

    def get_percentile(self, p):
        # assert is_number_list(p, threshold=100), 'p should be list of number, [0, 100]'
        return np.percentile(self.score, p)

    def min(self):
        return self.score.min()

    def max(self):
        return self.score.max()


# PSI
def get_psi(data, data2, bins=10, list_=False):
    cs = calc_psi_list(data, data2, nbins=bins)
    if list_:
        print(cs["psi_value"])
    return cs["psi_value"].sum()

if __name__ == "__main__":
    pass





