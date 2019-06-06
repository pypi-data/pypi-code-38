import requests
import csv
import BlueTest
from FormCommon import *
import os
from Zhuru import *
import business

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
mkdir("./cases/")
mkdir("./templates/daily_report")
mkdir("./picture/")

response = requests.get("https://www.baidu.com/img/bd_logo1.png")
with open('./picture/baidu.jpg', 'wb') as f:
    f.write(response.content)

"""
list2Dict读取csv文件，将文件内的数据转化成测试用例，形式：[{"key":"value"},{"key":"value"},……]
soloRequest获取请求参数，执行请求，用于获取token的请求方式
staticsoloRequest用于需要token时的请求方式
"""

class Csv2CaseList(object):
    def __init__(self,path=""):
        self.path = path

    def caseList(self):
        try:
            with open(self.path,'r',encoding="gbk") as f:
                casedata = business.dataRefresh(csv.DictReader(f))
                print(casedata)
                return casedata
        except Exception as es:
            print(es)

class RequestCase():

    def elementsRefresh(self,data,token,temp_files):
        if "body" in data.keys():
            if data["body"] != "null" and data["body"]:
                payload = eval(data["body"])
            else:
                payload = {}
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
                files={}
        else:
            files = {}
        return payload,headers,params,files

    def soloRequest(self,data,token,temp_files=""):
        host = data["url"]
        path = data["path"]
        url = host + path
        method = data["method"]

        payload, headers, params, files = self.elementsRefresh(data,token,temp_files)
        print(method, url, payload, headers, params)
        with requests.request(method=method,url=url,data=payload,headers =headers,params=params,files=files) as response :
            return response


"""
getToken:不同平台获取token方式
{fwzx:客服，ifwzx2：销售，ifwzx3：教务，ifwzx4：财务，ifwzx5：运营，ifwzx6：班主任，ifwzx7：管理员}
{ixb1:销售工作台,ixb2:班主任工作台}
initToken：初始化先获取token
"""

class Token(Csv2CaseList):
    def initToken(self,datas):
        token = {}
        for data in datas:
            if business.checkPlayer(data) is True:
                response = RequestCase().soloRequest(data,token)
                token_temp = business.getToken(response)
                if token_temp:
                    for index in range(0, len(token_temp), 2):
                        token[token_temp[index]] = token_temp[index+1]
        return token


class Resualt():
    def __init__(self):
        self.result = 2
        self.case_name="2222"
    def id(self):
        return ""+case_file_name
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
        self.result_up = {}
    def solorun(self,case,case_name):
        dd = Resualt()
        dd.__class__.__name__=case_file_name+"流程校验"
        dd.case_name = case_name
        print_data = ""
        for data in case:
            single_response_time = ""
            try:
                if business.checkPlayer(data) is False:
                    files = {"file": ("baidu.jpg", open(r"./picture/baidu.jpg", "rb"), "image/jpeg", {})}
                    response = RequestCase().soloRequest(data, self.token,temp_files=files)
                    single_response_time = str(response.elapsed.microseconds / 1000)
                    print("单次请求时间" + single_response_time)

                    business.evalBusiness(data,response=response)

                    # if data["Zhuru"]:
                    #     exec(data["Zhuru"])
                    print_data += business.assertBusiness(data,response)
                    # print_data += "%s:结果%s\n"%(data["name"], jsonAssert(response.text))
                    print("checkpoint", data["checkpoint"], response.text)

                    if data["checkpoint"] in response.text:
                        result = jsonAssert(response.text)
                        if data["assert"].lower() != str(result).lower():
                            print(case_name, "失败了！！！")
                            # self.result_up[]
                            return (1, dd, print_data, "")
                    else:
                        print(case_name,"验证错误")
                        return (1, dd, "数据格式未包含校验点:"+str(data["checkpoint"]), "")
                # else:
                #     return False
            except Exception as e:
                print(e)
        print(case_name,"成功！")
        if dd.case_name not in self.result_up.keys():
            self.result_up[dd.case_name]={0,print_data,single_response_time}
        return (0, dd, print_data, "")

    def run(self):
        for case_name, case in self.cases.items():
            result = self.solorun(case,case_name)
            if  result:
                self.results.append(result)

    def Result(self):
        self.run()
        return self.results

    def mainRun(file_name):
        datas = Csv2CaseList(test_name + ".csv").caseList()
        token = Token(test_name + ".csv").initToken(datas)
        cases=business.getCases(datas)
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
        case_file_name =  key #login2
        file_name = "templates//daily_report//"+ case_file_name +str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'TestReport' + '.html')
        Test.mainRun(file_name)
