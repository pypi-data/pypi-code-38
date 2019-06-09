from types import GeneratorType
from collections import namedtuple, abc

import pandas as pd

from scrapgo.lib.dataframe import dataframe2path, TableFrame

from .settings import OUTPUT_FILE_FORMAT

from .apps import get_kofia_fundlist, get_kofia_fund_detail_list, get_kofia_price_progress, get_kofia_settle_exso_list
from .db.vars import (
    구분, 표준코드, 상환여부,

    펀드정보테이블명, 펀드정보테이블기준키, 펀드정보테이블컬럼매핑,
    지수테이블명, 지수테이블기준키, 지수테이블컬럼매핑,
    결산테이블명, 결산테이블기준키, 결산테이블컬럼매핑,
)


App = namedtuple('App', 'prefix table uniques mapping updateto', defaults=('Fund', None, None, None, None,))

apps = {
    get_kofia_fundlist: App(
        'FundList_{start_date}~{end_date}',
    ),
    get_kofia_fund_detail_list: App(
        'FundDetailList_{start_date}~{end_date}',
        펀드정보테이블명, 펀드정보테이블기준키, 펀드정보테이블컬럼매핑
    ),
    get_kofia_price_progress: App(
        'FundPriceProgress',
        지수테이블명, 지수테이블기준키, 지수테이블컬럼매핑
    ),
    get_kofia_settle_exso_list: App(
        'FundSettleExsoList_{start_date}~{end_date}',
        결산테이블명, 결산테이블기준키, 결산테이블컬럼매핑,
        펀드정보테이블명 # 정보 받은 후 바로 업데이트 시도
    )
}

def pipe(app, **kwargs):
    output = kwargs.get('output')
    dbconn = kwargs.get('db_conf_path')
    meta = apps.get(app)
    if meta is None:
        raise ValueError(
            f"{app.__name__}은 설정 된 출력 파이프가 없습니다. pipeline.py 의 apps에서 지정할 수 있습니다."
        )
    df = app(**kwargs)
    if not isinstance(df, GeneratorType):
        df = [df]
    if output in OUTPUT_FILE_FORMAT or output is None:
        dataframe = pd.concat(df, ignore_index=True)
        if output is None:
            print(dataframe.head())
        else:
            filename = meta.prefix.format(**kwargs)
            dataframe2path(dataframe, filename, extension=output)
    elif output in ['db']:
        db = TableFrame(
            db_conf_path=dbconn
        )
        if not meta.table:
            raise ValueError("DB 로 Insert 할 테이블명이 설정 되지않았 습니다.")
        for dataframe in df:
            db.insert(
                dataframe, meta.table, meta.uniques, meta.mapping
            )
            if meta.updateto:
                table_for_updated = meta.updateto
                db.update(
                    dataframe,
                    table_for_updated,
                    index='표준코드',
                    pk=표준코드,
                    source_column='구분',
                    dest_column=상환여부,
                    valuemap={'상환': 'Y'},
                    default='N',
                )
    else:
        print(df.head())

