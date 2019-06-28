# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/6/21
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
import base64
import json
import time
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import cv2
import os
import numpy
from aip import AipFace


class BayesFaceRegister:
    __SEARCH = 'search'
    __MULTI_SEARCH = 'multi-search'
    __APP_ID = '14987471'
    __API_KEY = '5T5yB8G2OpFdCcVb1OK7ipap'
    __SECRET_KEY = 'juNdil9rcizpakslmUXSHRQzuo9h0T96'
    __GROUP_ID = 'bayes_test'
    __IMAGE_BASE64 = 'BASE64'
    __MAX_FACE_NUM = 10
    __MAX_USER_NUM = 1
    __MATCH_THRESHOLD = 90
    __TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'
    __MULTI_SEARCH_URL = 'https://aip.baidubce.com/rest/2.0/face/v3/multi-search'

    def __init__(self):
        self.baidu_client = AipFace(self.__APP_ID, self.__API_KEY, self.__SECRET_KEY)
        super().__init__()

    def token_acquire(self):
        params = {'grant_type': 'client_credentials',
                  'client_id': self.__API_KEY,
                  'client_secret': self.__SECRET_KEY}
        post_data = urlencode(params).encode('utf-8')
        req_ = Request(self.__TOKEN_URL, post_data)
        try:
            f_ = urlopen(req_, timeout=5)
            result_str_ = f_.read().decode('utf-8')
            res = json.loads(result_str_)
            f_.stop()
            if 'access_token' in res:
                return res['access_token']
            else:
                raise Exception('access_token not in result')
        except Exception as err:
            print('BayesFaceRecognize token_acquire failed: {}'.format(err))
            return None

    @staticmethod
    def img2base64(img_src):
        if isinstance(img_src, numpy.ndarray):
            img_str = cv2.imencode('.jpg', img_src)[1].tostring()
            img_base64 = base64.b64encode(img_str).decode('utf-8')
        else:
            img_str = cv2.imencode('.jpg', img_src)[1].tostring()
            img_base64 = base64.b64encode(img_str).decode('utf-8')
        return img_base64

    def search(self, img_src):
        try:
            img_base64 = self.img2base64(img_src)
            img_type = 'BASE64'
            group_id_list = self.__GROUP_ID
            options = {"quality_control": "NORMAL", "liveness_control": "LOW", "max_user_num": self.__MAX_USER_NUM}
            search_result = self.baidu_client.search(img_base64, img_type, group_id_list, options)
            if search_result['error_code'] == 0 and search_result['result']:
                return self.recognize_result(search_result['result'], self.__SEARCH)
            else:
                return None
        except Exception as err:
            print('BayesFaceRecognize search error happen:{}'.format(err))

    def multi_search(self, img_src):
        try:
            img_base64 = self.img2base64(img_src)
            request_url = self.__MULTI_SEARCH_URL
            data = {
                'image': img_base64,
                'image_type': self.__IMAGE_BASE64,
                'group_id_list': self.__GROUP_ID,
                'max_face_num': self.__MAX_FACE_NUM,
                'max_user_num': self.__MAX_USER_NUM,
                'match_threshold': self.__MATCH_THRESHOLD
            }
            params = urlencode(data).encode('utf-8')
            access_token = self.token_acquire()
            if access_token:
                request_url = request_url + "?access_token=" + access_token
                request = Request(url=request_url, data=params)
                request.add_header('Content-Type', 'application/json')
                response = urlopen(request)
                content = response.read().decode('utf-8')
                response.stop()
                if content:
                    content = json.loads(content)
                    if content['error_code'] == 0 and content['result']:
                        return self.recognize_result(content['result']['face_list'], self.__MULTI_SEARCH)
                    else:
                        return None
                else:
                    return None
            else:
                return None
        except Exception as err:
            print('BayesFaceRecognize multi_search error happen:{}'.format(err))

    def register(self, img_src, user_id, group_id=__GROUP_ID):
        # search_result = self.search(img_src)
        # if not search_result:
        #     print(1111)
        #     return None
        img_base64 = self.img2base64(img_src)
        img_type = 'BASE64'
        options = {"user_info": "{}'s info".format(user_id),
                   "quality_control": "NORMAL",
                   "liveness_control": "LOW"}
        return self.baidu_client.addUser(img_base64, img_type, group_id, user_id, options)

    def update(self, img_src, user_id, group_id=__GROUP_ID):
        img_base64 = self.img2base64(img_src)
        img_type = 'BASE64'
        options = {"user_info": "{}'s info".format(user_id),
                   "quality_control": "NORMAL",
                   "liveness_control": "LOW"}
        return self.baidu_client.updateUser(img_base64, img_type, group_id, user_id, options)

    def delete_face(self, user_id, face_token, group_id=''):
        return self.baidu_client.faceDelete(user_id, group_id, face_token)

    def delete_user(self, user_id, group_id):
        return self.baidu_client.deleteUser(group_id, user_id)

    def query_face(self, user_id, group_id):
        return self.baidu_client.faceGetlist(user_id, group_id)

    def query_user(self, user_id, group_id):
        return self.baidu_client.getUser(user_id, group_id)

    def recognize_result(self, content, res_type):
        face_result = list()
        if res_type == self.__SEARCH:
            face_info = dict()
            face_info['face_token'] = content['face_token']
            if isinstance(content['user_list'], list) and len(content['user_list']) >= 1:
                face_info['user_name'] = content['user_list'][0]['user_id']
                face_info['score'] = content['user_list'][0]['score']
            face_result.append(face_info)
        else:
            for face_res in content:
                face_info = dict()
                face_info['face_token'] = face_res['face_token']
                if isinstance(face_res['user_list'], list) and len(face_res['user_list']) >= 1:
                    face_info['user_name'] = face_res['user_list'][0]['user_id']
                    face_info['score'] = round(face_res['user_list'][0]['score'])
                if isinstance(face_res['location'], dict) and face_res['location']:
                    face_info['face_size'] = face_res['location']['width'] * face_res['location']['height']
                    face_info['face_top'] = face_res['location']['top']
                    face_info['face_left'] = face_res['location']['left']
                    face_info['face_draw'] = dict()
                    top_left_rec_left = face_res['location']['left'] - 10 if face_res['location']['left'] > 10 else 0
                    top_left_rec_top = face_res['location']['top'] - 30 if face_res['location']['top'] > 30 else 0
                    face_info['face_draw']['top_left_rec'] = (round(top_left_rec_left),
                                                              round(top_left_rec_top))
                    bottom_right_rec_right = face_res['location']['left'] + face_res['location']['width'] + 10
                    bottom_right_rec_bottom = face_res['location']['top'] + face_res['location']['height'] + 10
                    face_info['face_draw']['bottom_right_rec'] = (round(bottom_right_rec_right),
                                                                  round(bottom_right_rec_bottom))
                    top_left_text_rec_left = top_left_rec_left
                    top_left_text_rec_top = top_left_rec_top - 20 if top_left_rec_top > 20 else bottom_right_rec_bottom
                    face_info['face_draw']['top_left_text_rec'] = (round(top_left_text_rec_left),
                                                                   round(top_left_text_rec_top))
                    bottom_right_text_rec_right = bottom_right_rec_right
                    bottom_right_text_rec_bottom = top_left_text_rec_top + 20
                    face_info['face_draw']['bottom_right_text_rec'] = (round(bottom_right_text_rec_right),
                                                                       round(bottom_right_text_rec_bottom))
                    person_text_left = top_left_text_rec_left
                    person_text_bottom = top_left_text_rec_top + 16
                    face_info['face_draw']['face_username_text'] = (round(person_text_left),
                                                                    round(person_text_bottom))
                face_result.append(face_info)
        return face_result


