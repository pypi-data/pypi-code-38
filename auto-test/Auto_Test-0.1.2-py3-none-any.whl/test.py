import requests
import csv
from FormCommon import *
import time
from Zhuru import *

"""
list2Dict读取csv文件，将文件内的数据转化成测试用例，形式：[{"key":"value"},{"key":"value"},……]
soloRequest获取请求参数，执行请求，用于获取token的请求方式
staticsoloRequest用于需要token时的请求方式
"""
class Csv2Dict(object):
    def __init__(self,path="",debug=False,student_phone="",student_name="",student_extraPhone=""):
        self.path = path
        self.debug = debug
        self.student_phone = student_phone
        self.student_name = student_name
        self.student_extraPhone = student_extraPhone

    def list2Dict(self):
        try:
            with open(self.path,'r',encoding="gbk") as f:
                rander = csv.DictReader(f)
                casedata = []
                for line in rander:
                    casedata.append(dict(line))
                print(casedata)
                return casedata
        except Exception as es:
            print(es)

    def soloRequest(self,data,temp_files=""):
        host = data["url"]
        path = data["path"]
        url = host + path
        method = data["method"]
        files = data["files"]

        if data["body"] != "null" and data["body"]:
            payload = eval(data["body"])
        else:
            payload = {}
        if "headers" in data.keys():
            if data["headers"] and data["headers"] != "null":
                headers = eval(data["headers"])
            else:
                headers = {}
        else:
            headers = {}
        if "params" in data.keys():
            if data["params"] and data["params"] != "null":
                params = eval(data["params"])
            else:
                params = {}
        else:
            params = {}

        if "files" in data.keys():
            if data["files"] and data["files"] !="null":
                files = temp_files
        else:
            files = {}
        with requests.request(method=method,url=url,data=payload,headers =headers,params=params,files=files) as response :
            return response

    @staticmethod
    def staticsoloRequest(data,token,csv2dict="",temp_files=""):
        host = data["url"]
        path = data["path"]
        url = host + path
        method = data["method"]
        files = data["files"]

        # student_phone = csv2dict.student_phone
        # student_name = csv2dict.student_name
        # student_extraPhone = csv2dict.student_extraPhone
        # request = csv2dict

        if data["body"] != "null" and data["body"]:
            payload = eval(data["body"])
        else:
            payload = {}
        if "headers" in data.keys():
            if data["headers"] and data["headers"] != "null":
                headers = token[data["headers"]]
            else:
                headers = {}
        else:
            headers = {}
        if "params" in data.keys():
            if data["params"] and data["params"] != "null":
                params = eval(data["params"])
            else:
                params = {}
        else:
            params = {}
        if "files" in data.keys():
            if data["files"] and data["files"] !="null":
                files = temp_files
        else:
            files = {}
        print(method,url,payload,headers,params)
        with requests.request(method=method,url=url,data=payload,headers =headers,params=params,files=files) as response :
            return response

"""
getToken:不同平台获取token方式
{fwzx:客服，ifwzx2：销售，ifwzx3：教务，ifwzx4：财务，ifwzx5：运营，ifwzx6：班主任，ifwzx7：管理员}
{ixb1:销售工作台,ixb2:班主任工作台}
initToken：初始化先获取token
run:处理用例，并执行，验证
"""
class Test(Csv2Dict):
    def getToken(self,response):
        try:
            if "Player=fwzx" in response.request.url:
                headers = {"Authorization":'Bearer ' + response.json()["data"]["access_token"]}
                Player = ['fwzx2','fwzx3','fwzx4','fwzx5','fwzx6','fwzx7']
                for x in Player :
                    if x in response.request.url:
                        return "i"+x,headers
                return "ifwzx", headers
            elif "Player=ixb" in response.request.url:
                token = response.json()['data']['access_token']
                b_token = response.json()['data']['b_token']
                headers = {}
                headers_simple={}
                headers["Authorization"]="Bearer " + token
                headers["auth-x"] = b_token
                headers_simple["Authorization"] = "Bearer " + token
                if "Player=ixb1" in response.request.url:
                    return "ixs",headers,"ixs1",headers_simple
                elif "Player=ixb2" in response.request.url:
                    return "izj",headers,"izj1",headers_simple
            return False
        except:
            print ("get token error")
            return  False

    def initToken(self,datas):
        token = {}
        for data in datas:
            if "Player=" in data["path"]:
                response = self.soloRequest(data)
                token_temp = self.getToken(response)
                if token_temp:
                    for index in range(0, len(token_temp), 2):
                        token[token_temp[index]] = token_temp[index+1]
        return token

    def run(self,file):
        dd = Test(file)
        datas = dd.list2Dict()
        token = dd.initToken(datas)
        print(token)
        cases = {}
        case_name = ""
        for data in datas:
            if data["name"] == 'START':
                case_name = data["url"]
                cases[case_name] = []
            else:
                cases[case_name].append(data)
        for case_name, case in cases.items():
            for data in case:
                    if "Player=" not in data["path"]:
                        if data["files"]:
                            files = {"file": ("Chrysanthemum.jpg", open("Chrysanthemum.jpg", "rb"), "image/jpeg", {})}
                            response = self.staticsoloRequest(data, token, temp_files=files)
                        else:
                            response = self.staticsoloRequest(data, token)
                        if data["Zhuru"]:
                            exec(data["Zhuru"])
                        result = jsonAssert(response.text)
                        print(data["name"], "checkpoint", data["checkpoint"], response.json())
                        if data["checkpoint"] in response.text:
                            if data["assert"].lower() != str(result).lower():
                                print(case_name, "失败了！！！")
                                break
                        else:
                            print("验证错误")
            print(case_name, "run 完了！！！！")

if __name__ == '__main__':
    Test().run("login.csv")
