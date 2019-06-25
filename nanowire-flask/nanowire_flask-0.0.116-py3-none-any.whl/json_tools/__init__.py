#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 20 11:32:34 2019

@author: stuart
"""

#nanowire_flask json tools


import time
import pandas as pd
import requests

from io import BytesIO

import traceback

import jsonpickle
from flask import request, Response
from flask.views import View

from flask_api import FlaskAPI

#memory and cpu usage collection tools

import sys
import os

import socket

py_version = int(sys.version[0])

import json
import inspect


from nanowire_flask import scrub_newlines, usage_collection


###################################
### Functions for a json plugin ###
###################################


def run_json(r, app): 

    #if the user has sent a url then we want to extract that URL like this
    if r.headers['Content-Type'] != 'application/json':

        # convert string of image data to uint8
        text = json.loads(r.files['doc'].read().decode())

    #if the user has sent an image then lets extract that image and store it as
    #a PIL
    else:
        #extract the json info sent to the plugin
        variables_info = r.json
        
        #make sure content url is the right case
        #variables_info = map_contenturl2casecorrect(variables_info)

        if 'contentUrl' in variables_info.keys():
            
            response = requests.get(variables_info['contentUrl'])
                     
            text = json.loads(response.content.decode())
            
            if response.status_code == 404:
                
                raise Exception("FILE MISSING, CHECK URL OF LINK")
            
            variables_info.pop('contentUrl', None)
            
        else:
            text = variables_info

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
def check_json_function_is_valid(function):

    args = inspect.getargspec(function)[0]

    if args != ['inputJSON'] and args != ['self', 'inputJSON']:
        
        return False
        
    else:
        return True


class mount_json_function(object):
    
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
        
        if check_json_function_is_valid(self.app.config['function']):
            
            #define the class we're mounting onto post
            tool = jsonAPI
            
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

    
class jsonAPI(View):
    
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
            answer = run_json(request, self.app)
            
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