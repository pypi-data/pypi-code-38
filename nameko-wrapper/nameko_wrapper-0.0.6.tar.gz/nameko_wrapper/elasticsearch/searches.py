"""
Search Object Wrapper
"""
from elasticsearch_dsl import Search, MultiSearch, connections

from .utils.formatters import SearchResultFormatter


class SearchBase(object):
    """Search Base Class"""

    def search(self):
        """原始搜索方法，返回原始搜索结果"""
        pass

    @property
    def result(self):
        raise NotImplementedError('Not implement `result` property method.')


class ESSearch(SearchBase):
    """ElasticSearch Search"""

    def __init__(self, search, schema=None, *args, page=None, many=False, raise_exception=True, **kwargs):
        """

        Args:
            search: ElasticSearch Search object instance
            schema: 用于格式化输出结果（marshmallow schema class)
            page: pagination info dict
                format:
                    {
                        'offset': int,
                        'size': int
                    }
            many: 控制返回结果是否为多个
            raise_exception: 当`many=False`，结果查询为空时是否触发异常
        """
        self._search = search
        self.schema = schema
        self.page = page
        self.many = many
        self._args = args
        self._kwargs = kwargs
        self.raise_exception = raise_exception

    def search(self):
        """执行搜索并返回原始搜索结果"""
        if self.page and 'offset' in self.page and 'size' in self.page:
            search = self._search[self.page['offset']:(self.page['offset'] + self.page['size'])]
            return {'result': search.execute(), 'total': search.count()}
        else:
            search = self._search
            return {'result': search.execute()}

    @property
    def result(self):
        """返回最终搜索结果列表"""

        # 根据不同的返回要求，控制搜索结果为空的时候是否引发异常
        # raise_exception = False if self.many else True

        return SearchResultFormatter(
            self.search(), schema=self.schema, many=self.many, raise_exception=self.raise_exception,
            *self._args, **self._kwargs
        ).data


class DslSearch(SearchBase):
    """通过原始DSL查询进行搜索"""

    def __init__(self, dsl, *args, **kwargs):
        """
        Elasticsearch DSL search interface

        Args:
            data:
                {
                    'header': # 查询条件控制（此处为Elasticsearch搜索控制添加）
                        {
                            'index': 'f5-*',    # Such as: index, ...
                            ...
                        }
                    'body':  # DSL 查询语句
                }

        Returns:
            Elasticsearch 原生查询结果（和使用DSL查询结果一致）
        """
        self.dsl = dsl
        self.header = dsl['header']
        self.body = dsl['body']

    def search(self):
        search = Search(**self.header).from_dict(self.body)
        result = search.execute()
        return {'result': result}

    @property
    def result(self):
        return self.search()['result']


class MultiDslSearch(SearchBase):
    """
    Elasticsearch Multi DSL Search interface
    """

    def __init__(self, raw_dsl, index=None, **kwargs):
        """通过DSL字符串查询并返回结果

        Args:
            raw_dsl: 原始DSL字符串
            index: 索引同`elasticsearch` msearch()方法`index`

        Returns:
            返回原始响应数据
        """
        self.raw_dsl = raw_dsl
        self.index = index
        self._kwargs = kwargs

    def search(self):
        c = connections.get_connection()
        result = c.msearch(body=self.raw_dsl, index=self.index, **self._kwargs)
        return {'result': result}

    @property
    def result(self):
        return self.search()['result']

