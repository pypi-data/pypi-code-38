import requests
from consul import Consul


class AuthError(Exception):
    pass

class Auth():
    def __init__(self):
        consul = Consul()
        auth_conf = consul.catalog.service('auth',tag='kong')[1]
        if not auth_conf:
            raise Exception('The auth service is not exist!')
        self.ip = auth_conf[0]['ServiceAddress']
        self.port = auth_conf[0]['ServicePort']

    # curl -X POST --header 'Content-Type: application/x-www-form-urlencoded' --header 'Accept: chatset=utf8' -d 'user=ksbus&password=698d51a19d8a121ce581499d7b701668' 'http://192.168.101.31:8000/auth/v1.0/login_jwt'
    def login_jwt(self,user,password,version='v1.0'):
        '''

        :param user:
        :param password: 密碼的MD5
        :param version:
        :return:
        '''
        headers = {'Content-Type':'application/x-www-form-urlencoded',
                  'Accept': 'chatset=utf8'}
        data = {'user':user,'password':password}
        resp = requests.post('http://{ip}:{port}/auth/{version}/login_jwt'.format(ip=self.ip,
                            port=self.port,version=version),
                      data=data,headers=headers)
        return resp.status_code,resp.json()

    # curl -X GET --header 'Accept: chatset=utf8' 'http://192.168.101.31:8000/auth/v1.0/logout_jwt?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI1ZjJiMzg0M2E4MWI0MWNkYmNhMzI5ODcyM2YzNmE2NyIsImV4cCI6MTUwMjQ3ODAwMH0.9Wist-q_iD_g8haOziJMd9iUYBNE-voQjEY69oqc2Co'
    def logout_jwt(self,jwt,version='v1.0'):
        headers = {'Accept': 'chatset=utf8'}
        data = {'jwt': jwt}
        resp = requests.get('http://{ip}:{port}/auth/{version}/logout_jwt'.format(ip=self.ip,
                                        port=self.port, version=version),
                             params=data, headers=headers)
        return resp.status_code, resp.json()

if __name__ == '__main__':
    auth = Auth()
    # print(auth.login_jwt('ksbus','698d51a19d8a121ce581499d7b701668'))
    print(auth.logout_jwt('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1NDZkZmMyNGU3NTI0ZDc5YjA3NDI1YzI5MzA5MzMwNCIsImV4cCI6MTUwMjQ3ODAwMH0.Kx5sarFv0hAkLwyRxSvqXotc7qyuWA0aur4C0Tr-PfI'))