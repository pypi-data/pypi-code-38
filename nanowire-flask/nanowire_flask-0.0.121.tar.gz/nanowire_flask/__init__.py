#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 13:12:51 2019

@author: stuart
"""

#nanowire flask plugin tool

import time
from PIL import Image

import unicodedata as uni

import requests

from io import BytesIO

import traceback

import jsonpickle
from flask import request, Response
from flask.views import View

from flask_api import FlaskAPI

import pandas as pd

#memory and cpu usage collection tools

import sys
import os
import re
import psutil
import threading
import socket

py_version = int(sys.version[0])


if py_version == 2:
    import Queue as queue
else:
    import queue


import inspect

import logging

logging.basicConfig(format='%(message)s')

logger = logging.getLogger('NANOWIRE_FLASK_TOOL')

logger.setLevel(level=logging.DEBUG)

mod_path = os.path.abspath(__path__[0])

files = os.listdir(os.path.join(mod_path, '../'))

files[:] = [x for x in files if 'nanowire_flask' in x]

files[:] = [x for x in files if x != 'nanowire_flask']

__version__ = re.findall(r'([0-9]*\.[0-9]*\.[0-9]*)', files[0])[0]

###################
### Admin tools ###
###################

def scrub_newlines(txt):
    
    out = ""
    for char in txt:
        if uni.category(char) != "Cc":
            
            out += char
            
    return out

##############################
### ADVANCED LOGGING TOOLS ###
##############################

class usage_collection(object):
    
    def __init__(self):
        

        #CPUs are collected in % usage
        self.cpus_queue = queue.Queue()
        #memory queue is in MB
        self.mem_queue = queue.Queue()
        self.running = False
    
    def collection_thread(self):
        
        #logger.info("Background thread is STARTING")
        self.running = True
        
        while self.running:
            
            self.cpus_queue.put_nowait(psutil.cpu_percent())
            self.mem_queue.put_nowait(psutil.Process(os.getpid()).memory_info().rss/1e6)
            time.sleep(0.01)
            #logger.info("Background thread is RUNNING")
            
        #logger.info("Background thread is CLOSING")
            
            
    def finish_collection(self):
        
        self.running = False

        cpus = []
        mems = []
        while True:
            try:
                cpus.append(self.cpus_queue.get_nowait())
                mems.append(self.mem_queue.get_nowait())

            except:
                break
        if len(mems) > 0:
        
            max_mem = max(mems)
            max_cpu = max(cpus)
            
        else:
            max_mem = psutil.Process(os.getpid()).memory_info().rss/1e6
            max_cpu = psutil.cpu_percent()
            
        return [max_mem, max_cpu]
    
    def start_collection(self):
        
        threading.Thread(target=self.collection_thread).start()


##############################
### IMAGE PROCESSING TOOLS ###
##############################

def run_image(r, app): 
 
    start_time = time.time()

    #if the user has sent a url then we want to extract that URL like this
    if r.headers['Content-Type'] != 'application/json':
    
        variables_info = dict(r.args)
                
        # convert string of image data to uint8
        im = Image.open(r.files['image']).convert("RGB")

    #if the user has sent an image then lets extract that image and store it as
    #a PIL
    else:
        #extract the variables info sent to the plugin
        variables_info = r.json

        #extract the image from the sent url
        im_request = requests.get(variables_info['contentUrl'])

        im = Image.open(BytesIO(im_request.content)).convert("RGB")
        
        variables_info.pop('contentUrl', None)

    #apply the function to the image
    
    if inspect.getargspec(app.config['function'])[0][-1] == 'variables':
        out_predictions = app.config['function'](im, variables_info)
    else:
        out_predictions = app.config['function'](im)
        
        
    if not isinstance(out_predictions, dict):
        raise Exception("FUNCTION MUST RETURN A DICTIONARY")

    
    #print("Took {0:0.2f} seconds".format(time.time()-start_time))
    
    return out_predictions

#function to check if the user defined function is as it should be
def check_Image_function_is_valid(function):

    args = inspect.getargspec(function)[0]

    if args != ['img', 'variables'] and args != ['self', 'img', 'variables'] and args != ['img'] and args != ['self', 'img']:
        
        return False
        
    else:
        return True


class mount_Image_function(object):
    
    def __init__(self, function, host='0.0.0.0', port=5000, path='/model/predict'):
        
        
        debug_mode = False
        if 'PYTHON_DEBUG' in os.environ:
            if os.environ['PYTHON_DEBUG'].lower() == 'true':
                
                debug_mode = True
        
        self.app = FlaskAPI(__name__)

        self.app.config['debug'] = debug_mode
        
        self.app.config['function'] = function
        
        self.host = host
        
        self.port = port
        
        self.path = path
        
        if check_Image_function_is_valid(self.app.config['function']):
            
            #define the class we're mounting onto post
            tool = ImagesAPI
            
            #if we're in debug mode we will need to collect usage statistics
            if True:
                tool.debug_mode = True
                tool.collection_tool = usage_collection()
            else:
                tool.debug_mode = False
            
            #store a link to the app in tool
            tool.app = self.app
            
            #create the rule for /model/predict
            self.app.add_url_rule(self.path, view_func = tool.as_view('UserAPI'))
            
            #run the app
            self.app.run(host=self.host, port=self.port, debug=self.app.config['debug'])
        
        else:
            #if the function has bad inputs reject it
            raise Exception("BAD ARGUMENTS SENT TO FUNCTION")

    
class ImagesAPI(View):
    
    methods = ['POST']
    
    def dispatch_request(self):
        
        try:
            
            #start usage stats collection
            if True:
                [max_mem, max_cpu] = self.collection_tool.start_collection()
                start_time = time.time()
            
            #run the function
            answer = run_image(request, self.app)
            
            #check a dictionary has been returned
            if not isinstance(answer, dict):
                raise Exception("PLUGIN MUST RETURN A DICTIONARY, RETURNED {0}".format(str(type(answer))))
            
            #grab usage stats
            if True:
                [max_mem, max_cpu] = self.collection_tool.finish_collection()
                
            #store the usage stats
            if True:
                
                answer['max_cpu'] = max_cpu
                answer['max_mem'] = max_mem
                answer['containerID'] = socket.gethostname()
                answer['time_taken'] = round(time.time() - start_time, 2)
                if os.path.exists("/VERSION"):
                    with open("/VERSION", "r") as f:
                        version = scrub_newlines(f.read())    
                    answer["image_version"] = version
                    
                if os.path.exists("/IMAGE_NAME"):
                    with open("/IMAGE_NAME", "r") as f:
                        img_name = scrub_newlines(f.read())
                    answer['image_name'] = img_name
            
            answer['status'] = 'ok'
            
            response_pic = jsonpickle.encode(answer)
            #everything has gone fine, return the results in a nice response
            return Response(response=response_pic, status=200, mimetype="application/json")
        
        except Exception as exp:
            

            response = {'status':'failure', 'error':str(exp)}
            
            #if we're in debug mode then return a full traceback
            if self.app.config['debug']:
                response['full_traceback'] = str(traceback.format_exc())
                
            response_pic = jsonpickle.encode(response)
            
            #something has gone wrong return the bad result in this response
            return Response(response=response_pic, status=400, mimetype='application/json')


###########################################
### Functions for running a text plugin ###
###########################################
    

def run_text(r, app): 

    #if the user has sent a url then we want to extract that URL like this
    if r.headers['Content-Type'] != 'application/json':
    
        variables_info = dict(r.args)
        # convert string of image data to uint8
        text = r.files['doc'].read().decode()

    #if the user has sent an image then lets extract that image and store it as
    #a PIL
    else:
        #extract the variables info sent to the plugin
        variables_info = r.json
        
        #make sure content url is the right case
        #variables_info = map_contenturl2casecorrect(variables_info)

        if 'text' in variables_info.keys():

            #extract the image from the sent url
            text = variables_info['text']
            
            variables_info.pop('text', None)
            
        elif 'contentUrl' in variables_info.keys():
            
            response = requests.get(variables_info['contentUrl'])
                     
            text = response.content.decode()
            
            if response.status_code == 404:
                
                raise Exception("FILE MISSING, CHECK URL OF LINK")
            
            variables_info.pop('contentUrl', None)
            
        else:
            raise Exception("COULD NOT FIND 'contentUrl' OR 'text' IN REQUEST")

    #apply the function to the image
    if inspect.getargspec(app.config['function'])[0][-1] == 'variables':
        out_predictions = app.config['function'](text, variables_info)
    else:
        out_predictions = app.config['function'](text)
        
    if not isinstance(out_predictions, dict):
        raise Exception("FUNCTION MUST RETURN A DICTIONARY")
    
    #return the taskID if it's there
    if 'taskID' in variables_info.keys():
        
        out_predictions['taskID'] = variables_info['taskID']
        
    #print("Took {0:0.2f} seconds".format(time.time()-start_time))
    
    return out_predictions

#function to check if the user defined function is as it should be
def check_text_function_is_valid(function):

    args = inspect.getargspec(function)[0]

    if args != ['text', 'variables'] and args != ['self', 'text', 'variables'] and args != ['text'] and args != ['self', 'text']:
        
        return False
        
    else:
        return True


class mount_text_function(object):
    
    def __init__(self, function, host='0.0.0.0', port=5000, path='/model/predict'):
        
        debug_mode = False
        if 'PYTHON_DEBUG' in os.environ:
            if os.environ['PYTHON_DEBUG'].lower() == 'true':
                
                debug_mode = True
                
        self.app = FlaskAPI(__name__)

        self.app.config['debug'] = debug_mode
        
        self.app.config['function'] = function
        
        self.host = host
        
        self.port = port
        
        self.path = path
        
        if check_text_function_is_valid(self.app.config['function']):
            
            #define the class we're mounting onto post
            tool = TextAPI
            
            #if we're in debug mode we will need to collect usage statistics
            if True:
                tool.debug_mode = True
                tool.collection_tool = usage_collection()
            else:
                tool.debug_mode = False
            #store a link to the app in tool
            tool.app = self.app
            
            #create the rule for /model/predict
            self.app.add_url_rule(self.path, view_func = tool.as_view('UserAPI'))
            
            #run the app
            self.app.run(host=self.host, port=self.port, debug=self.app.config['debug'])
        
        else:
            #if the function has bad inputs reject it
            raise Exception("BAD ARGUMENTS SENT TO FUNCTION")

    
class TextAPI(View):
    
    #this is a post method
    methods = ['POST']
    
    def dispatch_request(self):
        
        try:
            
            #start collecting usage stats
            if True:
                #logger.info("STARTING DATA COLLECTION")
                self.collection_tool.start_collection()
                start_time = time.time()
            
            #run the mounted function
            answer = run_text(request, self.app)
            
            #collect the usage stats
            if True:
                #logger.info("FINISHING DATA COLLECTION")
                [max_mem, max_cpu] = self.collection_tool.finish_collection()
            
            #check a dictionary has been returned
            if not isinstance(answer, dict):
                raise Exception("PLUGIN MUST RETURN A DICTIONARY, RETURNED {0}".format(str(type(answer))))
            
            answer['status'] = 'ok'
            
            #save the usage stats
            if True:
                answer['max_cpu'] = max_cpu
                answer['max_mem'] = max_mem
                answer['containerID'] = socket.gethostname()
                answer['time_taken'] = round(time.time() - start_time, 2)
                
                if os.path.exists("/VERSION"):
                    with open("/VERSION", "r") as f:
                        version = scrub_newlines(f.read())    
                    answer["image_version"] = version
                    
                if os.path.exists("/IMAGE_NAME"):
                    with open("/IMAGE_NAME", "r") as f:
                        img_name = scrub_newlines(f.read())
                    answer['image_name'] = img_name
            
            response_pic = jsonpickle.encode(answer)
            #everything has gone fine, return the results in a nice response
            return Response(response=response_pic, status=200, mimetype="application/json")
        
        except Exception as exp:
            
            response = {'status':'failure', 'error':str(exp)}
            
            #if we're in debug mode then return a full traceback
            if self.app.config['debug']:
                response['full_traceback'] = str(traceback.format_exc())
                
            response_pic = jsonpickle.encode(response)
            
            #something has gone wrong return the bad result in this response
            return Response(response=response_pic, status=400, mimetype='application/json')
