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
import jinja2 as _jinja2
import shutil as _shutil


# _default_dataspine_templates_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'templates'))

@click.group()
def model():
    """The family commands to work with model"""
    pass

@model.command()
@click.option('--model-name', 'model_name', prompt="Model name", help='Name of the model')
@click.option('--model-tag', 'model_tag', prompt="Model tag", help='Tag of the model')
@click.option('--model-type', 'model_type', prompt="Model type", help='Type of the model')
@click.option('--model-runtime', 'model_runtime', prompt="Model runtime", help='Runtime of the model')
@click.option('--model-chip', 'model_chip', prompt="Model chip", help='Compute type of the model')
@click.option('--model-path', 'model_path', prompt="Model path", help='Model path')
def init(model_chip, model_tag, model_name, model_runtime, model_type, model_path):
    """Init a model in the cluster"""

    url = '{}/model/init'.format(API_URL_BASE)
    #headers = get_header_basic_auth()

    body = {
        'model_tag': model_tag,
        'model_name': model_name,
        'model_type': model_type,
        'model_runtime': model_runtime,
        'model_chip' : model_chip,
        'model_path' : model_path,
    }
    #_model_subdir_name = 'spine'
    _model_subdir_name = model_name

    model_path = os.path.expandvars(model_path)
    model_path = os.path.expanduser(model_path)
    model_path = os.path.normpath(model_path)
    absolute_model_path = os.path.abspath(model_path)

    if not os.path.exists(absolute_model_path):
        os.makedirs(absolute_model_path)

    #absolute_template_file_path = _os.path.normpath(_os.path.join(templates_base_path, template))
    absolute_model_file_directory = os.path.normpath(os.path.join(absolute_model_path, _model_subdir_name))
    if not os.path.exists(absolute_model_file_directory):
        os.makedirs(absolute_model_file_directory)

    response = requests.get(url, json=body).json()
    for file in response['model_files']:
        with open(file['relative_model_file_path'], 'wt') as fh:
                fh.write(file['file_contents'])
    print ("Model files have been initialized. Please check the project directory")


@model.command('build-manifest')
@click.option('--model-name', prompt='Model name', help='Model Name.')
@click.option('--model-tag', prompt='Model tag', help='Model Tag.')
@click.option('--model-type', prompt='Model type', help='Model Type.')
@click.option('--model-path', prompt='Model path', help='Model Path.')
# @click.option('--model_runtime', prompt = 'Model runtime', help = 'Model runtime.', required = False, default = None)
def buildfiles(model_name, model_tag, model_type, model_path):
    """Build model container"""

    url = API_URL_BASE + '/buildmodel'
    #directory = _subprocess.call('pwd', shell=True)
    request = {
        'model_tag': model_tag,
        'model_name': model_name,
        'model_type': model_type,
        'model_path': model_path,
        # 'model_runtime': model_runtime,
    }

    #print("Building Dockerfile!\n\n")
    response = requests.post(url, request).json()
    build_coordinates = response['build_coordinates']

    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars

    fileContent = urlopen(response['dockerFileUrl'], context=gcontext).read().decode('utf-8')
    basePath = os.path.join(os.path.expanduser(model_path))
    filePath = os.path.join(basePath, response['dockerFileName'])
    Dockerfilepath = os.path.join(basePath, 'Dockerfile')

    f = open(filePath, 'w')
    f.write(fileContent)
    f.close()

    f = open(Dockerfilepath, 'w')
    f.write(fileContent)
    f.close()

    print ("Model files built and are ready to be pushed to Git")



    # cmd = 'docker build %s -f %s %s' % (build_coordinates, filePath, basePath)
    # process = _subprocess.call(cmd, shell=True)
    #  if (response['command']):
    #    print(response['command'])
    #    process = _subprocess.call(response['command'], shell = True)
    #  else:
    #    print("Something went wrong!")
    # print(response)

# @model.command()
# @click.option('--model-name', prompt='Model name', help='Model Name.')
# @click.option('--model-tag', prompt='Model tag', help='Model Tag.')
# @click.option('--model-type', prompt='Model type', help='Model Type.')
# @click.option('--model-path', prompt='Model path', help='Model Path.')
# # @click.option('--model_runtime', prompt = 'Model runtime', help = 'Model runtime.', required = False, default = None)
# def build(model_name, model_tag, model_type, model_path):
#     """Build model container"""

