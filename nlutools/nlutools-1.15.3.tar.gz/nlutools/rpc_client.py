import requests
import json

from utils import *
from config import *

http_headers = {"Content-type":"application/json"}

def doTask(serverName,data):
    try:
        data = json.dumps({'server_name':serverName,'traffic_paramsDict':data})
        taskUrl = mapConf[serverName+'_'+env]
        requests.adapters.DEFAULT_RETRIES=5
        session = requests.session()
        session.keep_alive = False
        ret = session.post(taskUrl,data,headers=http_headers,timeout=3)
        response_status = ret.status_code
        if response_status == 200:
            result = json.loads(ret.text)
            if result['status']==True:
                return result['result']
            return None
        else:
            printException('response error with status code:%s '%response_status)
            printException('please contact supporter %s for this exception'%(supportConf[serverName]))
            return None
    except Exception as e:
        printException('%s exception \nplease contact supporter %s for this exception : \n%s'%(serverName,supportConf[serverName],e))

entity_request_header = {"log_id":"0x111","user_ip":"","provider":"algo_survey","product_name":"algo_survey","uid":"0x111"}
def doCustomTask(serverName,data,m,c="tagging"):
    try:
        request_data = {"header":entity_request_header,"request":{"c":c,"m":m,"p":{"query_body":{"text_list":data}}}}   
        request_data = json.dumps(request_data)
        taskUrl=mapConf[serverName+'_'+env]
        requests.adapters.DEFAULT_RETRIES=5
        session = requests.session()
        session.keep_alive = False
        ret = session.post(taskUrl,request_data,headers=http_headers,timeout=3)
        response_status = ret.status_code
        if response_status == 200:
            result = json.loads(ret.text)['response']['results']
            if result:
                return result
            return None
        else:
            printException('response error with status code:%s '%response_status)
            printException('please contact supporter %s for this exception'%(supportConf[serverName]))
            return None
    except Exception as e:
        printException('%s exception \nplease contact supporter %s for this exception : \n%s'%(serverName,supportConf[serverName],e))
