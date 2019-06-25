from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, Float, Long
import sense_core as sd
import re
import pypinyin
import datetime
import sqlalchemy

sd.log_init_config('core', '/tmp')


class RiskStockIndex(sd.Base, sd.BaseModel):
    __tablename__ = 'risk_stock_index'
    __label__ = "mysql_stock"
    __database__ = 'stock_db'

    id = sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True)
    stock_code = sqlalchemy.Column('stock_code', sqlalchemy.String(256))
    company_name = sqlalchemy.Column('company_name', sqlalchemy.DateTime)
    combine_risk_score = sqlalchemy.Column('combine_risk_score', sqlalchemy.Float)


class StockBasicDataDocTest(Document):
    stock_code = Text(analyzer='ik_max_word')
    company_name = Text(analyzer='pinyin')
    company_name_index = Text(analyzer='ik_max_word')
    company_name_first = Text(analyzer='standard')
    risk_score = Float()
    update_time = Date()

    class Index:
        name = 'stock_basic_data_test'
        using = 'es_default'


class StockBasicDataIndexer(sd.BaseIndexer):

    def __init__(self):
        super(StockBasicDataIndexer, self).__init__('es_default', StockBasicDataDocTest)

    @classmethod
    def build_pinyin(cls, company_name):
        company_name = company_name.lower()
        pinyin = re.sub("[a-zA-Z\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+", "", company_name)
        pinyin = ''.join(cls.chinese_to_pinyin(pinyin))
        if company_name.find('st') >= 0:
            pinyin = 'st' + pinyin
        return pinyin

    @classmethod
    def chinese_to_pinyin(cls, word, first=True):
        _res = []
        for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
            if first:
                _res.extend(i[0][0])
            else:
                _res.extend(i)
        return _res

    @classmethod
    def build_doc_param(cls, stock_code, company_name, risk_score):
        return {
            'stock_code': stock_code,
            'update_time': datetime.datetime.now().strftime('%Y-%m-%d'),
            'company_name_index': company_name,
            'company_name': company_name,
            'company_name_first': cls.build_pinyin(company_name),
            'risk_score': risk_score,
        }


def test_rebuild_index():
    indexer = StockBasicDataIndexer()
    indexer.init_rebuild_index()
    index_list = RiskStockIndex.get_all()
    for index in index_list:
        param = StockBasicDataIndexer.build_doc_param(index.stock_code, index.company_name, index.combine_risk_score)
        indexer.add_bulk_data(index.stock_code, param)
    indexer.done_rebuild_index()


def test_1():
    indexer = StockBasicDataIndexer()
    indexer.init_rebuild_index()
    indexer.done_rebuild_index()



