# -*- coding: utf-8 -*-
# Copyright 2019 by Andrey Ignatov. All Rights Reserved.

import datetime
import time
import base64

BENCHMARK_VERSION = "0-1-0"


def update_info(mode, testInfo):

    from firebase import firebase

    try:

        url = base64.b64decode(b'aHR0cHM6Ly9haS1iZW5jaG1hcmstYWxwaGEuZmlyZWJhc2Vpby5jb20=').decode('ascii')
        firebase_ = firebase.FirebaseApplication(url, None)
        timestamp = getTimeStamp()

        data = {}
        data['tf_version'] = testInfo.tf_version
        data['platform'] = testInfo.platform_info
        data['cpu'] = testInfo.cpu_model
        data['cpu_ram'] = testInfo.cpu_ram
        data['is_cpu_inference'] = 1 if testInfo.is_cpu_inference else 0

        if not testInfo.is_cpu_inference:

            gpu_id = 0
            for gpu_info in testInfo.gpu_devices:
                data["gpu-" + str(gpu_id)] = gpu_info[0]
                data["gpu-" + str(gpu_id) + "-ram"] = gpu_info[1]
                gpu_id += 1

            data['cuda_version'] = testInfo.cuda_version
            data['cuda_build'] = testInfo.cuda_build

        if mode == "launch":
            if testInfo.is_cpu_inference:
                firebase_.patch(url=BENCHMARK_VERSION + '/launch/cpu/' + clean_symbols(data['cpu']) + "/" + timestamp, data=data, connection=None)
            else:
                firebase_.patch(url=BENCHMARK_VERSION + '/launch/gpu/' + clean_symbols(data["gpu-0"]) + "/" + timestamp, data=data, connection=None)

        if mode == "scores":

            if testInfo._type != "training":
                data['inference_score'] = testInfo.results.inference_score
                data['inference_results'] = arrayToString(testInfo.results.results_inference)

            if testInfo._type == "full" or testInfo._type == "training":
                data['training_score'] = testInfo.results.training_score
                data['training_results'] = arrayToString(testInfo.results.results_training)

            if testInfo._type == "full":
                data['ai_score'] = testInfo.results.ai_score

            if testInfo.is_cpu_inference:
                firebase_.patch(url=BENCHMARK_VERSION + '/' + testInfo._type + '/cpu/' + clean_symbols(data['cpu']) + "/" + timestamp, data=data, connection=None)
            else:
                firebase_.patch(url=BENCHMARK_VERSION + '/' + testInfo._type + '/gpu/' + clean_symbols(data["gpu-0"]) + "/" + timestamp, data=data, connection=None)

    except:
        pass


def clean_symbols(s):

    s = s.replace(".", "-")
    s = s.replace("$", "-")
    s = s.replace("[", "-")
    s = s.replace("]", "-")
    s = s.replace("#", "-")
    s = s.replace("/", "-")

    return s


def arrayToString(scores):

    s = ""
    for score in scores:

        score = int(score) if score >= 100 else float(round(100 * score)) / 100
        s += str(score) + " "

    return s[:-1]


def getTimeStamp():
    timestamp = time.time()
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
