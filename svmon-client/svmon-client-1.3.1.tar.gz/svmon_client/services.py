#!/usr/bin/python
# -*- coding: UTF-8 -*-

import subprocess
import os

_services={}

_services['b2safe']=['b2safe','irods']
_services['gitlab']=['gitlab']
_services['svmon']=['spring','angular']
_services['b2access']=['b2access_unity']
_services['b2find']=['b2find','ckan']
_services['b2handle']=['handle','epic']
_services['B2HANDLE']=['handle','epic']
_services['b2drop']=['nextcloud']
_services['dpmt']=['plone']
_services['eudat_website']=['drupal']
_services['b2gether']=['b2gether']
_services['gocdb']=['creg']
_services['b2access']=['unity']
_services['svmon_client']=['client']

_rpm_packages={}
_rpm_packages['b2safe']='b2safe'
_rpm_packages['irods']='irods-icat'

_tags={}
_tags['svmon']=['3.1','1.7']

def in_service_list(service_type):
    if service_type == None or service_type == "" or isinstance(service_type,str) == False:
        print("The service type argument should be a non-empty string")
        exit(1)
    if service_type in _services.keys():
        return True
    else:
        print("Your service type is unsupported. Please type --list-service-type see supported services.")
        exit(1)

def get_service_name(service_type):
    if service_type == None or service_type == "" or isinstance(service_type,str) == False:
        print("The service type argument should be a non-empty string")
        exit(1)
    if in_service_list(service_type):
        return _services.get(service_type)
    return []


def get_service_tag(service_type,configs=None):
    if service_type == None or service_type == "" or isinstance(service_type,str) == False:
        print("The service type argument should be a non-empty string")
        exit(1)
    if in_service_list(service_type) == False:
        print("The service type is currently unsupported in svmon client")
        exit(1)

    tags=[]
    if service_type == "svmon_client":
        tmp = subprocess.Popen('pip show svmon-client-pilot', shell=True, stdout = subprocess.PIPE)
        tmp = subprocess.Popen('grep Version', shell = True, stdin=tmp.stdout, stdout = subprocess.PIPE)
        tmp = tmp.communicate()
        tmp=tmp[0]
        if tmp == '' or tmp == None:
            print("No svmon client has been installed, please refer to https://gitlab.eudat.eu/jie.yuan/pysvmon")
            exit(1)
        ltmp=tmp.split('\n')
        ltmp=ltmp[0].split(':')
        if ltmp == None or len(ltmp) < 2:
            print("SVMON client can not be resolved, please check for installation")
            exit(1)
        ltmp=ltmp[1]
        ltmp.replace("\n","")
        ltmp.replace(" ", "")

        if ltmp == "":
            print("the version of svmon client can not resolved. Please check installation of svmon client")
            exit(1)
        tags.append(ltmp)
        return tags
    elif service_type == "gitlab":
        #tags.append("ce15") #currently for test
        tmp = get_by_rpm_packages("gitlab", 0 , 1)
        if tmp == "":
            print("no gitlab version can be resolved")
            exit(1)
        tags.append(tmp)
        return tags
    elif service_type == "b2safe":
        tmp=get_by_rpm_packages("b2safe")
        if tmp == "":
            print("no b2safe version can be resolved")
            exit(1)
        tags.append(tmp)
        tmp=get_by_rpm_packages("irods-icat")
        if tmp == "":
            print("no icat version can be resolved")
            exit(1)
        tags.append(tmp)
        return tags
    elif service_type == "svmon":
        return _tags['svmon']
    elif service_type == "b2handle" or service_type == "B2HANDLE":
        if configs.has_key('epic_version_file') or configs.has_key('handle_server_path'):
            tags=[]
            if configs.has_key('epic_version_file') and configs.get('epic_version_file') != '' and configs.get('epic_version_file') != None: 
                tags.append(get_epic_version(configs.get('epic_version_file')))
            if configs.has_key('handle_server_path') and configs.get('handle_server_path') != '' and configs.get('handle_server_path') != None: 
                tags.append(get_handle_server(configs.get('handle_server_path')))
            return tags
        else:
            print("No b2handle configuration to get versions")
            exit(1)







