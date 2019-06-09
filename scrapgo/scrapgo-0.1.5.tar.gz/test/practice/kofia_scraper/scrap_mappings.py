# 스크래핑용 컬럼 매핑

# FUNDINFO TABLE - LIST
SCRAPMAP_FUND_LIST_COLUMNS = {
    'tmpv1': '회사',
    'tmpv2': '펀드명',
    'tmpv3': '설정일',
    'tmpv4': '펀드유형',
    'tmpv5': '투자지역',
    'tmpv8': '수탁회사',
    'tmpv9': '대표판매사',
    'tmpv10': '표준코드'
}

# FUNDINFO TABLE - DETAIL
SCRAPMAP_FUND_DETAIL_COLUMNS = {
    'vfundgbnm': '구분',
    'ufundtypnm': '상품분류',
    'vadditionalestmtdnm': '추가/단위구분',
    'establishmentdt': '최초설정일',
    'classcd': '분류코드',
    'shortcd': '단축코드',
    'trustacctrm': '신탁회계기간',
    'vinvestrgngbnm': '투자지역구분',
    'vsalergngbnm': '판매지역구분',
    'vprofittypecdnm': '운용실적공시분류',
    'vtraitdivnm': '특성분류',
    'vpripubgbnm': '공시/사모구분',
    'establishmentcot': '최소설정기준가격',
    'trusttrm': '신탁기간',
    'managerewrate': '운용보수',
    'salerewrate': '판매보수',
    'trustrewrate': '수탁보수',
    'generalofctrtrewrate': '일반사무수탁보수',
    'rewsum': '보수합계',
    'ter': '총비율이율(TER)',
    'frontendcmsrate': '선취수수료',
    'backendcmsrate': '후취수수료',
    'vmanagecompnm': '운용회사',
    'vgeneralofctrtcompnm': '일반사무수탁회사',
    'vtrustcompnm': '수탁회사상세',  # 겹쳐서 변경->'상세' postfixing
    'companycd': '회사코드',
    # 추가 정보
    'uoriginalamt': '설정원본',
    'netasstotamt': '순자산총액',

}

# 지수 테이블
SCRAPMAP_PRICE_PROGRESS_COLUMNS = {
    'standarddt': '기준일자',
    'standardcot': '기준가격',
    'vbefdayfltstdcot': '전일대비등락',
    'standardassstdcot': '과표기준가격',
    'uoriginalamt': '설정원본',  # 겹침
    'kospiepn': 'KOSPI',
    'kospi200epn': 'KOSPI200',
    'kosdaqepn': 'KOSDAQ',
    'tbondbnd3y': '국공채(3년만기)',
    'companybnd3y': '회사채(3년만기)',
}

# 결산 및 상환 테이블 - BY 펀드코드
SCRAPMAP_SETTLE_EXSO_COLUMNS = {
    'trustaccsrt': '신탁회계기초',
    'trustaccend': '신탁회계기말',
    'vpassdaycnt': '경과일수',
    'standardcot': '기준',
    'standardasscot': '과표',
    'uoriginalamt': '설정원본',  # 겹침
    'vsettlegbnm': '결산'
}

# 결산 및 상환 테이블 - BY DATE RANGE
SCRAPMAP_SETTLE_EXSO_BY_DATE_COLUMNS = {
    # 'tmpv1': '회사',
    # 'tmpv2': '펀드명',
    'tmpv3': '회계기초',
    'tmpv4': '회계기말',
    'tmpv5': '경과일수',
    'tmpv6': '설정원본',
    'tmpv7': '기준',
    'tmpv8': '과표',
    'tmpv9': '분배율',
    'tmpv10': '구분',
    'tmpv11': '표준코드'
}
