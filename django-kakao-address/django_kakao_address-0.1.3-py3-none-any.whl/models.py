from django.db import models


class KakaoAddress(models.Model):
    CHOICES_ADDRESS_TYPE = (('R', '도로명'), ('J', '지번'))
    CHOICES_LANGUAGE_TYPE = (('K', '한글주소'), ('E', '영문주소'))

    # 우편번호
    zipcode = models.CharField('우편번호', max_length=10, help_text='국가기초구역번호. 2015년 8월 1일부터 시행되는 새 우편번호')
    postcode = models.CharField('구 우편번호', max_length=7, help_text='2015년 8월 1일 이후 업데이트 없음')
    postcode1 = models.CharField('구 우편번호 앞 3자리', max_length=3, help_text='2015년 8월 1일 이후 업데이트 없음')
    postcode2 = models.CharField('구 우편번호 뒤 3자리', max_length=3, help_text='2015년 8월 1일 이후 업데이트 없음')

    # 주소
    road_address = models.CharField('도로명주소', max_length=200)
    road_address_english = models.CharField('도로명 영문주소', max_length=200)
    jibun_address = models.CharField('지번주소', max_length=200)
    jibun_address_english = models.CharField('지번 영문주소', max_length=200)

    # 건물
    building_code = models.CharField('건물관리번호', max_length=50)
    building_name = models.CharField('건물명', max_length=50)
    is_apartment = models.BooleanField('공동주택여부', help_text='아파트, 연립주택, 다세대주택 등')

    # 행정구역
    sido = models.CharField('도/시 이름', max_length=20)
    sigungu = models.CharField('시/군/구 이름', max_length=30)
    sigungu_code = models.CharField('시/군/구 코드', max_length=10, help_text='5자리 구성된 시/군/구 코드')
    roadname = models.CharField('도로명 값', max_length=20, help_text='검색 결과 중 선택한 "도로명"의 값이 들어감 (건물번호 제외)')
    roadname_code = models.CharField('도로명 코드', max_length=20)
    bname = models.CharField('법정동/법정리 이름', max_length=30)
    bname1 = models.CharField('법정리의 읍/면 이름', max_length=30, help_text='"동"지역일 경우 공백, "리"지역일 경우에는 "읍"또는 "면"정보가 들어감')
    bname2 = models.CharField('법정동/법정리 이름', max_length=30)
    hname = models.CharField('행정동 이름', max_length=30, help_text='검색어를 행정동으로 검색하고, 검색결과의 법정동과 검색어의 행정동이 다른 경우 표시')
