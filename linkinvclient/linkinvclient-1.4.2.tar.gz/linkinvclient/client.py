import os
import requests
import json
# import jwt

# from tokenleaderclient.client.client import Client as tlClient
# from linkinvclient.configs.config_handler import Configs as LIConfig


class LIClient():
    '''
    we want to change all client_conf initialization from tlclient
    for that tlclient to provide client_conf
    First initialize an instance of tokenleader client and  pass it to LIClient 
    as its parameter
    '''
    service_name = 'linkInventory'
    
    def __init__(self, tlClient ):       
        
        self.tlClient = tlClient
        self.client_confs = tlClient.configs.general_config
        self.service_conf = self.client_confs.get(self.service_name)
        self.url_type = self.service_conf.get('url_type')
        self.ssl_enabled = self.service_conf.get('ssl_verify')
        self.ssl_verify = self.service_conf.get('ssl_verify')
#         self.url_to_connect = self.service_conf.get_url_to_connect()
        
#     def get_url_to_connect(self):
#         url_to_connect = None
#         catalogue = self.tlClient.get_token()['service_catalog']
#         #print(catalogue)
#         if catalogue.get(service_name):
#             #print(catalogue.get(service_name))
#             url_to_connect = catalogue[service_name][self.url_type]
#         else:
#             msg = ("{} is not found in the service catalogue, ask the administrator"
#                    " to register it in tokenleader".format(service_name))
#             print(msg)
#         return url_to_connect
    
    
    def invoke_call(self, method, service_endpoint,  headers, data=None,):
        try:
            if method == 'GET':  
                r = requests.get(service_endpoint, headers=headers, verify=self.ssl_verify)
            elif method == 'POST':
                r = requests.post(service_endpoint, data, headers=headers, verify=self.ssl_verify)
        except Exception as e:
            r_dict = {'error': 'could not conect to server , the error is {}'.format(e)}
            print(r_dict)
        try:
            r_dict = json.loads(r.content.decode())   
        except Exception as e:
            r_dict = {"looks like server has an error processing the"
                      "the request, the response recieved is {}".format(r.text)}
                      
                    
        return r_dict
              
    def get_service_ep_n_auth_header(self, api_route, service_name=service_name):
        ''' url to connect method was not caturing the exception when service enfpoint
        construction fails for non availability of tokenleader. Also there  call to 
        tokenleader used to be  twice. This code will correct the above issues but need to 
        be tested'''       
        url_to_connect = None
        try:
            all_data_token = self.tlClient.get_token()
            auth_token = all_data_token.get('auth_token')
            headers_v={'X-Auth-Token': auth_token}
            catalogue = all_data_token.get('service_catalog')            
            api_route = api_route            
        #print(catalogue)
            if catalogue.get(service_name):
                #print(catalogue.get(service_name))
                url_to_connect = catalogue[service_name][self.url_type]
                service_endpoint_v = url_to_connect + api_route
            else:
                msg = ("{} is not found in the service catalogue, ask the administrator"
                       " to register it in tokenleader".format(service_name))
                print(msg)
        except:
            print("could not retrieve service_catalog from token leader," 
                  " is token leaader service running ?"
                  " is tokenleader reachable from this server/container ??")
        return service_endpoint_v,  headers_v
    
    
    def handle_response(self, return_response):
        try:
            r_dict = json.loads(return_response.content.decode())
        except Exception as e:
            r_dict = {"Content returned by the server is not json serializable"
                    " checking the server log  might  help. "
                    " the text returned by the server is {}".format(
                        return_response.text)}
        return r_dict
        
        
    def post_request(self , api_route, data):        
        service_ep, headers = self.get_service_ep_n_auth_header(api_route)
        headers.update({'content-type':'application/json'})
        try:  
            r = requests.post(service_ep, 
                             headers=headers, 
                             data = json.dumps(data),                             
                            verify=self.ssl_verify)
            r_dict = self.handle_response(r)               
        except Exception as e:
            r_dict = {'error': 'could not connect to server , the error is {}'.format(e)}    #     
            print(r_dict)
