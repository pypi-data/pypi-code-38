import os
import shutil
from json import loads

from pyecharts import options as opts
from pyecharts.charts import Parallel 

# import matplotlib.pyplot as plt
import pandas as pd
# import numpy as np

# from pathlib import Path

from pyecharts.options import InitOpts

init_100 = InitOpts(
    width = "1600px",
    height = "900px",
#     chart_id = '100%',

    page_title = "Parallel Coordinates Plot",

    js_host = "js/",
)


# def load_json_to_plot(json_name):
#     f = open('experiment(2).json').read()
#     f = open(json_name).read()
#     j = loads(f)

def load_json_to_plot():
    # print(saved_path)
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

    # print(optimize_mode)
    # j['experimentParameters']['params']['searchSpace']

    # print(eval(j['experimentParameters']['params']['searchSpace']))
    # print(type(eval(j['experimentParameters']['params']['searchSpace'])))
    searchSpace = eval(j['experimentParameters']['params']['searchSpace'])
    name_list = list(searchSpace.keys())
    # print(name_list)
    # print(name_list[0])
    # print(j['experimentParameters']['params']['searchSpace'][name_list[0]]['_type'])
    # print(searchSpace[str(name_list[0])])

    # only support uniform / choice / randint
    ss_types = [searchSpace[n]['_type'] for n in name_list]

    search_space_list = list()

    for i in range(len(name_list)):
        vv = list(list(searchSpace.values())[i]['_value'])
        if not type(vv[0]) == 'str':
            for i, v in enumerate(vv):
                vv[i] = str(v)
        search_space_list.append(vv)

    # print()
    # print(search_space_list)
    # print()
    # print(j['trialMessage'])
    trialMessage = j['trialMessage']
    # print(type(trialMessage[0]['hyperParameters'][0]))
    # print(trialMessage[0]['hyperParameters'][0])
    # print(eval(trialMessage[0]['hyperParameters'])['parameters'])

    data = [list(eval(trialMessage[ii]['hyperParameters'][0])['parameters'].values()) for ii in range(len(trialMessage))]

    # print()
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

    if data:
        df = pd.DataFrame(data)
        df['default_metric'] = data_default_metric
        df['id'] = id_list
        df['status'] = status_list
        df.columns = name_list + ['default_metric', 'id', 'status']
        df.to_csv(os.path.join(saved_path, 'res.csv'))


    p = parallel_category(data, data_default_metric, name_list, ss_types, search_space_list, optimize_mode)
    p.render(os.path.join(saved_path, 'parallel_category.html'))
    if not os.path.exists(os.path.join(saved_path, 'js')):
        os.mkdir(os.path.join(saved_path, 'js'))
    # shutil.copy('js/echarts.min.js', os.path.join(saved_path,'js/echarts.min.js'))
    # print(js_path)
    if not os.path.exists(os.path.join(saved_path,'js/echarts.min.js')):
        js_path = os.path.join(os.path.dirname(__file__), 'echarts.min.js')
        shutil.copy(js_path, os.path.join(saved_path,'js/echarts.min.js'))

# def load_json_to_plot(json_name):
#     # f = open('experiment(2).json').read()
#     f = open(json_name).read()
#     j = loads(f)


#     optimize_mode = None
#     if j['experimentParameters']['params']['tuner']['builtinTunerName'] == 'Random':
#         optimize_mode = 'maximize'
#     else:
#         optimize_mode = j['experimentParameters']['params']['tuner']['classArgs']['optimize_mode']

#     # print(optimize_mode)
#     # j['experimentParameters']['params']['searchSpace']

#     # print(eval(j['experimentParameters']['params']['searchSpace']))
#     # print(type(eval(j['experimentParameters']['params']['searchSpace'])))
#     searchSpace = j['experimentParameters']['params']['searchSpace']
#     name_list = list(searchSpace.keys())
#     # print(name_list)
#     # print(name_list[0])
#     # print(j['experimentParameters']['params']['searchSpace'][name_list[0]]['_type'])
#     # print(searchSpace[str(name_list[0])])

#     # only support uniform / choice / randint
#     ss_types = [searchSpace[n]['_type'] for n in name_list]

