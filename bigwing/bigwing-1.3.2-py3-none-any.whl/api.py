#!/usr/bin/env python
# coding: utf-8

import requests as req
import json
import pandas as pd
import warnings
from IPython.display import clear_output
from time import sleep
from abc import *
warnings.filterwarnings("ignore")


class BigwingAPIProcessor(metaclass=ABCMeta) :
    ''' 빅윙추상클래스 '''
    def run(self, limit=True):
        pass

    def __fetch(self, address) :
        pass

    def insert(self, data, col) :
        '''
        검색대상 데이터셋 입력함수
        :param data: 데이터셋 (타입 : 데이터프레임)
        :param col: 검색 키워드 Column 지정 (타입 : 문자열)
        :return: 없음
        '''
        self._check("url") # 인증키 유효성 확인
    
        # 데이터 유효성 확인 및 삽입
        if data.__class__ != pd.DataFrame().__class__ :
            print("FAILED : 입력하신 데이터는 pandas 데이터프레임이 아닙니다.")
        else :
            if col not in data.columns :
                print("FAILED : 입력하신 데이터에 해당 컬럼이 존재하지 않습니다.")
            else :
                self.data = data
                self.col = col
                print("SUCCEEDED : 데이터를 삽입했습니다.")
        return self
    

    
    def takeout(self) :
        '''
        검색된 data를 리턴하는 Getter함수
        :return: 데이터프레임 타입 변수
        '''
        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        return self.data
    
    def get_param(self) :
        '''
        api 파라미터 정보를 리턴하는 Getter함수
        :return: Dict.items 객체 변수
        '''
        try:
            self.params
        except NameError:
            raise RuntimeError("FAILED : 인수를 설정하지 않았습니다.")
        return self.params.items()
    
    def _set_param(self) :
        '''
        api 파라미터 정보를 설정하는 Setter함수
        :return: 없음
        '''
        param_str = ""       
        for param_nm, param_val in self.params.items() :
            param_str = param_str + "&" + param_nm + "=" + param_val
        self.url = self.base_url + param_str

    def summary(self) :
        '''
        처리결과요약을 출력하는 함수
        :return: 없음
        '''
        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        print("- 처리 건수 : ",self.data.shape[0])
        print("- 성공 건수 : ",sum(self.data.처리상태 == "OK"))
        print("- 실패 건수 : ",sum(self.data.처리상태 != "OK"))
        print("- 성공율 : {}%".format(round(sum(self.data.처리상태 == "OK")/self.data.shape[0]*100,1)))
        
    def _check(self, attr) :
        '''
        클래스 속성이 존재하는지 검사하는 함수(클래스 내부사용)
        :param attr: 속성 변수
        :return: 없음
        '''
        try:
            getattr(self, attr)
        except AttributeError:
            raise RuntimeError("FAILED : {} 를 확인해주세요.".format(attr))