# for package version that can be accessed via rpm management
def get_by_rpm_packages(software,start=0,end=0):
    if isinstance(software,str)  == False or software == "" or software == None:
        print("software name should be a non-empty string")
        exit(1)
    if isinstance(start,int) == False or isinstance(end, int) == False:
        print("The input of indices should be integers to fetch correct version,")
        exit(1)
    tmp = subprocess.Popen("rpm -qa", shell=True, stdout=subprocess.PIPE)
    tmp = subprocess.Popen('grep ' + software, shell=True, stdin=tmp.stdout, stdout=subprocess.PIPE)
    tmp = tmp.communicate()
    tmp = tmp[0]
    if  tmp == None or tmp == "":
        print("no rpm packages can be found for " + software)
        exit(1)
    ind=tmp.find(software)
    ind=ind+len(software)
    ltmp=tmp[ind+1:len(tmp)].split('-')

    if len(ltmp) > end:
        if start == end:
            return ltmp[start]
        elif start < end:
            res=""
            for i in range(start,end+1):
                res=res+ltmp[i]
            return res
        else:
            print("The start index should be smaller than end index for a correct rpm package resolver")
    else:
        print(software +" version not resolved")
        exit(1)


def get_user():
    tmp=subprocess.Popen("whoami",shell=True,stdout=subprocess.PIPE)
    tmp=tmp.communicate()
    return tmp[0].replace('\n','')


def get():
    tags=get_service_tag("svmon_client")
    return tags[0]

def get_epic_version(epic_version_file):
    exist =  os.path.exists(epic_version_file)
    if exist:
        f=open(epic_version_file,'r')
        while True:
            line=f.readline()
            if not line:
                f.close()
                print("The epic version can not be resolved from "+ epic_version_file)
                exit(1)
                break
            if line.find("VERSION=") != -1 :
                f.close()
                if line.find("\'") != -1:
                    line=line.replace("\'","")
                for i in range(len(line)):
                    if line[i].isupper() == True:
                        line=line.replace(line[i],"=")
                if line.find("=") != -1:
                    line=line.replace("=","")
                return line
                break

        print("No epic version information in " + epic_version_file)
        exit(1)

          

def get_handle_server(handle_server_path):
    tmp = subprocess.Popen(handle_server_path, shell=True, stdout = subprocess.PIPE)
    tmp = tmp.communicate()
    if tmp == None and len(tmp) < 2:
        print("Handle server executable is incorrect")
        exit(1)
    tmp = tmp[0].split('\n')
    if tmp == None and len(tmp) < 1:
        print("Handle server executable is incorrect")
        exit(1)
    tmp = tmp[0]
    tmp = tmp.split('version')
   

    return tmp[1].lstrip()


#get svmon client version
def get_version():
    tmp = subprocess.Popen('pip show svmon-client-pilot', shell=True, stdout=subprocess.PIPE)
    tmp = subprocess.Popen('grep Version', shell=True, stdin=tmp.stdout, stdout=subprocess.PIPE)
    tmp = tmp.communicate()
    tmp = tmp[0]
    if tmp == '' or tmp == None:
        print("No svmon client has been installed, please refer to https://gitlab.eudat.eu/jie.yuan/pysvmon")
        exit(1)
    ltmp = tmp.split('\n')
    ltmp = ltmp[0].split(':')
    if ltmp == None or len(ltmp) < 2:
        print("SVMON client can not be resolved, please check for installation")
        exit(1)
    ltmp = ltmp[1]
    ltmp.replace("\n", "")
    return ltmp


if __name__ == "__main__":
    print(get())
    
