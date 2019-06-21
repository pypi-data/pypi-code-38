# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/1/25 0025
__author__ = 'huohuo'

import requests
from aip import AipOcr
import sys
reload(sys)
sys.setdefaultencoding('utf8')
APP_ID = '15486076'
API_KEY = 'cNnOpI7tSp0fOkSCRIprx4US'
SECRET_KEY = '5MIuHdx02gs2bDVtDgOwzA8lXRIEobm3'
template_id = '75728a7d5fbaa201049f6198f651305f'
# client_id 为官网获取的AK， client_secret 为官网获取的SK

client = AipOcr('15486462', 'vzYWYRTiZA6pzmQePdFw1rs1', 'ZUWT9fFedej78rLPngN1yfCCLz7I4Mxj')


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def print_result(result):
    for r in result:
        for k in r:
            print r[k], '\t',
        print '\n'


def my_rq(method, url, params=None, rq=None, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
    res = requests.request(method, url, params=params, headers=headers, json=rq)
    if res.status_code == 200:
        return res.json()
    return None


def get_access_token():
    params = {'grant_type': 'client_credentials', 'client_id': API_KEY, 'client_secret': SECRET_KEY}
    rq = my_rq('POST', 'https://aip.baidubce.com/oauth/2.0/token', params=params)
    if rq:
        return rq['access_token']
    return None


def get_img(img):
    access_token = get_access_token()
    if access_token is None:
        return None
    print access_token
    params = {'access_token': access_token}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    rq = {'image': img, 'templateSign': '75728a7d5fbaa201049f6198f651305f2019'}
    res = requests.request('POST', 'https://aip.baidubce.com/rest/2.0/solution/v1/iocr/recognise',
                params=params, headers=headers, data=rq)
    if res:
        print res.json()
    return None


image = get_file_content('test_aip.jpg')
data0 = client.basicAccurate(image)
print_result(data0['words_result'])
# get_img(image)
from jy_word.File import File
my_file = File()
data1 = client.custom(image, template_id)
# print data1
my_file.write('aip_test.json', data1)

if __name__ == "__main__":
    pass
    

