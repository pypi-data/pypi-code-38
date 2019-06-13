"""
 * Copyright (c) 2019 QuantumCore Inc.
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
"""
This is a sample code for QuantumCore Engine. 
You can see how accurate and how fast the model is.
In this demo, we use time-series data below:

Japanese Vowels Data Set
https://archive.ics.uci.edu/ml/datasets/Japanese+Vowels
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from pyqcore.client import SimpleQCoreClient
from pyqcore.examples.jpvow import load_jpvow
from sklearn import model_selection
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression


import numpy as np

if __name__ == "__main__":
    # load data
    data = load_jpvow()
    # Train: 80% / Test: 20%
    X_train, X_test, y_train, y_test = model_selection.train_test_split(
        data.data, data.target, test_size=0.2, random_state=1
    )

    print("===QCORE(Sample)===")
    # create API instance
    client = SimpleQCoreClient()
    # get token (
    access_token = client.login(
        username="#USER#", password="#PASS#", endpoint="http://#ENDPOINT#"
    )
    print(access_token)
    # train
    start = time.time()
    print(X_train.shape)
    res = client.classifier_train(X=X_train, Y=y_train, access_token=access_token)
    print(res)
    # test
    res = client.classifier_test(X=X_test, Y=y_test, access_token=access_token)
    print(res)
    # classify
    res = client.classifier_predict(X=X_test, access_token=access_token)
    print("acc=", accuracy_score(y_test.tolist(), res["Y"]))
    print("f1=", f1_score(y_test.tolist(), res["Y"], average="weighted"))
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")

    # compare other models
    X_train = X_train.reshape(len(X_train), -1).astype(np.float64)
    X_test = X_test.reshape(len(X_test), -1).astype(np.float64)
    y_train = np.ravel(y_train)
    y_test = np.ravel(y_test)

    print("===LogisticRegression(Using Sklearn)===")
    start = time.time()
    lr_cls = LogisticRegression(C=9.0)
    lr_cls.fit(X_train, y_train)
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    res = lr_cls.predict(X=X_test)
    print("acc=", accuracy_score(y_test.tolist(), res))
    print("f1=", f1_score(y_test.tolist(), res, average="weighted"))

    print("===MLP(Using Sklearn)===")
    start = time.time()
    mlp_cls = MLPClassifier(hidden_layer_sizes=(100, 100, 100, 10))
    mlp_cls.fit(X_train, y_train)
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    res = mlp_cls.predict(X=X_test)
    print("acc=", accuracy_score(y_test.tolist(), res))
    print("f1=", f1_score(y_test.tolist(), res, average="weighted"))
