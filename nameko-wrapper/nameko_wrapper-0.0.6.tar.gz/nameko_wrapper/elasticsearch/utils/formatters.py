"""
内容格式化器
"""
from nameko_wrapper.exceptions import NotFound


class SearchResultFormatter(object):
    """
    ElasticSearch Search Result Formatter
    """

    def __init__(self, result, schema=None, *, many=False, include_id=True, raise_exception=False):
        """
        Args:
            result: ElasticSearch Search结果（包括Search结果和详情结果）
                format:
                    {
                        'result': search.execute(),  # 必须
                        ...
                        'total': 总数
                    }
            schema: 表单格式化输出
            many: 搜索结果是否为列表
            include_id: 返回结果是否包含id
        """
        self.result = result
        self.schema = schema
        self.many = many
        self.include_id = include_id
        self.raise_exception = raise_exception

    def _item_format(self, item):
        """结果项格式化
        结构：
            {
                "_id": ,
                "_index": ,
                "_type": ,
                "_source": {},

                "found": true/false,    # item result 独有
                "_version": ,           # item result 独有
                "_score": ,             # list result 独有
            }
        """
        if self.include_id:
            if 'id' not in item['_source']:
                item['_source']['id'] = item['_id']
                return item['_source']

        return item['_source']

    @property
    def data(self):
        """返回格式化结果"""
        # result.hits.hits 始终为列表对象
        result = [self._item_format(item) for item in self.result['result'].hits.hits]
        if self.schema:
            result = self.schema().dump(result, many=True)

        if not self.many:
            if result:
                result = result[0]
            else:
                if self.raise_exception:
                    raise NotFound
                else:
                    result = None
        self.result.update(result=result)
        return self.result


class SearchFormatter(SearchResultFormatter):
    """ElasticSearch Search and Search Result Format"""

    def __init__(self, search, *args, **kwargs):
        """
        Search执行后结果形式：
            1. result.hits.hits -> []
        Args:
            search: ElasticSearch 搜索对象
            *args:
            **kwargs:
        """
        result = search.execute()
        super().__init__({'result': result}, *args, **kwargs)
