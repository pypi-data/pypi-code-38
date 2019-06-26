# -*- coding: utf-8 -*-
""" Multinomial proportion confidence interval for pandas dataframes

Created on Fri Mar 28 12:07:07 2019

Author: Marco Bellini
License: BSD-3
"""

from unittest import TestCase
from numpy.testing import assert_allclose


import numpy as np
from scipy import stats
import pandas as pd
from df_multinomial import multinomial_proportions_confint_df, gen_ci_label
from statsmodels.stats.proportion import multinomial_proportions_confint

class TestMultinomial_proportions_confint_df(TestCase):

    def test_1row(self):
        """
        tests a 1-row DataFrame

        :return:
        """

        in_df = pd.DataFrame(np.array([[ 1,  2,  1, 10]]),columns=[1,2,3,4])
        output = pd.DataFrame(np.array([[0.00886303, 0.02964269, 0.00886303, 0.38886499, 0.39820861, 0.47625034, 0.39820861, 0.90759919]]),
                          columns = ['lb_1', 'lb_2','lb_3','lb_4', 'ub_1', 'ub_2','ub_3','ub_4'])

        out_df=multinomial_proportions_confint_df(in_df, alpha=0.05)
        assert_allclose(output.values,out_df.values, rtol=1e-06, err_msg="test_1row: values ")
        self.assertSequenceEqual(list(output.columns), list(out_df.columns), 'test_1row: different columns')

    def test_3rows(self):
        """
        tests a 3-row DataFrame

        :return:
        """

        in_df = pd.DataFrame(np.array([[1, 2, 1, 10],[ 4, 50,  1, 20], [400,50,133,15] ]))
        output = pd.DataFrame(np.array(
            [[0.00886303, 0.02964269, 0.00886303, 0.38886499, 0.39820861, 0.47625034, 0.39820861, 0.90759919],
             [0.01654455, 0.52260908, 0.0016451, 0.16073701, 0.15872367,  0.78512666, 0.09976654, 0.40843295]
             [0.61930197, 0.05945823, 0.182921, 0.01335789, 0.71500309, 0.11636395, 0.26762712, 0.04661599]]) ,
            columns = ['lb_1', 'lb_2','lb_3','lb_4', 'ub_1', 'ub_2','ub_3','ub_4'])

        out_df = multinomial_proportions_confint_df(in_df, alpha=0.05)
        assert_allclose(output.values, out_df.values, rtol=1e-06, err_msg="test_3rows: values ")
        self.assertSequenceEqual(list(output.columns), list(out_df.columns),'test_3rows: different columns')

    def test_df_loc(self):
        # tests the df subsetting including subsetting the index

        subsample_index=2
        nc = 4
        nr = subsample_index*16
        alpha=0.01

        a = np.arange(0, nr * nc).reshape(nr, nc)
        df_all = pd.DataFrame(a, columns=np.arange(0, nc))

        df_sub=df_all.loc[::subsample_index,:]

        in_values=df_sub.values
        out_values=np.zeroes((nr/subsample_index,2*nc))

        for nl in range(0,in_values.shape[0]):
            ci=multinomial_proportions_confint(in_values[nl,:],alpha=alpha,method='goodman'  )
            out_values[nl, 0:nc] = ci[:, 0]
            out_values[nl, nc:-1] = ci[:, 1]

        output_sm=pd.DataFrame(out_values,gen_ci_label(df_all.columns,'lb')+gen_ci_label(df_all.columns,'ub'))

        out_df = multinomial_proportions_confint_df(df_sub, alpha=alpha)
        assert_allclose(output_sm.values, out_df.values, rtol=1e-07, err_msg="test_df_loc ")
        self.assertSequenceEqual(list(output_sm.columns), list(out_df.columns), 'test_df_loc: different columns')
        self.assertSequenceEqual(list(output_sm.index), list(out_df.index), 'test_df_loc: different indices')


            # def test_multinomial_proportions_confint_df(self):
    #     self.fail()

    def test_df_mean(self):
        #TODO: add the testing of the mean

        pass


if __name__ == '__main__':
    unittest.main()