#         print(r)  # for displaying from the cli  print in cli parser
        return r_dict
    
    
    def put_request(self , api_route, data):        
        service_ep, headers = self.get_service_ep_n_auth_header(api_route)
        headers.update({'content-type':'application/json'})
        try:  
            r = requests.put(service_ep, 
                             headers=headers, 
                             data = json.dumps(data),                             
                            verify=self.ssl_verify)
            r_dict = self.handle_response(r)                
        except Exception as e:
            r_dict = {'error': 'could not connect to server , the error is {}'.format(e)}    #     
            print(r_dict)
        return r_dict
    
    
    def delete_request(self, api_route ):
        service_ep, headers = self.get_service_ep_n_auth_header(api_route)
        try:  
            r = requests.delete(service_ep, headers=headers, verify=self.ssl_verify)            
        except Exception as e:
            r_dict = {'error': 'could not connect to server , the error is {}'.format(e)}
        r_dict = self.handle_response(r) 
        return r_dict
    
    
    def get_request(self, api_route):
        service_ep, headers = self.get_service_ep_n_auth_header(api_route)
        try:  
            r = requests.get(service_ep, headers=headers, verify=self.ssl_verify)            
        except Exception as e:
            r_dict = {'error': 'could not connect to server , the error is {}'.format(e)}
        r_dict = self.handle_response(r) 
        return r_dict
    
    
    def file_request_put(self, api_route, filepath):
            service_endpoint, headers = self.get_service_ep_n_auth_header(api_route)
            print(service_endpoint, headers)
            files = {'file': ( os.path.basename(filepath), 
                              open(filepath, 'rb'), 
                              'application/vnd.ms-excel', 
                              {'Expires': '0'})}
            try:              
                r = requests.put(service_endpoint, headers=headers, 
                                 files=files, verify=self.ssl_verify)
                r_dict = self.handle_response(r)               
            except Exception as e:
                r_dict = {'error': 'could not connect to server , the error is {}'.format(e)} 
            
            return r_dict
        
    def file_request_post(self, api_route, filepath):
            service_endpoint, headers = self.get_service_ep_n_auth_header(api_route)
            print(service_endpoint, headers)
            files = {'file': ( os.path.basename(filepath), 
                              open(filepath, 'rb'), 
                              'application/vnd.ms-excel', 
                              {'Expires': '0'})}
            try:              
                r = requests.post(service_endpoint, headers=headers, 
                                 files=files, verify=self.ssl_verify)
                r_dict = self.handle_response(r)               
            except Exception as e:
                r_dict = {'error': 'could not connect to server , the error is {}'.format(e)} 
            
            return r_dict
    
    def list_links(self):
        token = self.tlClient.get_token().get('auth_token')
        api_route = '/list/links'
        service_endpoint = self.url_to_connect + api_route
        headers={'X-Auth-Token': token}  
        return self.invoke_call( 'GET', service_endpoint, headers )
    
    def list_link_by_slno(self, slno):
        token = self.tlClient.get_token().get('auth_token')
        api_route = '/list/link/{}'.format(slno)
        service_endpoint = self.url_to_connect + api_route
        headers={'X-Auth-Token': token}  
        return self.invoke_call( 'GET', service_endpoint, headers )
    
    def list_link_by_circuit_id(self, circuit_id):
        api_route = '/list/links/{}'.format(circuit_id)
        r_dict = self.get_request(api_route)       
        return r_dict
        
    
    def add_rate(self, dictdata):
        r_dict = self.post_request('/add_rate', dictdata )
        return r_dict
    
    def add_payment(self, dictdata):
        r_dict = self.post_request('/add_payment', dictdata )
        return r_dict
    
    def add_altaddress(self, dictdata):
        r_dict = self.post_request('/add_altaddress', dictdata )
        return r_dict
    
    def add_lnetlink(self, dictdata):
        r_dict = self.post_request('/add_lnetlink', dictdata )
        return r_dict
    
    def list_obj(self, objname, field_name, field_value):        
        api_route = '/list_obj/{}/{}/{}'.format(
            objname, field_name, field_value)
        r_dict = self.get_request(api_route)       
        return r_dict
    
    def delete_obj(self, objname, objid):        
        api_route = '/delete_obj/{}/{}'.format(objname, objid)
        print(api_route)      
        r_dict = self.delete_request(api_route)
        return r_dict
