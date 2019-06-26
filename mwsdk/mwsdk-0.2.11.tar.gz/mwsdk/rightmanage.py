import requests
from consul import Consul
from collections import namedtuple
from mwutils.mw_consul import ServiceConf
import warnings
import aiohttp


User = namedtuple('User', ['uid', 'username', 'issystemuser','ismanageuser','manageuserid'])

class RightmanageError(Exception):
    pass

class Rightmanage():
    def __init__(self):
        self.service_name = 'rightmanage'
        consul = Consul()
        auth_conf = consul.catalog.service(self.service_name,tag='kong')[1]
        if not auth_conf:
            raise Exception('The %s service is not exist!'%self.service_name)
        self.ip = auth_conf[0]['ServiceAddress']
        self.port = auth_conf[0]['ServicePort']

    # curl -X GET --header 'Accept: chatset=utf8' 'http://192.168.101.31:8000/rightmanage/v1.0/cur-permissions?systemname=maxguideweb&jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0ZGI1Y2Y0YzVhNWY0NGU5OWY1YTFkMTdhZWY0ODExNiIsImV4cCI6MTUwMjQ3ODAwMH0.XiIDlOFQ3I1n5P5kivSw6ESDapGe7dfFXUIAcZmlXC0'
    def cur_permissions(self,systemname,jwt,version='v1.0'):
        headers = {'Accept': 'chatset=utf8'}
        data = {'systemname':systemname,'jwt':jwt}
        resp = requests.get('http://{ip}:{port}/{service}/{version}/cur-permissions'.format(ip=self.ip,
                            port=self.port,version=version,service=self.service_name),
                      params=data,headers=headers)

        return resp.status_code,resp.json()

    # curl -X GET --header 'Accept: chatset=utf8' 'http://192.168.101.31:8000/rightmanage/v1.0/cur-user?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0ZGI1Y2Y0YzVhNWY0NGU5OWY1YTFkMTdhZWY0ODExNiIsImV4cCI6MTUwMjQ3ODAwMH0.XiIDlOFQ3I1n5P5kivSw6ESDapGe7dfFXUIAcZmlXC0'
    def cur_user(self,jwt,version='v1.0'):
        '''
        返回值是json
        {"uid": self.uid,   #user.id
        "uname": self.uname, # user.name
        "systemuser":self.systemuser, #user.issystemuser
            "manageuser":self.manageuser,
            "manageuserid":self.manageuserid}
        '''
        warnings.warn("cur_user is deprecated, "
                      "use g.current_user instead",
                      DeprecationWarning)
        headers = {'Accept': 'chatset=utf8'}
        data = {'jwt':jwt}
        resp = requests.get('http://{ip}:{port}/{service}/{version}/cur-user'.format(ip=self.ip,
                            port=self.port,version=version,service=self.service_name),
                      params=data,headers=headers)
        return resp.status_code,resp.json()

    def login_user(self,jwt,version='v1.0'):
        warnings.warn("login_user is deprecated, "
                      "use g.current_user instead",
                      DeprecationWarning)
        _, user_js = self.cur_user(jwt,version)
        return User(uid=user_js['uid'],
                    username=user_js['uname'],
                    issystemuser=user_js['systemuser'],
                    ismanageuser=user_js['manageuser'],
                    manageuserid=user_js['manageuserid']
                    )

class Rightmanage_inner():
    '''
    内部API ，跳过auth，便于使用
    '''
    def __init__(self):
        self.service_name = 'rightmanage'
        auth_conf = ServiceConf(self.service_name,'inner',near=True)
        self.ip = auth_conf.ip
        self.port = auth_conf.port

    # curl -X GET --header 'Accept: application/json' 'http://192.168.101.75:8003/rightmanage-ext/v1.0/permissions?systemname=maxguideweb&user_id=1999'
    def permissions(self,systemname,userid,version='v1.0'):
        headers = {'Accept': 'chatset=utf8'}
        data = {'systemname':systemname,'user_id':userid}
        resp = requests.get('http://{ip}:{port}/rightmanage-ext/{version}/permissions'.format(ip=self.ip,
                            port=self.port,version=version),
                      params=data,headers=headers)
        return resp.status_code,resp.json()

    def create_user(self,login_userid,new_username,new_passwordmd5,companyid):
        '''
        为公司创建一个主账户，公司必须在资料库中已存在
        :param login_userid: 登录用户的id
        :param new_username: 新用户名
        :param new_passwordmd5: 新用户密码的md5值
        :param companyid: 新用户分配的公司
        :return:
        '''
        headers = {'Accept': 'chatset=utf8'}
        params = {'user_id':login_userid}
        data = {"uname":new_username,"passwordmd5":new_passwordmd5,"companyid":companyid}
        resp = requests.post('http://{ip}:{port}/rightmanage-ext/v1.0/users'.format(ip=self.ip,
                            port=self.port),params=params,
                            json=data,headers=headers)
        return resp.status_code,resp.json()

    def refresh_permissions(self,companyid):
        '''
        刷新redis中某个公司的权限
        :param companyid: 需刷新的compony.id
        :return:
        '''
        headers = {'Accept': 'chatset=utf8'}
        resp = requests.get('http://{ip}:{port}/rightmanage-ext/v1.0/refresh-permissions/{companyid}'.format(ip=self.ip,
                            port=self.port,companyid=companyid),
                            headers=headers)
        if resp.status_code==422:
            raise Exception(resp.json()['error'])
        elif resp.status_code!=200:
            raise Exception(resp.text)
        return resp.status_code

class AIORightmanage_inner():
    '''
    内部API ，跳过auth，便于使用
    支持异步获取权限资料
    '''
    def __init__(self):
        self.service_name = 'rightmanage'
        auth_conf = ServiceConf(self.service_name,'inner')
        self.ip = auth_conf.ip
        self.port = auth_conf.port

    # curl -X GET --header 'Accept: application/json' 'http://192.168.101.75:8003/rightmanage-ext/v1.0/permissions?systemname=maxguideweb&user_id=1999'
    async def permissions(self,systemname,userid,version='v1.0'):
        headers = {'Accept': 'chatset=utf8'}
        params = {'systemname':systemname,'user_id':userid}
        async with aiohttp.ClientSession() as session:
            async with session.get('http://{ip}:{port}/rightmanage-ext/{version}/permissions'.format(ip=self.ip,
                            port=self.port,version=version), params=params) as resp:
                status = resp.status
                resp_json = await resp.json()
        return status,resp_json

if __name__ == '__main__':
    rm = Rightmanage_inner()
    # print(auth.login_jwt('ksbus','698d51a19d8a121ce581499d7b701668'))
    code ,result = rm.create_user('aaa','aa','aa','aa')
    print(result)