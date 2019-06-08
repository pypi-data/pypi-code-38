import requests

class microservice:

    def __init__(self):

        return None

    def execute(self, url, function, query=None, headers=None, body=None):

        if body==None:
            if headers == None:
                headers={}

            response = requests.get(url=url+"/myfunction/"+str(function), params=query,headers=headers)

            return response.content
        else:
            if headers == None:
                headers={}

            response = requests.post(url=url+"/myfunction/"+str(function),params=query, headers=headers, data=body)

            return response.content