#     url = API_URL_BASE + '/buildfile'
#     directory = _subprocess.call('pwd', shell=True)
#     request = {
#         'model_tag': model_tag,
#         'model_name': model_name,
#         'model_type': model_type,
#         'model_path': model_path,
#         # 'model_runtime': model_runtime,
#     }

#     print("Building Dockerfile!\n\n")
#     response = requests.post(url, request).json()
#     print(response['status'])
    



# @model.command()
# @click.option('--model-name', prompt='Model name', help='Model Name.')
# @click.option('--model-tag', prompt='Model tag', help='Model Tag.')
# @click.option('--model-type', prompt='Model type', help='Model Type.')
# @click.option('--model-path', prompt='Model path', help='Model Path.')
# # @click.option('--model_runtime', prompt = 'Model runtime', help = 'Model runtime.', required = False, default = None)
# def train(model_name, model_tag, model_type, model_path):
#     """Build train container"""

#     url = API_URL_BASE + '/build/trainserver'
#     directory = _subprocess.call('pwd', shell=True)
#     request = {
#         'model_tag': model_tag,
#         'model_name': model_name,
#         'model_type': model_type,
#         'model_path': model_path,
#         # 'model_runtime': model_runtime,
#     }

#     print("Building Dockerfile!\n\n")
#     response = requests.post(url, request).json()
#     build_coordinates = response['build_coordinates']

#     gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars

#     fileContent = urlopen(response['dockerFileUrl'], context=gcontext).read().decode('utf-8')
#     basePath = os.path.join(os.path.expanduser(model_path))
#     filePath = os.path.join(basePath, response['dockerFileName'])

#     f = open(filePath, 'w')
#     f.write(fileContent)
#     f.close()

#     cmd = 'docker build %s -f %s %s' % (build_coordinates, filePath, basePath)
#     process = _subprocess.call(cmd, shell=True)
#     #  if (response['command']):
#     #    print(response['command'])
#     #    process = _subprocess.call(response['command'], shell = True)
#     #  else:
#     #    print("Something went wrong!")
#     # print(response)




@model.command()
@click.option('--model-name', prompt='Model name', help='Model Name.')
@click.option('--model-tag', prompt='Model tag', help='Model Tag.')
def push(model_name, model_tag):
    """Push model to registry"""
    url = API_URL_BASE + '/modelpush'
    request = {
        'model_tag': model_tag,
        'model_name': model_name,
        # 'model_runtime': model_runtime,
    }
    response = requests.post(url, request).json()
    registry_coordinates = response['registry_coordinates']
    cmd = 'docker push %s' % registry_coordinates
    print(cmd)
    print("")
    process = _subprocess.call(cmd, shell=True)


# @model.command()
# @click.option('--git-url', prompt='Git URL', help='Git URL')
# @click.option('--model-name', prompt='Model name', help='Model name')
# @click.option('--model-tag', prompt='Model tag', help='Model tag')
# def build(git_url, model_name, model_tag):
#     """Build model and push to registry"""
#     url = API_URL_BASE + '/model/cbi/build'
#     request = {
#         'git_url': git_url,
#         'model_name': model_name,
#         'model_tag': model_tag,
#         # 'model_runtime': model_runtime,
#     }
#     response = requests.post(url, request).json()

#     #response1 = response.json()
#     print(response['message'])


@model.command()
@click.option('--account-id', 'account_id', prompt='Account ID', help='Account ID')
@click.option('--git-url', prompt='Git URL', help='Git URL')
@click.option('--model-name', prompt='Model name', help='Model name')
@click.option('--model-tag', prompt='Model tag', help='Model tag')
def build(git_url, model_name, model_tag, account_id):
   """Build model and push to registry"""
   url = API_URL_BASE + '/model/cbi/build'
   request = {
       'git_url': git_url,
       'model_name': model_name,
       'model_tag': model_tag,
       'account_id': account_id,
       # 'model_runtime': model_runtime,
   }
   response = requests.post(url, request).json()

   #response1 = response.json()
   print(response['message'])


