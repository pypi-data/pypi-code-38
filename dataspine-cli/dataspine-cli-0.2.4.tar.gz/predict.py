#-*- coding: utf-8 -*-
import os
import json
import ssl
import click
import requests
import subprocess as _subprocess
from urllib.request import urlopen
import os.path
from utils import API_URL_BASE, API_SERVER
from utils import get_header_basic_auth
from model import model_endpoint
from pprint import pprint
#import matplotlib.pyplot as plt


@click.group()
def predict():
    """The family commands to work with predict"""
    pass


# @predict.command('create-route')
# #@click.option('--cluster name', 'cluster', prompt='Cluster name', help='The name of the cluster')
# @click.option('--model-name', 'model', prompt='Model name', help='The name of the model')
# @click.option('--weights', 'model_split_tag_and_weight_dict', prompt='Weights with model tags', help='Provide weights along with model tags i.e. {"a": 100, "b": 0, "c": 0}')
# @click.option('--shadow-weights', 'model_shadow_tag_list', prompt='Shadow model tags', help='Provide shadow model tags i.e. [b, c] Note: must set b and c to traffic split 0 above')
# def routetraffic(model, model_split_tag_and_weight_dict, model_shadow_tag_list):
#     """Route traffic between different versions"""

#     url = API_URL_BASE + '/predict-route'
#     headers = get_header_basic_auth()
#     #print(model_split_tag_and_weight_dict)
#     body = {
#         'model_split_tag_and_weight_dict': model_split_tag_and_weight_dict,
#         'model_shadow_tag_list': model_shadow_tag_list,
#         'model_name': model,
#     }
#     try:
#         response = requests.post(url, headers=headers, json=body).json()
#         print('Status:' , response['status'])
#         print('Routes:',  response['new_traffic_split_routes'])
#         print('Shadow tags:', response['new_traffic_shadow_routes'])

#     except KeyError:
#         error = 'Something went wrong'
#         print(error)

@predict.command('create-route')
@click.option('--account-id', 'account_id', prompt='Account ID', help='Account ID')
@click.option('--model-name', 'model', prompt='Model name', help='The name of the model')
@click.option('--weights', 'model_split_tag_and_weight_dict', prompt='Weights with model tags', help='Provide weights along with model tags i.e. {"a": 100, "b": 0, "c": 0}')
@click.option('--shadow-weights', 'model_shadow_tag_list', prompt='Shadow model tags', help='Provide shadow model tags i.e. [b, c] Note: must set b and c to traffic split 0 above')
def routetraffic(model, model_split_tag_and_weight_dict, model_shadow_tag_list, account_id):
   """Route traffic between different versions"""

   url = API_URL_BASE + '/predict-route'
   headers = get_header_basic_auth()
   #print(model_split_tag_and_weight_dict)
   body = {
       'model_split_tag_and_weight_dict': model_split_tag_and_weight_dict,
       'model_shadow_tag_list': model_shadow_tag_list,
       'model_name': model,
       'account_id': account_id,
   }
   try:
       response = requests.post(url, headers=headers, json=body).json()
       print('Status:' , response['status'])
       print('Routes:',  response['new_traffic_split_routes'])
       print('Shadow tags:', response['new_traffic_shadow_routes'])

   except KeyError:
       error = 'Something went wrong'
       print(error)



@predict.command('delete-route')
#@click.option('--cluster name', 'cluster', prompt='Cluster name', help='The name of the cluster')
@click.option('--model-name', 'model', prompt='Model name', help='The name of the model')
def deletetraffic(model):
    """Delete traffic routes"""

    url = API_URL_BASE + '/traffic/delete'
    headers = get_header_basic_auth()
    #print(model_split_tag_and_weight_dict)
    body = {
        'model_name': model,
    }
    try:
        response = requests.delete(url, headers=headers, json=body).json()
        print('Status:' , response['message'])

    except KeyError:
        error = 'Something went wrong'
        print(error)



@predict.command('http-test')
#@click.option('--cluster name', 'cluster', prompt='Cluster name', help='The name of the cluster')
@click.option('--model-name', 'model', prompt='Model name', help='The name of the model')
@click.option('--test-file', 'test_request_path', prompt='Test request file (json)', help='Path for the test request json file' )
@click.option('--test-concurrency', 'test_request_concurrency', prompt='Request concurrency', help='Provide the concurrency required for requests')
def modeltest_http(test_request_path,
                   model,
                   test_request_concurrency,
                   test_request_mime_type='application/json',
                   test_response_mime_type='application/json',
                   test_request_timeout_seconds=1200):
    """Pings the model server with a test request"""

    from concurrent.futures import ThreadPoolExecutor
    url = '{}/predict-kube-endpoint'.format(API_URL_BASE)
    headers = get_header_basic_auth()
    account_id = headers["x-account-uuid"]
    body = {
        'model_name': model,
    }
    test_request_concurrency = int(test_request_concurrency)
    response = requests.get(url, headers=headers, json=body).json()
    model_endpoint_url = response["endpoint_url"]
    endpoint_url = model_endpoint_url.rstrip('/')

    with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
        for _ in range(test_request_concurrency):
            executor.submit(_predict_http_test(endpoint_url=endpoint_url,
                                               model_name = model,
                                               account_id = account_id,
                                               test_request_path=test_request_path,
                                               test_request_mime_type=test_request_mime_type,
                                               test_response_mime_type=test_response_mime_type,
                                               test_request_timeout_seconds=test_request_timeout_seconds))


def _predict_http_test(endpoint_url,
                       model_name,
                       account_id,
                       test_request_path,
                       test_request_mime_type='application/json',
                       test_response_mime_type='application/json',
                       test_request_timeout_seconds=1200):
    test_request_path = os.path.expandvars(test_request_path)
    test_request_path = os.path.expanduser(test_request_path)
    test_request_path = os.path.abspath(test_request_path)
    test_request_path = os.path.normpath(test_request_path)

    full_endpoint_url = endpoint_url.rstrip('/')
    print("")
    print("Predicting with file '%s' using '%s'" %
          (test_request_path, full_endpoint_url))
    print("")

    with open(test_request_path, 'rb') as fh:
        model_input_binary = fh.read()

    host_header = 'predict-%s.%s.svc.cluster.local' % (model_name, account_id)
    headers = {'Content-type': test_request_mime_type,
               'Accept': test_response_mime_type,
               'Host': host_header
               }
    from datetime import datetime

    begin_time = datetime.now()
    response = requests.post(url=full_endpoint_url,
                             headers=headers,
                             data=model_input_binary,
                             timeout=test_request_timeout_seconds)
    end_time = datetime.now()

    if response.text:
        print("")
        pprint(response.text)
        #image = json.loads(response.text)['outputs']['image_mask']
        #plt.imshow(image)
        #plt.show()

    if response.status_code == 200:
        print("")
        print("Success!")
    else:
        print(response.status_code)

    total_time = end_time - begin_time
    print("")
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")

    # return_dict = {"status": "complete",
    #                "endpoint_url": full_endpoint_url,
    #                "test_request_path": test_request_path}

    # if _http_mode:
    #     return _jsonify(return_dict)
    # else:
    #     return return_dict
