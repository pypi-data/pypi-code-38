import argparse
import os
import sys

import pandas as pd

from practice.naver_kin_scraper.kin import naver_kin_with_image
from practice.naver_webtoon_scraper.webtoon2 import retrive_webtoon
from practice.durginfo.druginfo_scraper import drug_search
from practice.kofia_scraper import (
    pipe,
    get_kofia_fundlist, get_kofia_fund_detail_list, get_kofia_price_progress, get_kofia_settle_exso_list
)

sys.path.append('.')


MEDIA_ROOT = 'media'


def main():
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="TEST Scraper"
    )
    argparser.add_argument('keywords', help='검색할 키워드들 나열', nargs='*')
    argparser.add_argument('-titleId', '--titleId')

    argparser.add_argument('-search', '--search', nargs='?')

    argparser.add_argument('-start', '--start', type=int, default=0)
    argparser.add_argument('-end', '--end', type=int, default=0)
    argparser.add_argument('-sd', '--start_date', type=str)
    argparser.add_argument('-ed', '--end_date', type=str)
    argparser.add_argument('-o', '--output', type=str)
    argparser.add_argument('-fund_std_code', '--fund_std_code')
    argparser.add_argument('-cd', '--code')
    argparser.add_argument('-conn', '--db_conf_path', type=str)

    args = argparser.parse_args()
    try:
        app = args.keywords[0]
    except:
        return

    context = {
        'save_to': MEDIA_ROOT
    }

    if app in ['webtoon', 'toon']:
        context['titleId'] = args.titleId
        retrive_webtoon(context)

    if app in ['kin']:
        context['save_to'] = os.path.join(MEDIA_ROOT, 'kin')
        naver_kin_with_image(params={'query': args.search}, context=context)

    if app in ['druginfo', 'di']:
        params = {
            'q': args.search
        }
        drug_search(params)

    kwargs = dict(args._get_kwargs())
    if app in ['kofia']:
        sub_app = args.keywords[1]
        if sub_app in ['ls']:
            apply = get_kofia_fundlist
        elif sub_app in ['ls-al']:
            apply = get_kofia_fund_detail_list
        elif sub_app in ['pg']:
            apply = get_kofia_price_progress
        elif sub_app in ['ex']:
            apply = get_kofia_settle_exso_list

        else:
            raise ValueError(f"{sub_app} 은 명령어 리스트에 존재하지 않습니다.")
        pipe(apply, **kwargs)
        # print(df.head())


if __name__ == "__main__":
    main()