class Vwolrd_Geocoder(BigwingAPIProcessor) :
    '''브이월드 지오코더'''

    def __init__(self, key, crs="EPSG:5181",type_="ROAD") :
        '''
        브이월드 지오코더 클래스 생성자
        :param key: 브이월드 인증키 입력 인수
        :param crs: 좌표계 입력 인수 (Default : EPSG:5181)
        :param type_: 도로명 또는 지번 주소 지정 옵션 입력 인수 (Default : ROAD) # ROAD(도로명) or PARCEL(지번)
        '''
        #파라미터 설정
        self.base_url = "http://api.vworld.kr/req/address?service=address&request=getCoord"
        self.params = {}
        self.params["key"] = key #인증키 설정
        self.params['crs'] = crs #좌표계 설정
        self.params['type'] = type_ #도로명 또는 지번 설정 (ROAD or PARCEL)
        self.params['simple'] = "true" #간단한 출력설정
        self._set_param()
        
        #인증키 유효성 확인
        status = self.__fetch("서울특별시 종로구 세종로 1")[0]     
        if status != "OK" :
            del self.params['key'], self.url
            print("KEY " + status + " : 인증키를 다시 확인해주세요.")
        else :
            print("KEY " + status + " : 인증키 유효성 확인 성공!")
                    
    def __fetch(self, address) :
        '''
        입력된 검색주소를 통해 지오코딩 단일레코드 정보를 받아오는 함수
        :param address: 검색 키워드(주소)
        :return: 튜플 타입의 검색상태 및 좌표정보
        '''
        values = {}
        fetch_url = self.url +"&address="+ address
        
        for cnt in range(10) :
            try :     
                resp = req.get(fetch_url).text
            except :
                print("{}번째 Fetch".format(cnt+2))
                sleep(3)
                continue
            break
        resp = json.loads(resp)

        status = resp['response']['status'] #상태코드 조회
        if status == 'OK' :
            #반환데이터 변수저장
            values = resp['response']['result']['point']
            return tuple([status] + [value for value in values.items()])
        else :
            return tuple(["NOT_FOUND"])

    def run(self, limit=True) :
        '''
        api 호출을 일괄실행하는 함수
        limit 인수는 Boolean 자료형을 받습니다. (Default : True)
        limit이 True일경우, 처리상태가 "OK"인 행데이터는 Skip하고 연속진행
        :return: 없음
        '''
        self._check("data") #데이터 삽입여부 확인
        self._check("url") # 인증키 유효성 확인

        data = self.data.copy()
        if (limit == True) & ("처리상태" in data.columns) :
            data = data[data["처리상태"] != "OK"]
        data_size = len(data)
        succeed_cnt = 0
        if data_size != 0 :
            for idx, keyword in enumerate(data[self.col]) :
                #변환 및 저장
                values = self.__fetch(keyword)
                print("debug : ",values)
                if values[0] == "OK" :
                    succeed_cnt += 1
                for value in values[1:] :
                    self.data.loc[self.data[self.col]==keyword, value[0]] = value[1]
                self.data.loc[self.data[self.col]==keyword, "처리상태"] = values[0]
                #결과 출력
                print("{} / {} ... {}%".format(idx+1,data_size, round((idx+1)/data_size*100),1))
                print("{} --> {}".format(keyword,values))
                clear_output(wait=True)
        print("처리완료!")
        print("추가정상처리건수 : ", succeed_cnt)
        self.summary()

        
####구글지오코더####
class Google_Geocoder(BigwingAPIProcessor) :
             
    def __init__(self, key) :
        '''
        구글 지오코더 클래스 생성자
        :param key: 브이월드 인증키 입력 인수
        '''
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
        self.params = {}
        self.params["key"] = key #인증키 설정
        self._set_param()
        
        #인증키 유효성 확인
        status = self.__fetch("서울특별시 종로구 세종로 1")[0]    
        if status != "OK" :
            del self.params['key'], self.url
            print("KEY " + status + " : 인증키를 다시 확인해주세요.")
        else :
            print("KEY " + status + " : 인증키 유효성 확인 성공!")

    
    def __fetch(self, keyword) :
        '''
        입력된 검색주소를 통해 지오코딩 단일레코드 정보를 받아오는 함수
        :param address: 검색 키워드(주소)
        :return: 튜플 타입의 검색상태 및 좌표정보
        '''
        values = {}
        fetch_url = self.url +"&address="+ keyword
        
        for cnt in range(10) :
            try :     
                resp = req.get(fetch_url).text
            except :
                print("{}번째 Fetch".format(cnt+2))
                sleep(3)
                continue
            break
        resp = json.loads(resp)
        status = resp['status'] #상태코드 조회
        if status == 'OK' :
            values = resp['results'][0]['geometry']['location']
            return tuple([status] + [value for value in values.items()])
        else :
            return tuple(["NOT_FOUND"])

    def run(self, limit=True) :
        '''
        api 호출을 일괄실행하는 함수
        limit 인수는 Boolean 자료형을 받습니다. (Default : True)
        limit이 True일경우, 처리상태가 "OK"인 행데이터는 Skip하고 연속진행
        :return: 없음
        '''
        self._check("data") #데이터 삽입여부 확인
        self._check("url") # 인증키 유효성 확인

        data = self.data.copy()
        if (limit == True) & ("처리상태" in data.columns) :
            data = data[data["처리상태"] != "OK"]
        data_size = len(data)
        succeed_cnt = 0
        if data_size != 0 :
            for idx, keyword in enumerate(data[self.col]) :
                #변환 및 저장
                values = self.__fetch(keyword)
                print("debug : ",values)
                if values[0] == "OK" :
                    succeed_cnt += 1
                for value in values[1:] :
                    self.data.loc[self.data[self.col]==keyword, value[0]] = value[1]
                self.data.loc[self.data[self.col]==keyword, "처리상태"] = values[0]
                #결과 출력
                print("{} / {} ... {}%".format(idx+1,data_size, round((idx+1)/data_size*100),1))
                print("{} --> {}".format(keyword,values))
                clear_output(wait=True)
        print("처리완료!")
        print("추가정상처리건수 : ", succeed_cnt)
        self.summary()
            
