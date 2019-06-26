#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json
import subprocess
from . import services
from . import json_operations

class SVMONReport:

    def __init__(self):
        self.site=""
        self.host=""
        self.service_names=[]
        self.service_type=""
        self.operating_system=""  
        self.tags=[]
        cwd = os.path.dirname(services.__file__)
        filename = cwd + "/config.json"
        with open(filename, 'r') as f:
            load_dict= json.load(f)
            self.site=str(load_dict['site'])
            self.host=str(load_dict['host'])
            self.service_type=str(load_dict['service_type'])
            

    def refresh_service_name_and_tag(self):
        if services.in_service_list(self.service_type) == False:
            print("service type not configured")
        self.service_names = services.get_service_name(self.service_type)
       
        b2handle_config= {}
        if self.service_type == 'b2handle' or self.service_type == "B2HANDLE":
            cwd = os.path.dirname(services.__file__)
            filename = cwd + "/config.json"
            with open(filename, 'r') as f:
                load_dict= json.load(f)
                if load_dict.has_key('epic_version_file') or load_dict.has_key('handle_server_path'):
                    if load_dict.has_key('epic_version_file') and load_dict.get('epic_version_file') != None and load_dict.get('epic_version_file') != '':
                        b2handle_config['epic_version_file'] = load_dict.get('epic_version_file')
                    if load_dict.has_key('handle_server_path') and load_dict.get('handle_server_path') != None and load_dict.get('handle_server_path') != '':
                        b2handle_config['handle_server_path'] = load_dict.get('handle_server_path')
                    self.tags = services.get_service_tag(self.service_type,b2handle_config)
                else:
                    print("No configuration for b2handle, please see svmon help")
                    exit(1)
        else:
            self.tags = services.get_service_tag(self.service_type)

    
    def get_site(self):
        return self.site

    def get_host(self):
        return self.host

    def get_service_names(self):
        return self.service_names

    def get_service_type(self):
        return self.service_type

    def get_tags(self):
        return self.tags
    
    def set_site(self,site):
        if isinstance(site,str):
            self.site=site

    def set_host(self,host):
        if isinstance(host,str):
            self.host=host

    def set_service_names(self,service_names):
        if isinstance(service_names,list):
            self.service_names=service_names

    def set_service_type(self,service_type):
        if isinstance(service_type,str):
            self.service_type=service_type

    def set_tags(self,tags):
        if isinstance(tags,list):
            self.tags=tags
   
    def set_operating_system(self,operating_system):
        if isinstance(operating_system,str):
            self.operating_system=operating_system

    def set_service_names_and_tags(self,service_name,tag):
        this.service_names.append(service_name)
        this.tags.append(tag)
       

    def print_report(self):
        if len(self.service_names) > 0:
            res=[]
            if self.service_names== None or len(self.service_names ) < 1:
                print("no service names is resolved at your host")
                exit(1)
            if  self.tags == None or len(self.tags) < 1:
                print("no service component version is resolved at your host")
                exit(1)
            j=0
            for i in range(len(self.service_names)):
                if j < len(self.tags) and self.tags[j] != None and self.tags[j] != "" :
                    res.append(self.site+'\t'+self.host+'\t'+self.operating_system+'\t'+self.service_type+'\t'+self.service_names[i]+'\t'+self.tags[j]+'\n')
                    j = j +1
                    #print(self.service_names[i])
            return res
        else:
            print("Zero service components")
            return []



    def jsonify(self):
        if len(self.service_names) > 0:
            res = {}
            res['site']= self.site
            res['host'] = self.host
            res['operating_system'] = self.operating_system
            res['service_type'] = self.service_type
            res['service_names'] = self.service_names
            res['tags'] = self.tags
            return res
        else:
            print("No services to be jsonified")
            return {}
    
    def save_b2handle_config_to_json(self,handle_server_path=None,epic_version_file=None):
        if handle_server_path == None and epic_version_file == None:
            print("No b2handle configuration input")
            exit(-1)
        if handle_server_path != None and isinstance(handle_server_path,str) == False:
            print("Handle server path should be a string")
            exit(-1)
        if epic_version_file != None and isinstance(epic_version_file,str) == False:
            print("Handle server path should be a string")
            exit(-1)
        if epic_version_file == "" and handle_server_path == "":
            print("No input for b2handle configuration")
            exit(-1)

        res={}
        res['site']= self.site
        res['host'] = self.host
        res['service_type'] = self.service_type
        if epic_version_file != "" and handle_server_path != "":
            res['epic_version_file'] = epic_version_file
            res['handle_server_path'] = handle_server_path
        elif epic_version_file == "" and handle_server_path != "":
            res['handle_server_path'] = handle_server_path
            print("No epic_version_file input")
            cwd = os.path.dirname(services.__file__)
            filename = cwd + "/config.json"
            with open(filename, 'r') as f:
                load_dict= json.load(f)
                if load_dict.has_key('epic_version_file'):
                    res['epic_version_file'] = load_dict.get('epic_version_file')
        elif epic_version_file != "" and handle_server_path == "":
            res['epic_version_file'] = epic_version_file
            print("No handle_server_path input")
            cwd = os.path.dirname(services.__file__)
            filename = cwd + "/config.json"
            with open(filename, 'r') as f:
                load_dict= json.load(f)
                if load_dict.has_key('handle_server_path'):
                    res['handle_server_path'] = load_dict.get('handle_server_path')

        cwd = os.path.dirname(services.__file__)
        filename = cwd + "/config.json"
        if services.get_user() != 'root' and cwd.find('usr') != -1 and cwd.find('lib') != -1:
            print('You need root priviledges to write the configuration file')
            exit(1)
        success = json_operations.save_to_file(filename,res)
        if success == False:
            print("Save json data failed")
            exit(1)
        else:
            print("Saved B2HANLE configuration")



    def save_to_json(self):
        if self.site != "" and self.site != None:
            res = {}
            res['site']= self.site
            res['host'] = self.host
            res['service_type'] = self.service_type
            if self.service_type == "b2hanle" or self.service_type == "B2HANDLE":
                cwd = os.path.dirname(services.__file__)
                filename = cwd + "/config.json"
                with open(filename, 'r') as f:
                    load_dict= json.load(f)
                    if load_dict.has_key('epic_version_file') and load_dict.get('epic_version_file') != None and load_dict.get('epic_version_file') != "":
                        res['epic_version_file'] = load_dict.get('epic_version_file')
                    if load_dict.has_key('handle_server_path') and load_dict.get('handle_server_path') != None and load_dict.get('handle_server_path') != "":
                        res['handle_server_path'] = load_dict.get('handle_server_path')

            cwd = os.path.dirname(services.__file__)
            filename = cwd + "/config.json"
            if services.get_user() != 'root' and cwd.find('usr') != -1 and cwd.find('lib') != -1:
                print('You need root priviledges to write the configuration file')
                exit(1)

            success = json_operations.save_to_file(filename,res)
            if success == False:
                print("Save json data failed")
                exit(1)
        else:
            print("No services to be jsonified")
            exit(1)
    
        
    
 

    def set_pair(self,key,value):
        if isinstance(key,str) == False:
            print("Key should be a string")
            exit(1)

        if key == "site":
            self.set_site(value)
        elif key == "host":
            self.set_host(value)
        elif key == "service_type":
            self.set_service_type(value)
        elif key == "operating_system":
            self.set_operating_system(value)
        elif key == "service_names":
            self.set_service_names(value)
        elif key == "tags":
            self.set_tags(value)
        else :
            print("such key is not supporteed: %s\n" %key)
            exit(1)


    def check_site(self):
        return True


    def check_host(self):
        return True

    def print_config_file(self):
        cwd = os.path.dirname(services.__file__)
        filename = cwd + "/config.json"
        with open(filename, 'r') as f:
            load_dict = json.load(f)
            print("The following are your current configurations: ")
            for k, v in load_dict.items():
                print(str(k) +'=  ' +str(v))
            print('Please use svmon --site <SITE> --host <HOST> --type <TYPE> --dump to change your configuration')
            print('More details, please see svmon --help')



    def send_report_to_svmon_server(self):
       import requests as re
       url = 'https://svmon.eudat.eu:8443/api/serviceComponent/jsonreport'
       headers = {}
       headers['Content-Type'] = 'application/json'
       cwd = os.path.dirname(services.__file__)
       certs = cwd + "/chain_TERENA_SSL_CA_3.pem"
       for i in range(len(self.service_names)):
           res = {}
           res['siteName']=self.site
           res['hostNameId']=self.host
           res['operatingSystem']=self.operating_system
           res['serviceType']=self.service_type
           res['serviceComponentName']=self.service_names[i]
           res['tagAtSite']=self.tags[i]
           r = re.post(url, headers=headers, data=json.dumps(res), verify=certs)
           if (r.status_code != 201):
               print('Sending report failed, please check your configuration')
               exit(1)
       print('Report has been sent successfully.')
       exit(0)



if __name__=="__main__":
    re=SVMONReport()
    re.save_to_json()
