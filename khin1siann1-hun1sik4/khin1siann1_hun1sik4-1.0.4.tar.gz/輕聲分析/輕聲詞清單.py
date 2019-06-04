from os.path import dirname
from os import path
import csv
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.解析整理.解析錯誤 import 解析錯誤


class 輕聲詞清單:

    @classmethod
    def 讀輕聲詞清單(cls):
        分寫清單 = []
        連寫清單 = []
        清單路徑 = path.join(dirname(dirname(__file__)), '輕聲詞資料', '全部輕聲詞.csv')
        with open(清單路徑) as csvfile:
            資料指標 = csv.DictReader(csvfile)
            for 一資料 in 資料指標:
                本調臺羅 = 一資料['臺羅'].replace('--', '')
                漢字 = 一資料['漢字']
                try:
                    分詞 = (
                        拆文分析器
                        .對齊詞物件(漢字, 本調臺羅)
                        .看分詞()
                    )
                except 解析錯誤:
                    continue

                分連不處理 = 一資料['分連不處理']
                if 分連不處理 == '分寫':
                    分寫清單.append(分詞)
                elif 分連不處理 == '連寫':
                    連寫清單.append(分詞)
        return {
            '分寫清單': 分寫清單,
            '連寫清單': 連寫清單
        }
