import numpy as np
from bgbb.bgbb_likelihood import nb_loglikelihood


def test_nb_loglikelihood():
    res = nb_loglikelihood([0.1, 0.1, 0.2, 0.3], np.r_[3], np.r_[4], np.r_[5])
    assert np.allclose(res, [-6.31032992])
