import requests,json
headers = {"Content-Type": "application/json; charset=utf-8",
"Authorization": "Bearer eyJrIjoiTWxJcndvSGYzOXFEbXoxY1BLM1ZRUG9tMVBsTExyM2siLCJuIjoiYXBpa2V5Y3VybCIsImlkIjoyfQ=="
}
headers2 = {
"Content-Type": "application/json; charset=utf-8",
    "Authorization":"Bearer eyJrIjoiUFFWWm1SbDVPckpKdGRNS3E5bW10SWRNdUo3VENCS2QiLCJuIjoidGVzdCIsImlkIjoyNTB9=="
}
def create_user1():
    #CREA EL USUARIO PERO NO LO ASOCIA A LA ORGANISATION
    url = 'http://admin:admin@ec2-18-216-89-176.us-east-2.compute.amazonaws.com:3000/api/admin/users'
    data = {
        "loginOrEmail": "usuario123",
        "role": "Viewer",
        "password":"12345678",
        "email":"test22@gmail.com"
        #"orgId":250
    }
    res = requests.post(url=url,data=json.dumps(data),headers=headers)
    print(res.content,res.status_code,res.reason)

def create_user2():
    url = 'http://admin:admin@ec2-18-216-89-176.us-east-2.compute.amazonaws.com:3000/api/orgs/250/users'
    data = {
        "loginOrEmail": "usuario2",
        "role": "Viewer",
        "password":"12345678",
        "email":"test2@gmail.com",
        "orgId":250
    }
    res = requests.post(url=url,data=json.dumps(data),headers=headers)
    print(res.content,res.status_code,res.reason)


def remove_folder_perssions():
    url = 'http://admin:admin@ec2-18-216-89-176.us-east-2.compute.amazonaws.com:3000/api/folders/cMIMPZNmz/permissions'
    data = {
        "items": [
            {
                "role": "Viewer",
                "permission": 1
            },
            # {
            #     "role": "Editor",
            #     "permission": 2
            # },
            # {
            #     "teamId": 1,
            #     "permission": 1
            # },
            # {
            #     "userId": 11,
            #     "permission": 4
            # }
        ]
    }
    res = requests.post(url=url,data=json.dumps(data),headers=headers)
    print(res.content,res.status_code,res.reason)