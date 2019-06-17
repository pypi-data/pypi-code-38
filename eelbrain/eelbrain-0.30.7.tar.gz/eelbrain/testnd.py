"""Statistical tests for multidimensional data in :class:`NDVar` objects"""
__test__ = False

from ._stats.testnd import (
    NDTest, MultiEffectNDTest,
    t_contrast_rel, corr, ttest_1samp, ttest_ind, ttest_rel, anova,
    Vector, VectorDifferenceRelated,
)
from ._stats.spm import LM, LMGroup
