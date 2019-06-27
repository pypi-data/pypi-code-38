##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017-18  SensiML Corporation.                                   #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################


from sensiml.datamanager.pipelineseed import PipelineSeed


class empty():
    pass


param_tabs = ',\n'+' '*4*8


def function_help(func):
    filter_list = ['group_columns', 'label_column', 'ignore_columns', 'passthrough_columns',
                   'classifiers', 'validation_methods']
    params = []
    for item in func.input_contract:
        key = item.get('name')
        value = item.get('default', None)
        key_type = item.get('type', None)
        options = item.get('options', None)
        if value is not None:
            if key_type == 'str':
                params.append('"{}": "{}"'.format(key, value))
            else:
                params.append('"{}": {}'.format(key, value))

            if options is not None and key not in filter_list:
                values = map(lambda x: x['name'], options)
                params[-1] += ', #options: ' + '<{}>'.format(
                    '/'.join(values))
        elif options and key not in filter_list:
            values = map(lambda x: x['name'], options)
            params.append('"{}": <{}>'.format(key, '/'.join(values)))
        elif key_type in ['int', 'float', 'str', 'numeric', 'list', 'dict'] and key not in filter_list:
            params.append('"{}": {}'.format(key, '<{}>'.format(key_type)))

    params.append('')

    if isinstance(func, PipelineSeed):
        return """results, summary = dsk.pipeline.auto({{'seed': '{}', 'params':{{{}}}}})""".format(func.name, param_tabs.join(params))

    if func.type == 'Feature Generator':
        return """dsk.pipeline.add_feature_generator([{{'name':'{}', 'params':{{{}}}}}])""".format(func.name, param_tabs.join(params))

    if func.type == 'Feature Selector':
        return """dsk.pipeline.add_feature_selector([{{'name':'{}', 'params':{{{}}}}}], params={{'number_of_features':(int)}})""".format(
            func.name, param_tabs.join(params))

    if func.type in ['Segmenter', 'Transform', 'Sampler']:
        return """dsk.pipeline.add_transform("{}", params={{{}}})""".format(func.name, param_tabs.join(params))

    if func.type == 'Training Algorithm':
        return """dsk.pipeline.set_training_algorithm("{}", params={{{}}})""".format(func.name, param_tabs.join(params))

    if func.type == 'Validation Method':
        return """dsk.pipeline.set_validation_method("{}", params={{{}}})""".format(func.name, param_tabs.join(params))

    if func.type == 'Classifier':
        return """dsk.pipeline.set_classifier("{}", params={{{}}})""".format(func.name, param_tabs.join(params))

    return None


class hold_function():
    def __init__(self, func):
        self.func = func

    def create_function(self):
        try:
            docs = function_help(self.func)
        except:
            docs = "unable to generate this function."
        try:
            get_ipython().set_next_input(docs, replace=True)
        except:
            print(docs)

        return docs


class Snippets():
    def __init__(self, function_df, function_list, seeds):
        self._function_df = function_df
        self._function_list = function_list
        self._seeds = seeds
        self._attach_types()

    def _attach_types(self):
        type_list = self._function_df.TYPE.unique()
        for func_type in type_list:
            setattr(self, func_type.replace(' ', '_'),
                    self._attach_functions(func_type))
        setattr(self, 'Auto', self._attach_seeds())

    def _attach_functions(self, func_type):
        funcs = self._function_df[self._function_df.TYPE == func_type]
        cls = empty()
        funcs = self._function_df[self._function_df.TYPE == func_type]
        for func in funcs.NAME:
            # functions names starting with numbers not allowed, check for them here
            sfunc = func
            if sfunc[:1] in '0123456789':
                sfunc = 'FG_' + func
            setattr(cls, sfunc.replace(' ', '_').replace('-', ''),
                    hold_function(self._function_list[func]).create_function)

        return cls

    def _attach_seeds(self):
        cls = empty()
        for seed in self._seeds:
            setattr(cls, seed.name.replace(' ', '_').replace('-', ''),
                    hold_function(seed).create_function)

        return cls


