from Zhuru import *

def getToken(response):
    try:
        if "Player=fwzx" in response.request.url:
            headers = {"Authorization": 'Bearer ' + response.json()["data"]["access_token"]}
            Player = ['fwzx2', 'fwzx3', 'fwzx4', 'fwzx5', 'fwzx6', 'fwzx7']
            for x in Player:
                if x in response.request.url:
                    return "i" + x, headers
            return "ifwzx", headers
        elif "Player=ixb" in response.request.url:
            token = response.json()['data']['access_token']
            b_token = response.json()['data']['b_token']
            headers = {}
            headers_simple = {}
            headers["Authorization"] = "Bearer " + token
            headers["auth-x"] = b_token
            headers_simple["Authorization"] = "Bearer " + token
            if "Player=ixb1" in response.request.url:
                return "ixs", headers, "ixs1", headers_simple
            elif "Player=ixb2" in response.request.url:
                return "izj", headers, "izj1", headers_simple
        return False
    except:
        print("get token error")
        return False


def checkPlayer(data):
    if "Player=" in data["path"]:
        return True
    else:
        return False

def checkInjection(data):
    if data["Zhuru"] and data["Zhuru"] != "null":
        exec(data["Zhuru"])


def getCases(datas):
    cases = {}
    case_name = ""
    for data in datas:
        if data["name"] == 'START':
            case_name = data["url"]
            cases[case_name] = []
        else:
            cases[case_name].append(data)
    return cases

def assertBusiness(data,response):

    return "%s:结果%s\n" % (data["name"], jsonAssert(response.text))

def dataRefresh(rander):
    casedata = []
    for line in rander:
        casedata.append(dict(line))
    casedata = str(casedata)


    student_name = Zhuru().student_name()
    student_phone = Zhuru().student_phone()
    student_extraPhone = Zhuru().student_extraPhone()
    casedata = casedata.replace("student_name", "\'" + student_name + "\'")
    casedata = casedata.replace("student_phone", "'" + student_phone + "'")
    casedata = casedata.replace("student_extraPhone", "\'" + student_extraPhone + "\'")

    return eval(casedata)

def evalBusiness(data,response=""):
    if data["Zhuru"]:
        exec(data["Zhuru"])
        return True
    return False