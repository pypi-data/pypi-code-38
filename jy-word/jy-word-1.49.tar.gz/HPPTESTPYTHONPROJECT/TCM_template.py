# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/5/28 0028
__author__ = 'huohuo'
from jy_word.File import File
import uuid
import json
my_file = File()


def get_uuid():
    uid = uuid.uuid1().hex
    return uid


templates = my_file.read('tcm_template.json')
# print d
templates1 = []
for template in templates:
    blocks = template.get('items') or []
    template['template'] = get_uuid()
    blocks2 = []
    for block in blocks:
        # print block.keys()
        bb = block.get('items') or []
        block['entry_name'] = block['title']
        del block['title']
        block['block_id'] = get_uuid()
        bb1 = []
        for item in bb:
            print item.keys(), item.get('text')
            input_items = item.get('input_items') or []
            for ii in input_items:
                # print ii.keys()
                ii['item_id'] = get_uuid()
                ii['item_name'] = ii.get('label')
                if 'field' in ii:
                    ii['field'] = ii['item_id']
                # elif ii.get('is_group'):
                #     group = ii.get('is_group')
                #     print ii
                elif 'items' in ii:
                    group = ii.get('is_group')
                    items = ii.get('items')
                    for iii in items:
                        if 'field' in ii:
                            iii['field'] = get_uuid()
                        elif group:
                            # print 'sss'
                            iii['field'] = get_uuid()
                        else:
                            print iii
                elif ii.get('is_list'):
                    data = ii.get('data')
                    ids = []
                    for datai in data:
                        ids.append(get_uuid())
                    ii['uuids'] = ids
                else:
                    print ii.keys()
                # for k in ii:
                #     if (type(ii[k])) not in ['unicode', 'str']:
                #         ii[k] = json.dumps(ii[k])
            bb1.append({'items': input_items, 'entry_name': item.get('text'), 'block_id': get_uuid()})
        blocks2.append(bb1)
    templates1.append(blocks2)


my_file.write('tcm_template1.json', templates)
import requests
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth('hpp_test', 'hpp.123456')
headers = {'Content-Type': 'application/json'}
rq = {
    'template_name': '普适版',
    'template': get_uuid(),
    'template_info': templates1[0]
}
rq = requests.request('post', 'http://192.168.105.4:8000/api/v2/detection/template/', auth=auth, headers=headers, json=rq)
# rq = requests.request('post', 'http://10.120.1.105:8000/api/v2/project/', auth=auth, headers=headers)
# rq = requests.request('post', 'http://10.6.50.248:8000/api/v2/project/', auth=auth, headers=headers)
print rq.status_code
if rq.status_code == 200:
    data = rq.json()
    if data.get('data'):
        print data.get('data').get('template')
    else:
        print data
# my_file.write('tcm_template2.json', templates1)


if __name__ == "__main__":
    pass
    

