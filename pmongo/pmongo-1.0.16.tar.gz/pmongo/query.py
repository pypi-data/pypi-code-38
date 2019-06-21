# -*- coding: UTF-8 -*
'''
Created on 2018-06-15

@author: trb
'''

from .document import Manager


class QueryManger(Manager):
    def _wrap_query(self, q):
        from .utils import day_end
        nq = {}
        wrapm = {
            'integer': lambda v: {'$eq': int(v['integer'])},
            'gte': lambda v: {'$gte': v['gte'], },
            'gt': lambda v: {'$gt': v['gt'], },
            'lte': lambda v: {'$lte': day_end(v['lte']), },  # if type(v['lte']) == datetime.datetime else v['lte'], },
            'lt': lambda v: {'$lt': v['lt'], },
            'icontains': lambda v: {'$regex': v['icontains'], '$options': 'im'},
            'float': lambda v: {'$eq': float(v['integer'])},
            'decimal': lambda v: {'$eq': float(v['decimal'])},
            'text': lambda v: {'$eq': str(v['text'])},
            'in': lambda v: {'$in': v['in']},
            'between': lambda v: {'$gte': v['between'][0], '$lte': v['between'][1]}
        }
        for k, v in q.items():
            if '__' in k:
                vs = k.split('__')
                k = vs[0]
                v = {vs[1]: v}
            if type(v) == dict:
                nv = {}
                for vk, vv in v.items():
                    if vk.startswith('$'):
                        nv[vk] = vv
                    elif vk in wrapm:
                        nv.update(wrapm[vk](v))
                v = nv
            nq[k] = v
        return nq
