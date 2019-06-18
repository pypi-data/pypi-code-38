#! /usr/bin/env python3

import os
import shutil

from json import loads
from re import sub

import pandas as pd

pcp_path = os.path.join(os.path.dirname(__file__), 'pcp.html')
pcp = open(pcp_path, 'r', encoding='utf-8').read()

def load_json_to_plot():
    saved_path = os.environ.get('SAVEDPATH')
    f1 = open(os.path.join(saved_path, 'nni_experiment')).read()
    f2 = open(os.path.join(saved_path, 'nni_trial')).read()
    experimentParameters = loads(f1)
    trialMessage = loads(f2)
    j = {'experimentParameters': experimentParameters, 'trialMessage':trialMessage}

    optimize_mode = None
    if j['experimentParameters']['params']['tuner']['builtinTunerName'] == 'Random':
        optimize_mode = 'maximize'
    else:
        optimize_mode = j['experimentParameters']['params']['tuner']['classArgs']['optimize_mode']

    searchSpace = eval(j['experimentParameters']['params']['searchSpace'])
    name_list = list(searchSpace.keys())

    # only support uniform / choice / randint
    ss_types = [searchSpace[n]['_type'] for n in name_list]

    search_space_list = list()

    for i in range(len(name_list)):
        vv = list(list(searchSpace.values())[i]['_value'])
        if not type(vv[0]) == 'str':
            for i, v in enumerate(vv):
                vv[i] = str(v)
        search_space_list.append(vv)

    trialMessage = j['trialMessage']

    data = [list(eval(trialMessage[ii]['hyperParameters'][0])['parameters'].values()) for ii in range(len(trialMessage))]

    id_list = list()
    status_list = list()
    data_default_metric = list() 
    for ii in range(len(data)):
        id_list.append(trialMessage[ii]['id'])
        status_list.append(trialMessage[ii]['status'])
        if trialMessage[ii]['status'] == 'SUCCEEDED':
            data_default_metric.append(trialMessage[ii]['finalMetricData'][0]['data'])
        else:
            data_default_metric.append('-')

    df = pd.DataFrame()
    table = ''
    if data:
        df = pd.DataFrame(data)
        df['default_metric'] = data_default_metric
        df['id'] = id_list
        df['status'] = status_list
        df.columns = name_list + ['default_metric', 'id', 'status']
        order = ['id', 'status', 'default_metric'] + name_list
        df = df[order]
        if optimize_mode == 'maximize':
            df.sort_values(by=['default_metric'], ascending=False, inplace=True)
        else:
            df.sort_values(by=['default_metric'], inplace=True)
        df.to_csv(os.path.join(saved_path, 'res.csv'))
        table = df.to_html(index=False)


    df = df.loc[df['default_metric']!='-',:]

    del df['id'], df['status']
    order = name_list + ['default_metric']
    df = df[order]

    df['default_metric'] = df['default_metric'].astype(float)
    p_max = df['default_metric'].max()
    p_min = df['default_metric'].min()

    parallel_axis_list = list()

    for i in range(len(name_list)):
        if ss_types[i] == 'choice':
            df[name_list[i]] = df[name_list[i]].astype(str)
            parallel_axis_list.append('{dim:'+str(i)+', name:\''+str(name_list[i])+'\', data:'+str(search_space_list[i])+', type:\'category\'}')
        elif len(search_space_list[i]) == 1:
            parallel_axis_list.append('{dim:'+str(i)+', name:\''+str(name_list[i])+'\', min:0, max:'+str(search_space_list[i][0])+', type:\'category\'}')
        else:
            parallel_axis_list.append('{dim:'+str(i)+', name:\''+str(name_list[i])+'\', min:'+str(search_space_list[i][0])+', max:'+str(search_space_list[i][1])+', type:\'value\'}')

    parallel_axis_list = sub('"', '', str(parallel_axis_list))


    html = sub('{barColorMin}', str(p_min), pcp)
    html = sub('{barColorMax}', str(p_max), html)
    html = sub('{data_list}', str(df.values.tolist()), html)
    html = sub('{parallel_axis_list}', str(parallel_axis_list), html) 
    html = sub('{table}', str(table), html)

    f = open(os.path.join(saved_path, 'parallel_category.html'), 'w', encoding='utf-8')
    f.write(html)
    f.close()
    if not os.path.exists(os.path.join(saved_path, 'js')):
        os.mkdir(os.path.join(saved_path, 'js'))
    if not os.path.exists(os.path.join(saved_path,'js/echarts.min.js')):
        js_path = os.path.join(os.path.dirname(__file__), 'echarts.min.js')
        shutil.copy(js_path, os.path.join(saved_path,'js/echarts.min.js'))


if __name__ == '__main__':
    os.environ['SAVEDPATH'] = '/home/shifangjun/nni_plot/a'
    load_json_to_plot()
