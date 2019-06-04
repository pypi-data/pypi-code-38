import requests
import csv
import BlueTest
from FormCommon import *
import os
from Zhuru import *

"""
list2Dict读取csv文件，将文件内的数据转化成测试用例，形式：[{"key":"value"},{"key":"value"},……]
soloRequest获取请求参数，执行请求，用于获取token的请求方式
staticsoloRequest用于需要token时的请求方式
"""

class Csv2Dict(object):
    def __init__(self,path=""):
        self.path = path

    def list2Dict(self):
        try:
            with open(self.path,'r',encoding="gbk") as f:
                rander = csv.DictReader(f)
                casedata = []
                for line in rander:
                    casedata.append(dict(line))
                casedata = str(casedata)

                student_name = Zhuru().student_name()
                student_phone = Zhuru().student_phone()
                student_extraPhone = Zhuru().student_extraPhone()
                casedata = casedata.replace("student_name", "\'"+student_name+"\'")
                casedata = casedata.replace("student_phone", "'"+student_phone+"'")
                casedata = casedata.replace("student_extraPhone", "\'"+student_extraPhone+"\'")


                casedata = eval(casedata)
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
        data["body"]=data["body"].replace("Zhuru.student_name","Zhuru().student_name()")
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
    def staticsoloRequest(data,token,temp_files=""):
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
"""
class Token(Csv2Dict):
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


class Resualt():
    def __init__(self):
        self.result = 2
        self.case_name="2222"
    def id(self):
        return ""+test_name
    def shortDescription(self):
        return self.case_name

"""
solorun执行case方法，将case执行结果写入Resualt的方法
run:执行case，将case执行结果写入Resualt
mainRun:主执行体，获取所需datas和token，处理用例。报告的结果 = 用例的执行结果，报告整理，生成报告
"""
class Test():
    def __init__(self,cases,token):
        self.results = []
        self.cases = cases
        self.token = token
    def solorun(self,case,case_name):
        dd = Resualt()
        dd.__class__.__name__=test_name+"流程校验"
        dd.case_name = case_name
        print_data = ""
        for data in case:
            # try:
                if "Player=" not in data["path"]:
                    files = {"file": ("Chrysanthemum.jpg", open(r"./Chrysanthemum.jpg", "rb"), "image/jpeg", {})}
                    response = Csv2Dict.staticsoloRequest(data, self.token,temp_files=files)
                    if data["Zhuru"]:
                        exec(data["Zhuru"])
                    result = jsonAssert(response.text)
                    print_data += "%s:结果%s\n"%(data["name"], jsonAssert(response.text))
                    print("checkpoint", data["checkpoint"], response.text)

                    if data["checkpoint"] in response.text:
                        if data["assert"].lower() != str(result).lower():
                            print(case_name, "失败了！！！")
                            return (1, dd, print_data, "")
                    else:
                        print(case_name,"验证错误")
                        return (1, dd, "数据格式未包含校验点:"+str(data["checkpoint"]), "")
            # except Exception as e:
            #     print(e)
        print(case_name,"成功！")
        return (0, dd, print_data, "")

    def run(self):
        for case_name, case in self.cases.items():
            result = self.solorun(case,case_name)
            self.results.append(result)

    def Result(self):
        self.run()
        return self.results

    def mainRun(file_name):
        dd = Token(test_name +".csv")
        datas = dd.list2Dict()
        token = dd.initToken(datas)
        # datas = Csv2Dict(test_name +".csv").list2Dict()
        # token = Token(test_name +".csv").initToken(datas)

        cases = {}
        case_name = ""
        for data in datas:
            if data["name"] == 'START':
                case_name = data["url"]
                cases[case_name] = []
            else:
                cases[case_name].append(data)
        print(token)

        runner = BlueTest.HTMLTestRunner(
            stream=file_name,
            title='服务中心测试报告',
            description='',
            tester='tester'
            )

        start_time = time.strftime('%Y-%m-%d %H:%M:%S')
        time_time = time.time()

        #运行测试用例  #用例数量调节器
        a = Test(cases,token) #用例执行体
        d = BlueTest.Report() #报告生成的类
        d.tester="董"
        d.start_time = str(start_time)
        d.result = a.Result() # 报告的结果 =用例的执行结果
        d.use_time = str ('%.2f 秒' % (time.time() - time_time))
        d.Arrangement() #数据整理
        runner.run(d) #生成报告

if __name__ == '__main__':
    case_file = findCase(".\cases")
    for key, value in case_file.items():
        test_name =value #'.\\cases\\login2'
        case =  key #login2
        file_name = "templates//daily_report//"+ case +str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'TestReport' + '.html')
        Test.mainRun(file_name)
