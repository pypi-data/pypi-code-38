"""
 * Copyright (c) 2018 QuantumCore Inc.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *    http://www.apache.org/licenses/LICENSE-2.0
 * 
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 """

import numpy as np
import json
import os


class _Bunch(dict):
    def __init__(self, **kwargs):
        super(_Bunch, self).__init__(kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __dir__(self):
        return self.keys()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setstate__(self, state):
        pass


def load_jpvow():
    """
    Japanese Vowels Data Set
    https://archive.ics.uci.edu/ml/datasets/Japanese+Vowels
    :return: scikit-learn data type(_Bunch-class)
    """
    _target_names = [
        "taro",
        "jiro",
        "saburo",
        "shiro",
        "goro",
        "mutuo",
        "shichiro",
        "hachiro",
        "kuro",
    ]
    with open(os.path.dirname(__file__) + "/data/jpvow_train_x.json", "r") as f:
        X = json.load(f)
    with open(os.path.dirname(__file__) + "/data/jpvow_train_y.json", "r") as f:
        Y = json.load(f)
    with open(os.path.dirname(__file__) + "/data/jpvow_test_x.json", "r") as f:
        Xte = json.load(f)
    with open(os.path.dirname(__file__) + "/data/jpvow_test_y.json", "r") as f:
        Yte = json.load(f)

    _data = np.concatenate((X, Xte), axis=0)
    _target = np.concatenate((Y, Yte), axis=0)
    return _Bunch(
        data=np.array(_data),
        target=np.array(_target),
        target_names=np.array(_target_names),
        feature_names=[
            "lpc1",
            "lpc2",
            "lpc3",
            "lpc4",
            "lpc5",
            "lpc6",
            "lpc7",
            "lpc8",
            "lpc9",
            "lpc10",
            "lpc11",
            "lpc12",
        ],
    )