### 행정안전부 도로명주소변환기 ####
class AddressConverter(BigwingAPIProcessor) :

    def __init__(self, key) :
        '''
        도로명주소 변환기 클래스 생성자
        :param key: 행정안전부 주소검색 사이트 인증키 입력 인수
        '''
        self.base_url = "http://www.juso.go.kr/addrlink/addrLinkApi.do?"
        self.params = {}
        self.params["confmKey"] = key #인증키 설정
        self.params['currentPage'] = "1" 
        self.params['countPerPage'] = "10"
        self.params['resultType'] = "json" 
        self._set_param()
        
        #인증키 유효성 확인
        status = self.__fetch("서울특별시 종로구 세종로 1")[0]
        if status != "OK" :
            del self.params['confmKey'], self.url
            print("KEY " + status + " : 인증키를 다시 확인해주세요.")
        else :
            print("KEY " + status + " : 인증키 유효성 확인 성공!")   
    
    def __fetch(self, keyword) :
        '''
        입력된 검색주소를 통해 변환정보 단일레코드 정보를 받아오는 함수
        :param keyword: 검색 키워드(주소)
        :return: 튜플 타입의 검색상태 및 변환 주소정보
        '''
        values = {}
        fetch_url = self.url +"&keyword="+ keyword
        
        for cnt in range(10) :
            try :     
                resp = req.get(fetch_url).text
            except :
                print("{}번째 Fetch".format(cnt+2))
                sleep(3)
                continue
            break
        resp = json.loads(resp)
        
        status = "OK" if "juso" in resp["results"].keys() else "NOT_FOUND" #상태코드 조회
        if status == 'OK':
            if resp["results"]["juso"]:
                values = resp['results']['juso'][0]
                return tuple([status] + [value for value in values.items()])
            else:
                return tuple(["NOT_FOUND"])
        else :
            return tuple(["NOT_FOUND"])

    def run(self, limit=True) :
        '''
        api 호출을 일괄실행하는 함수
        limit 인수는 Boolean 자료형을 받습니다. (Default : True)
        limit이 True일경우, 처리상태가 "OK"인 행데이터는 Skip하고 연속진행
        :return: 없음
        '''
        self._check("data") #데이터 삽입여부 확인
        self._check("url") # 인증키 유효성 확인

        data = self.data.copy()
        if (limit == True) & ("처리상태" in data.columns) :
            data = data[data["처리상태"] != "OK"]
        data_size = len(data)
        succeed_cnt = 0
        if data_size != 0 :
            for idx, keyword in enumerate(data[self.col]) :
                #변환 및 저장
                values = self.__fetch(keyword)
                print("debug : ",values)
                if values[0] == "OK" :
                    succeed_cnt += 1
                for value in values[1:] :
                    self.data.loc[self.data[self.col]==keyword, value[0]] = value[1]
                self.data.loc[self.data[self.col]==keyword, "처리상태"] = values[0]
                #결과 출력
                print("{} / {} ... {}%".format(idx+1,data_size, round((idx+1)/data_size*100),1))
                print("{} --> {}".format(keyword,values))
                clear_output(wait=True)
        print("처리완료!")
        print("추가정상처리건수 : ", succeed_cnt)
        self.summary()