def get_group_columns(steps):
    for step in steps:
        inputs = step.get('inputs', None)
        if inputs:
            return inputs.get('group_columns')


def get_label_column(steps):
    for step in steps:
        if step.get('type', None) == 'tvo':
            return step.get('label_column', None)


def pipeline_function_help(function_list, step, filter_list=['group_columns', 'label_column', 'ignore_columns', 'passthrough_columns', "classifiers", 'validation_methods',  'input_data', 'return_segment_index']):

    function_name = step.get('name', None)
    if function_name is None:
        function_name = step.get('function_name', None)
    if function_name is None:
        return None

    func = function_list[function_name]

    params = []
    for item in func.input_contract:
        key = item.get('name')
        if key not in filter_list:
            value = step['inputs'].get(key, None)
            if value is not None:
                if item.get('type', None) == 'str':
                    params.append('"{}":"{}"'.format(key, value))
                else:
                    params.append('"{}":{}'.format(key, value))

    if func.type == 'Feature Generator':
        return """{{'name':'{}', 'params':{{{}}}}}""".format(func.name, param_tabs.join(params))

    if func.type == 'Feature Selector':
        return """{{'name':'{}', 'params':{{{}}}}}, """.format(func.name, param_tabs.join(params))

    if func.type in ['Segmenter', 'Transform', 'Sampler']:
        return """dsk.pipeline.add_transform("{}", params={{{}}})""".format(func.name, param_tabs.join(params))

    if func.type == 'Training Algorithm':
        return """dsk.pipeline.set_training_algorithm("{}", params={{{}}})""".format(func.name, param_tabs.join(params))

    if func.type == 'Validation Method':
        return """dsk.pipeline.set_validation_method("{}", params={{{}}})""".format(func.name, param_tabs.join(params))

    if func.type == 'Classifier':
        return """dsk.pipeline.set_classifier("{}", params={{{}}})""".format(func.name, param_tabs.join(params))

    return None


def build_pipeline(function_list, steps):
    pipeline_steps = ["dsk.pipeline.reset()"]

    for step in steps:
        if step.get('type') == 'generatorset':
            feature_generators = []
            for generator in step['set']:
                feature_generators.append(
                    pipeline_function_help(function_list, generator))
            pipeline_steps.append("""dsk.pipeline.add_feature_generator([{}])""".format(
                ',\n{}'.format(' '*40).join(feature_generators)))

        elif step.get('type') == 'selectorset':
            feature_selectors = []
            for selector in step['set']:
                feature_selectors.append(
                    pipeline_function_help(function_list, selector))
            pipeline_steps.append("dsk.pipeline.add_feature_selector([{}])""".format(
                ',\n{}'.format(' '*40).join(feature_selectors)))

        elif step.get('type') == 'tvo':
            for key in ['classifiers', 'validation_methods', 'optimizers']:
                pipeline_steps.append(pipeline_function_help(
                    function_list, step[key][0]))

            pipeline_steps.append("dsk.pipeline.set_tvo({{'validation_seed':{}}})".format(
                step.get('validation_seed', 0)))

        elif step.get('type', None) == 'featurefile':
            pipeline_steps.append("""dsk.pipeline.set_input_data("{}", data_columns={}, \n{}group_columns={},\n{}label_column="{}")""".
                                  format(step.get('name', None), step.get('data_columns', None), ' '*40, get_group_columns(steps), ' '*40, get_label_column(steps)))

        elif step.get('type', None) == 'query':
            pipeline_steps.append("""dsk.pipeline.set_input_query("{}")""".
                                  format(step.get('name', None)))
        else:
            pipeline_steps.append(pipeline_function_help(function_list, step))

    return pipeline_steps


def generate_pipeline(function_list, steps, replace=True):
    pipeline_steps = build_pipeline(function_list, steps)

    if replace:
        pipeline_string = '\n\n'.join([x for x in pipeline_steps if x])
        get_ipython().set_next_input(pipeline_string, replace=True)

    return pipeline_steps
