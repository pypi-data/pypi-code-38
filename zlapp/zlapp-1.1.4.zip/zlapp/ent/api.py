import requests 


#365 企业信息，通过精准企业名称 或机构代码获取企业基本信息
def get_base(name=None,id=None):

    url="http://open.api.tianyancha.com/services/v4/open/baseinfoV3"

    headers={"Authorization":"18b501ac-77ca-4be8-89e7-7742aa64eff0"}
    data={}
    if name is not None:
        data["name"]=name
    if id is not None:
        data["id"]=id
    #print(data)
    r=requests.get(url,headers=headers, params=data)
    result=r.json()
    if 'error_code' not in result:return False 
    if result['error_code']==0:
        return result["result"]
    else:
        return None 

#736 根据统一社会信用代码获取基本信息和股东信息
def get_sh(tydm):
    url="http://open.api.tianyancha.com/services/v4/open/getCompanyByCode"
    headers={"Authorization":"18b501ac-77ca-4be8-89e7-7742aa64eff0"}
    data={"code":tydm}
    r=requests.get(url,headers=headers, params=data)
    result=r.json()
    if 'error_code' not in result:return False 
    if result['error_code']==0:
        return result["result"]
    else:
        return None 


#353 搜索

def get_ss(word):
    url="http://open.api.tianyancha.com/services/v4/open/searchV2"
    headers={"Authorization":"18b501ac-77ca-4be8-89e7-7742aa64eff0"}
    data={"word":word}
    r=requests.get(url,headers=headers, params=data)
    result=r.json()
    if 'error_code' not in result:return False 
    if result['error_code']==0:
        return result["result"]
    else:
        return None 

#370 变更记录 

def get_alter(name=None,id=None,pageNum=1):
    url="http://open.api.tianyancha.com/services/v4/open/changeinfo"
    headers={"Authorization":"18b501ac-77ca-4be8-89e7-7742aa64eff0"}
    data={"pageNum":pageNum}
    if name is not None:
            data["name"]=name
    if id is not None:
            data["id"]=id
    r=requests.get(url,headers=headers, params=data)
    result=r.json() 
    if 'error_code' not in result:return False
    if result['error_code']==0:

        return result["result"]
    else:
        return None 

def get_alters(name=None,id=None):

    a1=get_alter(name=name,id=id)
    if a1 is None:return None 
    if a1 is False:return False 

    total=a1['total']

    b1=a1['items']

    if total<=20:
        return b1
    pages=int(total/20)+1

    for i in range(pages-1):
        b=get_alter(name=name,id=id,pageNum=i+2)
        if b is not False and b is not None:
            b1.extend(b['items'])
    return b1




# x1="北京筑龙信息技术有限责任公司"

# x2="199557844"

# x3="91110000802100433B"


# x4="深圳市派诺杰实业有限公司"