class SuperAPICaller(BigwingAPIProcessor) :
    '''제너럴 API 요청 클래스'''

    def __init__(self, base_url, **params) :
        '''
        일반 API 요청 클래스 생성자
        :param base_url: BASE URL 입력 인수
        :param params: API 요청 파라미터 입력 인수
        '''
        self.base_url = base_url
        self.params = params
        self._set_param()

    def set_tagname(self, name) :
        '''
        검색어 태그 이름 파라미터 설정 Setter 함수
        :return: 없음
        '''
        self.tagname = name

    def set_status(self, status_loc, OK) :
        '''
        상태코드 위치와 정상코드를 설정합니다.
        :status_loc: dict객체로 추상화된 json 문서의 트리구조에서 상태코드의 위치를 지정하는 인수

         ex) self.status = "OK" if resp['results']['juso'] != [] else "NOT_FOUND"
             위 코드에서 resp['results']['juso'] 를 말함.
        :param OK: API가 정상적으로 값을 반환할 때, 함께 출력되는 "정상"을 의미하는 코드명을 입력받는 인수
        :return: 없음
        '''
        self.status_loc = status_loc
        self.OK = OK

    def set_values(self, values) :
        '''
        API요청으로 받아온 json 딕셔너리 객체에서 데이터의 위치를 설정하는 함수
        :param values: json 문서의 dict추상화 객체에서의 위치 값 설정 인수

        ex) values = resp['results']['juso'][0]

        :return: 없음
        '''
        self.values = values
        
    def __fetch(self, keyword) :
        '''
        입력된 검색주소를 통해 단일레코드 정보를 받아오는 함수
        :param keyword: 검색 키워드
        :return: 튜플 타입의 검색상태 및 정보
        '''
        values = {}
        fetch_url = self.url +"&" + self.tagname + "="+ keyword
        
        for cnt in range(10) :
            try :     
                resp = req.get(fetch_url).text
            except :
                print("{}번째 Fetch".format(cnt+2))
                sleep(3)
                continue
            break
        resp = json.loads(resp)
        
        status = "OK" if self.status_loc != self.OK else "NOT_FOUND" #상태코드 조회
        if status == 'OK' :
            return tuple([status] + [value for value in self.values.items()])
        else :
            return tuple(["NOT_FOUND"])

    def run(self, limit=True) :
        '''
        api 호출을 일괄실행하는 함수
        limit 인수는 Boolean 자료형을 받습니다. (Default : True)
        limit이 True일경우, 처리상태가 "OK"인 행데이터는 Skip하고 연속진행
        :return: 없음
        '''
        self._check("data") #데이터 삽입여부 확인
        self._check("url") # 인증키 유효성 확인

        data = self.data.copy()
        if (limit == True) & ("처리상태" in data.columns) :
            data = data[data["처리상태"] != "OK"]
        data_size = len(data)
        succeed_cnt = 0
        if data_size != 0 :
            for idx, keyword in enumerate(data[self.col]) :
                #변환 및 저장
                values = self.__fetch(keyword)
                print("debug : ",values)
                if values[0] == "OK" :
                    succeed_cnt += 1
                for value in values[1:] :
                    self.data.loc[self.data[self.col]==keyword, value[0]] = value[1]
                self.data.loc[self.data[self.col]==keyword, "처리상태"] = values[0]
                #결과 출력
                print("{} / {} ... {}%".format(idx+1,data_size, round((idx+1)/data_size*100),1))
                print("{} --> {}".format(keyword,values))
                clear_output(wait=True)
        print("처리완료!")
        print("추가정상처리건수 : ", succeed_cnt)
        self.summary()
