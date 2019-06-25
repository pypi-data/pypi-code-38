#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 20 11:32:33 2019

@author: stuart
"""

#nanowire_flask image tools

import time
from PIL import Image

import requests

from io import BytesIO

import traceback

import jsonpickle
from flask import request, Response
from flask.views import View

from flask_api import FlaskAPI

import urllib

#memory and cpu usage collection tools

import sys
import os

import socket

py_version = int(sys.version[0])

import inspect

from nanowire_flask import scrub_newlines, usage_collection

def pullAndSave(url):

    filename = url.split("/")[-1]

    urllib.request.urlretrieve(url)

    return filename


def run_file(r, app): 

    #if the user has sent a url then we want to extract that URL like this
    if r.headers['Content-Type'] != 'application/json':
    
        variables_info = dict(r.args)
                
        # convert string of image data to uint8
        
        #filename = pullAndSave(r.files['file'])
        print("+++++")
        print(type(r.files['file']))
        print(dir(r.files['file']))
        print(r.files['file'].filename)
        print("+++++")
        
        filename = r.files['file'].filename
        r.files['file'].save(filename)

    #if the user has sent an image then lets extract that image and store it as
    #a PIL
    else:
        #extract the variables info sent to the plugin
        variables_info = r.json

        #extract the image from the sent url
        filename = pullAndSave(variables_info['contentUrl'])

        variables_info.pop('contentUrl', None)

    #apply the function to the image
    
    if inspect.getargspec(app.config['function'])[0][-1] == 'variables':
        out_predictions = app.config['function'](filename, variables_info)
    else:
        out_predictions = app.config['function'](filename)

    os.remove(filename)
        
        
    if not isinstance(out_predictions, dict):
        raise Exception("FUNCTION MUST RETURN A DICTIONARY")

    
    #print("Took {0:0.2f} seconds".format(time.time()-start_time))
    
    return out_predictions

#function to check if the user defined function is as it should be
def check_file_function_is_valid(function):

    args = inspect.getargspec(function)[0]

    if args != ['filename', 'variables'] and args != ['self', 'filename', 'variables'] and args != ['filename'] and args != ['self', 'filename']:
        
        return False
        
    else:
        return True


class mount_file_function(object):
    
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
        
        if check_file_function_is_valid(self.app.config['function']):
            
            #define the class we're mounting onto post
            tool = filesAPI
            
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

    
class filesAPI(View):
    
    methods = ['POST']
    
    def dispatch_request(self):
        
        try:
            #start usage stats collection
            if True:
                self.collection_tool.start_collection()
                start_time = time.time()
            
            #run the function
            answer = run_file(request, self.app)
            
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
