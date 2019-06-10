#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: violinsolo
# Created on 24/09/2018

import os
import pandas as pd
import numpy as np


def read_all(dataset: str, use_pickle: bool=True, **kwargs) -> pd.DataFrame:
    if not os.path.exists(dataset+'.csv'):
        raise FileNotFoundError
    if use_pickle:
        if os.path.exists(dataset+'.pkl'):
            df = pd.read_pickle(dataset+'.pkl')
        else:
            df = pd.read_csv(dataset+'.csv', **kwargs)
            df.to_pickle(dataset+'.pkl')
    else:
        df = pd.read_csv(dataset + '.csv', **kwargs)

    return df
