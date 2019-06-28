#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from tabletree.tabletree import TableTree, TableNode, TableLink
import pandas as pd

__author__ = "Xi Rossi LUO"
__copyright__ = "Xi Rossi LUO"
__license__ = "mit"


def test():
        tab1_list = list( zip([1,2,3,4], ['M', 'F', 'M', 'F'] ) )
        tab2_list = list( zip(  [1,2,3,4], ['red', 'green', 'yellow', 'blue'] ) )
        tab1 = pd.DataFrame( tab1_list,   columns = ['tab1_v1', 'tab1_v2'])
        tab2 = pd.DataFrame( tab2_list,   columns = ['tab2_v1', 'tab2_v2'])
        tn1 = TableNode('sex', tab1)
        tn2 = TableNode('preference', tab2)
        ttree = TableTree(tn1)
        ttree.addChildren(tn2, TableLink('tab1_v1', 'tab2_v1'))
        assert all( [ a == b for a, b in zip(ttree.getAncestors('preference'), ['sex'] )  ] ), "getAncestors: wrong returns!"
        assert all( [ a == b for a, b in zip(ttree.getOffsprings('sex'), ['preference'] )  ] ), "getOffsprings: wrong returns!"
        df = ttree.findMatched('preference', 'sex', tn1.df.tab1_v2 == 'M')
        df_exp = pd.DataFrame(list(zip([1,3], ['red', 'yellow'])),columns = ['tab2_v1', 'tab2_v2'] )
        df = df.reset_index(drop= True)
        assert  df.equals(df_exp), "findMatched: two DFs don't match!"


