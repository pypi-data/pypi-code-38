import requests
import json
import os
import zipfile

class codeez:

    def __init__(self, User=None, Authorization=None):
        self.User = User
        self.url='https://api.codeez.tech/'
        self.UserAuthorization=Authorization

        headers={}
        headers['content-type'] = 'application/json'
        headers['User']=self.User
        headers['Authorization']=self.UserAuthorization

    def create_user(self, email, password, FirstName, LastName, AccountAuthorization):
        #try:
        headers={}
        headers['content-type'] = 'application/json'
        values={'email':email,'FirstName':FirstName,'LastName':LastName,'AccountAuthorization':AccountAuthorization,'credentials':{"password":password}}
        response = requests.post(url=self.url + 'users', headers=headers, data=json.dumps(values))

        if response.status_code == 200:
            #print(response.text)
            self.User=json.loads(response.text)['User']
            self.UserAuthorization=json.loads(response.text)['Authorization']
            return json.loads(response.text)
        else:
            return response.text,response.status_code

    def request_account(self, email, GroupName, Description):
        headers = {}
        headers['content-type'] = 'application/json'
        values = {'email': email, 'GroupName': GroupName, 'Description': Description}

        response = requests.request("POST", url=self.url + 'accounts/request', headers=headers, data=json.dumps(values))

        return response.text, response.status_code


    def servicelist(self):
        headers = {}
        if headers != None:
            headers['content-type'] = 'application/json'
        else:
            headers = {'content-type': 'application/json'}
        headers['User'] = self.User
        headers['Authorization'] = self.UserAuthorization
        try:
            response = requests.get(url=self.url + 'mservices', headers=headers)
        except:
            return {"error": "Something went wrong"}
        return json.loads(response.text),response.status_code

    def accountservicelist(self):
        headers = {}
        if headers != None:
            headers['content-type'] = 'application/json'
        else:
            headers = {'content-type': 'application/json'}
        headers['User'] = self.User
        headers['Authorization'] = self.UserAuthorization
        try:
            response = requests.get(url=self.url + 'accountmservices', headers=headers)
        except:
            return {"error": "Something went wrong"}
        return json.loads(response.text),response.status_code

    def connection(self,name):

        headers = {}
        headers['content-type'] = 'application/json'
        headers['User'] = self.User
        headers['Authorization'] = self.UserAuthorization

        try:
            response = requests.get(url=self.url + 'dbdetails/'+name, headers=headers)
        except:
            return {"error":"Something went wrong while retrieving db details. Check your micro-service has a database."}

        if response.status_code != 200:
            return json.loads(response.text), response.status_code

        details = json.loads(response.text)
        try:
            import psycopg2
        except:
            return {"error": "Please install psycopg2, not included in the codeez package","Database Info":{"host":details['host'],"port":details['port']}}

        host = details['host']
        port = details['port']
        self.dbHost=host
        self.dbPort=port
        connection = psycopg2.connect(host=host, port=port, user=self.User, password=self.UserAuthorization, dbname=name, sslmode='require')
        return connection

    def allservicelist(self):
        headers = {}
        if headers != None:
            headers['content-type'] = 'application/json'
        else:
            headers = {'content-type': 'application/json'}
        try:
            response = requests.get(url=self.url + 'allmservices', headers=headers)
        except:
            return {"error": "Something went wrong"}
        return json.loads(response.text),response.status_code

    def logs(self,name):
        headers = {}
        if headers != None:
            headers['content-type'] = 'application/json'
        else:
            headers = {'content-type': 'application/json'}
        headers['User'] = self.User
        headers['Authorization'] = self.UserAuthorization
        try:
            response = requests.get(url=self.url + 'logs/'+name, headers=headers)
        except:
            return {"error": "Something went wrong"}
        return json.loads(response.text),response.status_code


    def create(self,name,directory,type='MService',Description=None,Fork=False,Private=False,DB=False,ServiceName=None,ServiceAccount=None):

        User= self.User
        Authorization=self.UserAuthorization
        try:
            os.remove('/tmp/customer.zip')
        except:
            1==1

        #try:

        zipf = zipfile.ZipFile('/tmp/customer.zip', 'w', zipfile.ZIP_DEFLATED)
        os.chdir(directory)
        for root, dirs, files in os.walk('.'):
            for file in files:
                zipf.write(os.path.join(root, file))
        zipf.close()

        os.chdir('/tmp/')
        url=self.url
        files = {'file': open('customer.zip','rb')}
        #print(files)
        values = {'name': name,'User':User,'Authorization':Authorization,'Description':Description,'DB':DB,'Private':Private,'Fork':Fork}
        #except:
        #    return {"error":"Something went wrong"}
        #try:
        if type=='MService':
            response = requests.post(url=url+"mservices", files=files, data=values)
            #print(response.text)
            if response.status_code != 200:
                return {"error": response.text}, response.status_code
        elif type=='Site':
            if ServiceName != None and ServiceAccount != None:
                values['ServiceName']=ServiceName
                values['ServiceAccount']=ServiceAccount
            response = requests.post(url=url + "sites", files=files, data=values)
            # print(response.text)
            if response.status_code != 200:
                return {"error": response.text},response.status_code

        return json.loads(response.text)

    def update(self,name,directory,type='MService',Description=None,DB=False,Fork=False,Private=False,ServiceName=None,ServiceAccount=None):

        User= self.User
        Authorization=self.UserAuthorization
        try:
            os.remove('/tmp/customer.zip')
        except:
            1==1

        #try:
        zipf = zipfile.ZipFile('/tmp/customer.zip', 'w', zipfile.ZIP_DEFLATED)
        os.chdir(directory)
        for root, dirs, files in os.walk('.'):
            for file in files:
                zipf.write(os.path.join(root, file))
        zipf.close()

        os.chdir('/tmp/')
        url=self.url
        files = {'file': open('customer.zip','rb')}
        #print(files)
        values = {'name': name,'User':User,'Authorization':Authorization,'Description':Description,'DB':DB,'Private':Private,'Fork':Fork}

        if type=='MService':
            #response = requests.post(url=url+"mservices", files=files, data=values)

            response = requests.patch(url=url + "mservices", files=files, data=values)

        elif type=='Site':
            if ServiceName != None and ServiceAccount != None:
                values['ServiceName']=ServiceName
                values['ServiceAccount']=ServiceAccount
            response = requests.patch(url=url + "sites", files=files, data=values)

        if response.status_code != 200:
            return {"error": response.text, "error_code": response.status_code}
        #except:
        #    return {"error": "Something went wrong"}
        #try:
        os.remove('/tmp/customer.zip')
        #except:
        #    1==1
        return json.loads(response.text)

    def delete(self,name):

        Account= self.User
        Authorization=self.UserAuthorization

        #try:
        headers = {}
        headers['content-type'] = 'application/json'
        headers['User']=self.User
        headers['Authorization']=self.UserAuthorization
        values = {'name': name}

        response = requests.delete(url=self.url + 'mservices', headers=headers, data=json.dumps(values))

        if response.status_code != 200:
            return {"error": response.text,"error_code":response.status_code}

        return json.loads(response.text)

    def stop(self,name):

        Account= self.User
        Authorization=self.UserAuthorization

        #try:
        headers = {}
        headers['content-type'] = 'application/json'
        headers['User']=self.User
        headers['Authorization']=self.UserAuthorization
        values = {'name': name}
        type=None

        response = requests.post(url=self.url + 'mservices/stop', headers=headers, data=json.dumps(values))

        if response.status_code != 200:
            return {"error": response.text,"error_code":response.status_code}
        #except:
        #    return {"error": "Something went wrong"}

        return json.loads(response.text)

    def start(self,name):

        Account= self.User
        Authorization=self.UserAuthorization

        #try:
        headers = {}
        headers['content-type'] = 'application/json'
        headers['User']=self.User
        headers['Authorization']=self.UserAuthorization
        values = {'name': name}
        type=None

        response = requests.post(url=self.url + 'mservices/start', headers=headers, data=json.dumps(values))

        if response.status_code != 200:
            return {"error": response.text,"error_code":response.status_code}

        return json.loads(response.text)

    def store(self,name,Content):

        headers = {}

        headers['User'] = self.User
        headers['Authorization'] = self.UserAuthorization

        values = Content
        urlfunction = 'https://storage.codeez.tech/myfunction/store?Name='+name

        response = requests.post(url=urlfunction,headers=headers,data=values)
        if response.status_code != 200:
            return {"error": response.content,"error_code":response.status_code}
        else:
            return {"Storage": name, "Status": "Success"}

    def retrieve(self, name):

        headers = {}

        headers['User'] = self.User
        headers['Authorization'] = self.UserAuthorization

        urlfunction = 'https://storage.codeez.tech/myfunction/retrieve?Name=' + name

        response = requests.get(url=urlfunction, headers=headers)
        if response.status_code != 200:
            return {"error": response.content, "error_code": response.status_code}
        else:
            return response.content