def face_register(face_path):
    try:
        dir_files = os.listdir(face_path)
    except FileNotFoundError:
        print('input face path is wrong, please check your path')
        return
    bayes_face = BayesFaceRegister()
    for filename in dir_files:
        file_path = os.path.join(face_path, filename)
        if os.path.isdir(file_path):
            continue
        if os.path.isfile(file_path):
            user_id = filename.split('.')[0]
            img_format = filename.split('.')[-1]
            if img_format not in ['png', 'jpg', 'bmp']:
                print('{} is not a supported image format'.format(filename))
                continue
            try:
                img_file = cv2.imread(file_path)
                res = bayes_face.register(img_file, user_id=user_id)
                if res and res['error_code'] == 0:
                    print('{} register success'.format(user_id))
                else:
                    print('{} register failed, error:{}'.format(user_id, res['error_msg']))
                    continue
            except Exception as err:
                print('{} register failed, error:{}'.format(user_id, err))
                continue
    print('all image register success')
    return True


if __name__ == '__main__':
    t1 = time.clock()
    face_register(r'D:\Bayes\Product\EDUBOT\edubalibs\bayeslibs\app\vision\person\face')
    # img = cv2.imread(r'lvyaling.jpg')
    # baidu_face = BayesFaceRegister()
    # res = baidu_face.register(img, user_id='lvyaling')
    # print(res)
    # search_res1 = baidu_face.search(img)
    # search_res2 = baidu_face.multi_search(img)
    # # search_res = baidu_face.register(img)
    # # print(search_res1)
    # print(search_res2)
    # print('time spend:{}'.format(time.clock() - t1))
    # if search_res2:
    #     cv2.namedWindow('test', cv2.WINDOW_NORMAL)
    #     cv2.resizeWindow('test', 400, 300)
    #     for draw_info in search_res2:
    #         cv2.rectangle(img, draw_info['face_draw']['top_left_rec'], draw_info['face_draw']['bottom_right_rec'],
    #                       (0, 0, 255), 2)
    #
    #         cv2.rectangle(img, draw_info['face_draw']['top_left_text_rec'],
    #                       draw_info['face_draw']['bottom_right_text_rec'],
    #                       (0, 0, 255), -1)
    #         cv2.rectangle(img, draw_info['face_draw']['top_left_text_rec'],
    #                       draw_info['face_draw']['bottom_right_text_rec'],
    #                       (0, 0, 255), 2)
    #
    #         cv2.putText(img, '{}:{}'.format(draw_info['user_name'], draw_info['score']),
    #                     draw_info['face_draw']['face_username_text'],
    #                     cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1,
    #                     cv2.LINE_AA)
    #     cv2.imshow('test', img)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