@model.command('build-logs')
@click.option('--model-name', prompt='Model name', help='Model name')
@click.option('--model-tag', prompt='Model tag', help='Model tag')
def buildlogs(model_name, model_tag):
    url = API_URL_BASE + '/model/logs'
    request = {
         'model_name': model_name,
         'model_tag': model_tag,
    }
    response = requests.post(url, request).json()
    print(response["logs"])



# @model.command()
# @click.option('--model-name', prompt='Model name', help='Model Name.')
# @click.option('--model-tag', prompt='Model tag', help='Model Tag.')
# def pull(model_name, model_tag):
#     """Fetch model from registry"""
#     url = API_URL_BASE + '/modelpull'
#     request = {
#         'model_name': model_name,
#         'model_tag': model_tag,
#     }

#     response = requests.post(url, request).json()
#     pull_coordinates = response['pull_coordinates']
#     cmd = 'docker pull %s' % pull_coordinates
#     print(cmd)
#     print("")
#     process = _subprocess.call(cmd, shell=True)


# @model.command('deploy')
# @click.option('--cluster-name', prompt='Cluster name', help='Cluster name.')
# def deploy(cluster_name):
#     """Deploy the model in your cluster"""
#     url = API_URL_BASE + "/deploy-model"
#     headers = get_header_basic_auth()
#     body_cluster = {
#         "cluster_name": cluster_name
#     }

#     updated = requests.post(url, headers=headers, json=body_cluster)
#     # updated_json = json.loads(updated.text)
#     if updated.status_code != 200:
#         # print(updated_json['message'])
#         print(updated)
#         return

#     print("Model it's already deploy")


@model.command()
#@click.option('--cluster-name', 'cluster_name', prompt='Cluster name', help='The name of the cluster')
#@click.option('--namespace', 'cluster_namespace', prompt='Cluster namespace', help='The namespace in the cluster')
@click.option('--model-tag', 'model_tag', prompt="Model tag", help='Tag of the model')
@click.option('--model-name', 'model_name', prompt="Model name", help='Name of the model')
def deploy(model_tag, model_name):
    """Deploy a model in the cluster"""

    url = '{}/model/deploy'.format(API_URL_BASE)
    headers = get_header_basic_auth()

    body = {
        'model_tag': model_tag,
        'model_name': model_name,
        # 'cluster_name': cluster_name,
        # 'cluster_namespace': cluster_namespace
    }

    response = requests.post(url, headers=headers, json=body)
    response1 = response.json()
    print(response1['message'])




# @model.command()
# @click.option('--model-tag', 'model_tag', prompt="Model tag", help='Tag of the model')
# @click.option('--model-name', 'model_name', prompt="Model name", help='Name of the model')
# def traincluster(model_tag, model_name):
#     """Deploy a training job in the cluster"""

#     url = '{}/build/traincluster'.format(API_URL_BASE)
#     headers = get_header_basic_auth()

#     body = {
#         'model_tag': model_tag,
#         'model_name': model_name,
#     }

#     response = requests.post(url, headers=headers, json=body)
#     response1 = response.json()
#     print(response1['message'])


@model.command('endpoint')
#@click.option('--cluster name', 'cluster', prompt='Cluster name', help='The name of the cluster')
@click.option('--model-name', 'model_name', prompt="Model name", help='Name of the model')
def model_endpoint(model_name):
    """Get the model endpoint"""

    url = '{}/predict-kube-endpoint'.format(API_URL_BASE)
    headers = get_header_basic_auth()
    #headers["cluster_name"] = cluster
    body = {
        'model_name': model_name,
        #'cluster_name': cluster
    }

    response = requests.get(url, headers=headers, json=body).json()
    print("The model's endpoint is", response['endpoint_url'])


@model.command('variants')
@click.option('--model-name', 'model_name', prompt="Model name", help='Name of the model')
def model_variants(model_name):
    """List the model's variants"""

    url = '{}/model/variants'.format(API_URL_BASE)
    headers = get_header_basic_auth()
    body = {
        'model_name': model_name
    }

    response = requests.get(url, headers=headers, json=body).json()
    print("The model's variants are:")
    for f in response['model_variants']:
        print(f)

