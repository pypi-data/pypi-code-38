import requests 
import json
import random


def smsg(msg,rgistid_list):
    app_key="ba2d93a14664fd39bb4b5db5"
    master_secret="f241c5e5492ecdbbcffe306d"
    session=requests.Session()
    session.auth = (app_key, master_secret)
    headers = {}
    headers['user-agent'] = 'jpush-api-python-client'
    headers['connection'] = 'keep-alive'
    headers['content-type'] = 'application/json;charset:utf-8'
    timeout=10

    data={
    "platform": "all",
    "audience":{"registration_id":rgistid_list},
    "notification":{"alert":msg},
    "extra":{"type":1}
    }
    if rgistid_list=='all':
        data["audience"]='all'
    if msg.startswith('小标'):
        data["extra"]["type"]=1
    else:
        data["extra"]["type"]=2

    data=json.dumps(data,ensure_ascii=False).encode("utf-8")

    r= session.request("POST","https://api.jpush.cn/v3/push", data=data,headers=headers, timeout=timeout)


def test1():
    num=random.randint(1,20)
    num2=random.choice([2,5,7,10])
    msgs=['小标又为您找了%d条新的商机,快来看看吧'%num,"已经%d天没有为您找新的商机了，小标猜测您的关键字太冷门，点击修改一下吧"%num2]
    msg=random.choice(msgs)
    smsg(msg,'all')


if __name__=='__main__':
    rlist=["190e35f7e01cf893c0d","160a3797c82f2dd868b"]
    num=random.randint(1,20)
    num2=random.choice([2,5,7,10])
    msgs=['小标又为您找了%d条新的商机,快来看看吧'%num,"已经%d天没有为你找新的商机了，小标猜测您的关键字太冷门，点击修改一下吧"%num2]
    msg=random.choice(msgs)
    smsg(msg,rlist)