#     search_space_list = list()

#     for i in range(len(name_list)):
#         vv = list(list(searchSpace.values())[i]['_value'])
#         if not type(vv[0]) == 'str':
#             for i, v in enumerate(vv):
#                 vv[i] = str(v)
#         search_space_list.append(vv)

#     # print()
#     # print(search_space_list)
#     # print()
#     # print(j['trialMessage'])
#     trialMessage = j['trialMessage']
#     # print(trialMessage)

#     data = [list(trialMessage[ii]['hyperParameters']['parameters'].values()) for ii in range(len(trialMessage))]

#     # print(data)
#     # print()
#     data_default_metric = list() 
#     for ii in range(len(data)):
#         if trialMessage[ii]['status'] == 'SUCCEEDED':
#             data_default_metric.append(trialMessage[ii]['finalMetricData'][0]['data'])
#         else:
#             data_default_metric.append('-')
#     # print(data_default_metric)

#     # if data:
#     df = pd.DataFrame(data)
#     df['default_metric'] = data_default_metric
#     df.columns = name_list + ['default_metric']
#     df.to_csv('res.csv')


#     p = parallel_category(data, data_default_metric, name_list, ss_types, search_space_list, optimize_mode)
#     p.render()




def parallel_category(data, data_default_metric, name_list, ss_types, search_space_list, optimize_mode):

    types = list()
    for i, v in enumerate(ss_types):
        if v == 'choice':
            types.append('category')
        else:
            types.append('value')
    if data:
        for i, v in enumerate(data[0]):
            if types[i] == 'category' and not type(v) == 'str':
                for r, vv in enumerate(data):
                    # print(data[r][i])
                    data[r][i] = str(vv[i])
                    # print(data[r][i])

    data_dict = dict((k, v) for k, v in zip(data_default_metric, data))

    data_top_20 = list()
    others = list()
    if optimize_mode == 'maximize':
        top_20_index = dict((v, 0) for v in sorted(list(data_dict.keys()))[::-1][:max(int(len(data)*0.2), 1)] if not v =='-')
    else:
        top_20_index = dict((v, 0) for v in sorted(list(data_dict.keys()))[:max(int(len(data)*0.2), 1)] if not v =='-')

    for k, v in data_dict.items():
        if k in top_20_index:
            data_top_20.append(v)
        elif not k == '-':
            # print(k, v)
            others.append(v)

    # print()
    # print(data_top_20)
    # print()
    # print(others)
    schema = list()


    for i, n in enumerate(name_list):
        if types[i] == 'category':
            schema.append(opts.ParallelAxisOpts(dim=i, name=n, type_=types[i], data=search_space_list[i]))
            # print(i, search_space_list[i])
        elif len(search_space_list[i]) == 1:
            schema.append(opts.ParallelAxisOpts(dim=i, name=n, type_=types[i], min_=0, max_=search_space_list[i][0]))
        else:
            schema.append(opts.ParallelAxisOpts(dim=i, name=n, type_=types[i], min_=search_space_list[i][0], max_=search_space_list[i][1]))

    # [ opts.ParallelAxisOpts(dim=i, name=v[0], type_=v[1], data=list(v[2])) for i, v in enumerate(zip(name_list, types, search_space_list))]

    c = (
        Parallel(init_opts=init_100)
        .add_schema(
            
            schema
        )
        .add("top 20%", data_top_20)
        .add("others", others)
        .set_global_opts(title_opts=opts.TitleOpts(title="Parallel Coordinates Plot"))
    )
    return c

# p = parallel_category(data, data_default_metric, name_list, ss_types, search_space_list)
# p.render()

if __name__ == '__main__':
    # load_json_to_plot('experiment(2).json')

# path
    
    # f1 = open('nni_experiment').read()
    # f2 = open('nni_trial').read()
    # experimentParameters = loads(f1)
    # trialMessage = loads(f2)
    # j = {'experimentParameters': experimentParameters, 'trialMessage':trialMessage}
    os.environ['SAVEDPATH'] = '/home/shifangjun/nni_plot/hi'
    load_json_to_plot()
    # load_json_to_plot(j)
