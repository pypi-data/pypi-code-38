import pandas as pd


from scrapgo.utils.datecuts import slice_dates
from .utils import starts_after, connect_db, get_today_str_date, print_db_progress

from .scraper import *
from .settings import MIN_START_DATE, MAX_END_DATE
from .db.vars import (
    펀드정보테이블명, 지수테이블명,
    결산테이블명, 결산테이블컬럼매핑, 

    표준코드, 펀드명, 회사코드, 설정일, 스크랩여부, 상환여부, # FUNDINFO_TABLE
    기준일자, # FUNDINDEX_TABLE
    회계기말, 구분 # FUNDSETTTLE_TABLE
)


@starts_after(table_name=펀드정보테이블명, date_column_name=설정일)
@slice_dates(by='year')
def get_kofia_fundlist(**kwargs):
    sc = KofiaFundListScraper()
    r = sc.scrap(**kwargs)
    return pd.DataFrame(r['fund_list'])


def get_kofia_fund_detail(fund_std_code, **kwargs):
    kfinfo = KofiaFundInfoScraper()
    r = kfinfo.scrap(fund_std_code=fund_std_code)
    df_detail = pd.DataFrame(r['fund_detail'])
    df_etc = pd.DataFrame(r['fund_etc'])
    df_detail = pd.merge(df_detail, df_etc)
    return df_detail


@starts_after(table_name=펀드정보테이블명, date_column_name=설정일)
@slice_dates(by='month')
def get_kofia_fund_detail_list(**kwargs):
    sc = KofiaFundListScraper()
    r = sc.scrap(**kwargs)
    fund_list =  pd.DataFrame(r['fund_list'])
    details, etcs = [], []
    for index, fund in fund_list.iterrows():
        fund_std_code = fund['표준코드']
        scd = KofiaFundInfoScraper()
        r = scd.scrap(fund_std_code=fund_std_code)
        detail = pd.DataFrame(r['fund_detail'])
        etc = pd.DataFrame(r['fund_etc'])
        df = pd.merge(detail, etc, on='표준코드')
        details.append(df)
    detail = pd.concat(details, ignore_index=True)
    return pd.merge(fund_list, detail, on='표준코드')


@connect_db
def get_kofia_price_progress(db=None, **kwargs):
    fund_list = db.select(
        펀드정보테이블명, 
        columns=[표준코드, 회사코드, 설정일, 펀드명],
        where=f'{스크랩여부}="Y" AND {상환여부}="N"'
    )

    total_count = fund_list.shape[0]
    for i, (fund_std_code, company_code, start_date, fund_name) in enumerate(fund_list[[표준코드, 회사코드, 설정일, 펀드명]].values):
        initial_date = start_date
        if db:
            date = db.max(
                지수테이블명, 기준일자,
                where=f'{표준코드}="{fund_std_code}"'
            )
            if date:
                if date == get_today_str_date():
                    print(f"이미 {fund_std_code}({fund_name}) 의 오늘 자 지수 정보가 존재합니다.")
                    continue
                start_date = date
        sc = KofiaPriceProgressScraper()
        r = sc.scrap(
            fund_std_code=fund_std_code, company_code=company_code,
            start_date=start_date, end_date=MAX_END_DATE
        )
        df = pd.DataFrame(r['price_progress'])
        prefix = f"{fund_name}(설정일:{initial_date})에 대한 {df.shape[0]} 개의 새로운 지수 정보 저장중..."
        print_db_progress(total_count, i, 1, prefix=prefix)
        yield df


@starts_after(table_name=결산테이블명, date_column_name=회계기말)
@slice_dates(by='month')
def get_kofia_settle_exso_list(apply=펀드정보테이블명, **kwargs):
    sc = KofiaSettleExSoByDateScraper()
    r = sc.scrap(**kwargs)
    df =  pd.DataFrame(r['fund_exso_by_date'])
    return df


