# Created by Q-ays.
# whosqays@gmail.com

# install elasticsearch_dsl before use

# elastic-search tools

from elasticsearch_dsl import Q


def o2d(obj):
    is_arr = isinstance(obj, list)
    is_set = isinstance(obj, set)

    if is_set or is_arr:
        res = []
        for o in obj:
            if not isinstance(o, dict):
                d0 = o.to_dict(include_meta=True)
                d1 = d0.get('_source')
                d1['id'] = d0.get('_id')
                res.append(d1)
            else:
                if o.get('_source'):
                    d0 = o.get('_source')
                    d0['id'] = o.get('_id')
                    res.append(d0)
                else:
                    res.append(o)

        return res

    if not isinstance(obj, dict):
        d0 = obj.to_dict(include_meta=True)
        d1 = d0.get('_source')
        d1['id'] = d0.get('_id')
        return d1
    else:
        if obj.get('data'):
            data = obj.get('data')
            obj['data'] = o2d(data)

        return obj


doc_type0 = 'doc'


def repo_ref(doc_type):
    """
    基于es数据库增删改查的公共类
    :param doc_type:
    :return:
    """
    class BaseRepo:

        def __init__(self, ModelType, doc_type=doc_type):
            self.Model = ModelType
            self.index = ModelType.Index.name
            self.type = doc_type

        def add(self, data):
            print(data)
            model = self.Model(**data)
            model.save()
            return model

        def delete(self, did=None):
            if did:
                res = self.Model.get(did)
                res.delete()
                return res

        def update(self, did, data):
            model = self.Model.get(did)
            for key in data:
                if hasattr(model, key):
                    setattr(model, key, data[key])
            model.save()
            return model

        def get(self, did=None, p=None, **kwargs):
            if did:
                if isinstance(did, list):
                    obj = self.Model.mget(did)
                else:
                    obj = self.Model.get(did)
            else:
                s = self.Model.search()
                for key in kwargs:
                    if isinstance(kwargs[key], dict):
                        s = s.query('nested', path=key, query=Q('match', **{str(key) + '.id': kwargs[key].get('id')}))
                    else:
                        s = s.query('match', **{key: kwargs[key]})

                if isinstance(p, list) or isinstance(p, tuple):
                    s = s[p[0]:p[1]]
                    res = s.execute()
                else:
                    res = s.scan()

                obj = []
                for o in res:
                    obj.append(o)

            return obj

        def paging(self, p=(0, 10), **kwargs):
            s = self.Model.search()
            for key in kwargs:
                if isinstance(kwargs[key], dict):
                    s = s.query('nested', path=key, query=Q('match', **{str(key) + '.id': kwargs[key].get('id')}))
                else:
                    s = s.query('match', **{key: kwargs[key]})

            if isinstance(p, list) or isinstance(p, tuple):
                s = s[p[0]:p[1]]
                res = s.execute()
                obj = []
                for o in res:
                    obj.append(o)

                data = dict()
                data['loc'] = p[0]
                data['size'] = p[1]
                data['total'] = res.hits.total
                data['data'] = obj

                return data

    return BaseRepo


Repo = repo_ref(doc_type0)
