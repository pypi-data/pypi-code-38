#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 20 11:32:34 2019

@author: stuart
"""

#nanowire_flask csv tools



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

import inspect

from nanowire_flask import scrub_newlines, usage_collection


##################################
### Functions for a csv plugin ###
##################################


def process_input_var(txt):
    
    if ',' in txt:
        
        out = txt.split(',')
        
        #out[0] = out[0].replace('"', '')
        #out[-1] = out[-1].replace('"', '')
        
    else:
        out = txt
        
    return out

def run_csv(r, app): 
 

    #if the user has sent a url then we want to extract that URL like this
    if r.headers['Content-Type'] != 'application/json':

        variables_info = {}
        
        for val in r.values:

            variables_info[val] = process_input_var(r.values[val])
        
        # convert string of image data to uint8
        if 'csv' in r.files:
            df = pd.read_csv(r.files['csv'], dtype='unicode')
        elif 'xlsx' in r.files:
            df = pd.read_excel(r.files['xlsx'])
            
        

    #if the user has sent an image then lets extract that image and store it as
    #a PIL
    else:
        #extract the variables info sent to the plugin
        variables_info = r.json

        #extract the image from the sent url
        im_request = requests.get(variables_info['contentUrl'])
        
        bytes_obj = BytesIO(im_request.content)
        try:
            df = pd.read_csv(bytes_obj, dtype='unicode')
        except:
            df = pd.read_excel(variables_info['contentUrl'])
        
        variables_info.pop('contentUrl', None)

    #apply the function to the image
    
    if inspect.getargspec(app.config['function'])[0][-1] == 'variables':
        out_predictions = app.config['function'](df, variables_info)
    else:
        out_predictions = app.config['function'](df)
        
        
    if not isinstance(out_predictions, dict):
        raise Exception("FUNCTION MUST RETURN A DICTIONARY")

    
    #print("Took {0:0.2f} seconds".format(time.time()-start_time))
    
    return out_predictions

#function to check if the user defined function is as it should be
def check_csv_function_is_valid(function):

    args = inspect.getargspec(function)[0]

    if args != ['df', 'variables'] and args != ['self', 'df', 'variables'] and args != ['df'] and args != ['self', 'df']:
        
        return False
        
    else:
        return True


class mount_csv_function(object):
    
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
        
        if check_csv_function_is_valid(self.app.config['function']):
            
            #define the class we're mounting onto post
            tool = csvAPI
            
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

    
class csvAPI(View):
    
    methods = ['POST']
    
    def dispatch_request(self):
        
        try:
            
            #start usage stats collection
            if True:
                self.collection_tool.start_collection()
                start_time = time.time()
            
            #run the function
            answer = run_csv(request, self.app)
            
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
