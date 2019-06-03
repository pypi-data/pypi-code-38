"""
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
Filename: DNAv3_IntParser.py
Version: Python 3.7.0
Authors: Kris Swanson (kriswans@cisco.com)
Description:    This program reads and manipulates the json interface configs for the DNAv3 parsing json excercise.
"""

class IntParser:
    def __init__(self,file_name):
        '''Reads and parses interfaces json file.
        Establishes version and whether multiple interfaces exist. '''
        from json import load as load
        self.file=open(file_name,'r')
        self.json=load(self.file)
        self.file.close()
        if 'ietf-interfaces:interfaces' in self.json:
            self.multiple = True
        else:
            self.multiple = False
        self.version = 1
        self.master_list=[self.json]
    def print(self):
        '''nicely prints json file content'''
        from json import dumps
        print(dumps(self.json, indent=2))
    def interfaces(self):
        '''returns json interfaces'''
        try:
            self.interfaces=self.json['ietf-interfaces:interface']
        except:
            self.interfaces=self.json['ietf-interfaces:interfaces']['interface']
        return self.interfaces
    def ip_addresses(self):
        '''returns a list of tuples containing:
         interface, ip address, netmask, and mask length'''
        from ipaddress import IPv4Address as addr
        ip_int_list=[]
        try:
            self.intf=self.json["ietf-interfaces:interface"]["name"]
            self.ip_address=self.json["ietf-interfaces:interface"]["ietf-ip:ipv4"]["address"][0]["ip"]
            self.netmask=self.json["ietf-interfaces:interface"]["ietf-ip:ipv4"]["address"][0]["netmask"]
            self.maskbits=addr._make_netmask(self.netmask)[1]
            ip_int_list.append((self.intf,self.ip_address,self.netmask,self.maskbits))
        except:
            for i in self.json['ietf-interfaces:interfaces']["interface"]:
                self.intf=i['name']
                self.ip_address=i['ietf-ip:ipv4']['address'][0]['ip']
                self.netmask=i["ietf-ip:ipv4"]["address"][0]["netmask"]
                self.maskbits=addr._make_netmask(self.netmask)[1]
                ip_int_list.append((self.intf,self.ip_address,self.netmask,self.maskbits))
        return ip_int_list

    def update(self,name,ip,netmask,enabled='true',type='iana-if-type:ethernetCsmacd',):
        '''Updates json structure with arguments interface-name ip and netmask
        returns current json structure.Note: Only supports GigabitEthernet
        and Loopback today.'''

        int_number=max([i for i in list(range(65535)) if str(i) in name])
        if 'gi' in name or 'Gi' in name or 'GI' in name:
            int_type='GigabitEthernet'
            type="iana-if-type:ethernetCsmacd"
            name=int_type+str(int_number)
        else:
            int_type='Loopback'
            type='iana-if-type:softwareLoopback'
        int_name=int_type+str(int_number)


        update_dict={"name": int_name,
        "type": type,
        "enabled": 'true',
        "ietf-ip:ipv4": {
        "address": [
        {"ip": ip,
        "netmask": netmask}]}}

        if self.multiple == True:
            self.json['ietf-interfaces:interfaces']["interface"].append(update_dict)
        else:
            self.json={"ietf-interfaces:interfaces": {"interface":[self.json["ietf-interfaces:interface"]]}}
            self.json["ietf-interfaces:interfaces"]["interface"].append(update_dict)
            self.multiple = True
        self.version+=1
        if int_name in [i['name'] for i in self.json["ietf-interfaces:interfaces"]["interface"]][:-1]:
            dup_index=[i['name'] for i in self.json["ietf-interfaces:interfaces"]["interface"]].index(int_name)
            print(dup_index)
            self.json["ietf-interfaces:interfaces"]["interface"].remove(self.json["ietf-interfaces:interfaces"]["interface"][dup_index])
        self.master_list.append(self.json)
        return self.json

    def rollback(self,version):
        '''Rollback to specified version number'''
        self.json=self.master_list[version-1]
        self.version=version
        if 'ietf-interfaces:interfaces' in self.json:
            self.multiple = True
        else:
            self.multiple = False
        return self.json
