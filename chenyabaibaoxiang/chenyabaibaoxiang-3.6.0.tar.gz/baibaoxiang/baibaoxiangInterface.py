import requests
import re
import ast
from baibaoxiang import excel



class Interface_go:
    hang = 0
    lie = 0
    excel_input=excel.InputExcel()
    def leiji(self):
        # print(go.k, ",", go.l)
        Interface_go.lie += 1
        if Interface_go.lie >= 3:
            Interface_go.hang += 1
            Interface_go.lie = 0
    def __init__(self):
        print("开始接口连接过程。。。")



    def post(self,url, data, header,name):
        r = requests.post(url, data=data, headers=header)
        if "\"msg\":\"ok\"" in r.text and r.status_code == 200:
            print(name,"成功")
            try:
                print(r.json())
            except:
                print("无法输出json，转换成输出text")
                print(r.text)
        else:
            print(name,"未成功*****************************************************************************")
            print(r.json())
        try:
            on_to_over_time = r.elapsed.total_seconds()
            fanhui = re.findall("\{\"code\":.*?.*", str(r.json()))
            # print("这里是数组*************************",fanhui)
            if len(fanhui) == 0:
                fanhui = re.findall("\{\'code\':.*?.*", str(r.json()))
                if len(fanhui) == 0:
                    fanhui = str(r.json())
            jieguo = [name, url, str(data), r.status_code, fanhui,on_to_over_time]
            Interface_go.excel_input.input_excel(jieguo)
        except:
            print("无法输出json，转换成输出text")
            print(r.text)
            fanhui = re.findall("\{\"code\":.*?.*", r.text)
            # print("这里是数组*************************", fanhui)
            if len(fanhui) == 0:
                fanhui = re.findall("\{\'code\':.*?.*", r.text)
                if len(fanhui) == 0:
                    fanhui = r.text
            jieguo = [name, url, str(data), r.status_code, fanhui]
            Interface_go.excel_input.input_excel(jieguo)
        return r

    def get(self,url, data, header,name):
        r = requests.get(url, data=data, headers=header)
        if "\"msg\":\"ok\"" in r.text and r.status_code == 200:
            print(name,"成功")
            try:
                print(r.json())
            except:
                print("无法输出json，转换成输出text")
                print(r.text)
        else:
            print(name,"未成功*****************************************************************************")
            print(r.json())
        try:
            on_to_over_time = r.elapsed.total_seconds()
            fanhui = re.findall("\{\"code\":.*?.*", str(r.json()))
            # print("这里是数组*************************",fanhui)
            if len(fanhui) == 0:
                fanhui = re.findall("\{\'code\':.*?.*", str(r.json()))
                if len(fanhui) == 0:
                    fanhui = str(r.json())
            jieguo = [name, url, str(data), r.status_code, fanhui]
            Interface_go.excel_input.input_excel(jieguo)
        except:
            print("无法输出json，转换成输出text")
            print(r.text)
            fanhui = re.findall("\{\"code\":.*?.*", r.text)
            # print("这里是数组*************************", fanhui)
            if len(fanhui) == 0:
                fanhui = re.findall("\{\'code\':.*?.*", r.text)
                if len(fanhui) == 0:
                    fanhui = r.text
            jieguo = [name, url, str(data), r.status_code, fanhui,on_to_over_time]
            Interface_go.excel_input.input_excel(jieguo)
        return r



class Interface_Excel_go:
    def interface_excel_go(self,open_excel_file_address,input_excel_name,input_excel_address):
        i=Interface_go()
        goi=excel.OpenExcel()
        # t=go.open_excel('D:\linshi\涉及鲜橙收入和金额收入接口.xlsx')
        # t=go.open_excel('D:\linshi\工作簿1.xlsx')
        try:
            t=goi.open_excel(open_excel_file_address)
        except:
            print("文件地址必须是单引号")
        # print(t)
        for x in t:
            # print(x)
            name=x[0]
            if "http://" not in x[1] or 'http://' not in x[1]:
                address = "http://" + x[1] + x[2]
            else:
                address="http://"+x[1]+x[2]
            # print(x[3])
            try:
                data=ast.literal_eval(x[3])
            except:
                print("表格中的参数，必须加上双引号")
            # print(name+"\n"+address)
            # print(data)
            healer={}
            if x[5]=="post":
                i.post(address,data,healer,name)
            if x[5]=="get":
                i.get(address,data,healer,name)
        # excel.InputExcel().end("D:\\linshi\\","特殊")
        excel.InputExcel().end(input_excel_address,input_excel_name)


if __name__ == "__main__":
    go=Interface_go()
    go.post("url","data","header","name")
    excel.InputExcel().end("","")

    go2=Interface_Excel_go()
    go2.interface_excel_go("D:\linshi\涉及鲜橙收入和金额收入接口.xlsx","特殊","D:\\linshi\\")