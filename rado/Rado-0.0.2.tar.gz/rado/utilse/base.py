# -*-coding:utf-8-*-

import xlrd
import json
import os

from datatest import validate, ValidationError
from jsonpath import jsonpath

from rado.core import exceptions, logger


def get_test_data_from_excel(excel_file, num_sheet):
    f = xlrd.open_workbook(excel_file)
    sheet = f.sheets()[num_sheet]
    test_datas = {
        'parameterize': [],
        'unparameterize': []
    }
    ids = {
        'parameterize': [],
        'unparameterize': []
    }
    for i in range(1, int(sheet.nrows)):

        row_data = sheet.row_values(i, start_colx=0, end_colx=19)
        res_dic = {}
        res_dic['test_case_name'] = f"{row_data[0]}({row_data[1]})"

        res_dic['requests'] = {}
        res_dic['requests']['url'] = row_data[10]
        res_dic['requests']['method'] = row_data[9]

        res_dic['requests']['json'] = load_row_data_by_json(row_data, i, 11)

        res_dic['response'] = {}
        res_dic['response']['status_code'] = int(row_data[12])

        res_dic['response']['checkpoints'] = load_row_data_by_json(row_data,
                                                                   i, 13)
        res_dic['response']['validators'] = load_row_data_by_json(row_data,
                                                                  i, 14)
        res_dic['case_id'] = str(int(row_data[8]))

        if int(row_data[15]) == 1:
            test_datas['parameterize'].append(res_dic)
            ids['parameterize'].append(res_dic['case_id'])
        elif int(row_data[15]) == 0:
            test_datas['unparameterize'].append(res_dic)
            ids['unparameterize'].append(res_dic['case_id'])
    return test_datas, ids


def load_row_data_by_json(row_data, row, col):
    ret = row_data
    if row_data[col] == '':
        ret = ''
    elif row_data[col] == 0.0:
        ret = 0
    else:
        try:
            ret = json.loads(row_data[col])
        except json.decoder.JSONDecodeError:
            logger.log_info(f'row:{row}, col:{col} can not json loads try eval.\
\n{row_data[col]}')
            try:
                ret = eval(row_data[col])
            except SyntaxError:
                logger.log_info(f'row:{row}, col:{col} can not eval loads try read direct.\
\n{row_data[col]}')
    return ret


def excel_data_check(sheet):
    col_names = ['测试用例番号', '测试用例名', 'level', '预置条件', '测试内容',
                 '预期结果', 'category', 'automated', 'caseid', 'method',
                 'url', 'data', 'status_code', 'checkpoints', 'validate',
                 'parameterize', 'result', '关联JIRA']

    assert sheet.ncols >= 18
    for col_name in sheet.row_values(0):
        try:
            assert col_name in col_names
        except: # noqa
            print(f'col_name check: {col_name}')
            logger.log_debug(f'col_name check: {col_name}')
            raise

    for col_num in [2, 8, 12]:
        cols = sheet.col_values(col_num, start_rowx=1)
        for i in range(len(cols)):
            try:
                assert cols[i] != ''
            except: # noqa
                logger.log_error(
                    f'sheet:{sheet.name}, col:{sheet.cell_value(0,col_num)},\
                    row:{i+2} should not be null!')
                # print(f'{sheet.name}.{sheet.cell_value(0,col_num)}(row:{i+1})
                # should not be null!')
                raise
    return True


def get_test_data_from_excel_check(excel_file):
    f = xlrd.open_workbook(excel_file)

    for sheet in f.sheets():
        print(f'\ntry load {sheet.name} test data ...')
        excel_data_check(sheet)
        test_datas = {
            'parameterize': [],
            'unparameterize': []
        }
        ids = {
            'parameterize': [],
            'unparameterize': []
        }
        for i in range(1, int(sheet.nrows)):

            row_data = sheet.row_values(i, start_colx=0, end_colx=19)
            res_dic = {}
            res_dic['test_case_name'] = f"{row_data[0]}({row_data[1]})"

            res_dic['requests'] = {}
            res_dic['requests']['url'] = row_data[10]
            res_dic['requests']['method'] = row_data[9]

            res_dic['requests']['json'] = load_row_data_by_json_check(
                row_data, i, 11, sheet.name)

            res_dic['response'] = {}
            res_dic['response']['status_code'] = int(row_data[12])

            res_dic['response']['checkpoints'] = load_row_data_by_json_check(
                row_data, i, 13, sheet.name)
            res_dic['response']['validators'] = load_row_data_by_json_check(
                row_data, i, 14, sheet.name)
            res_dic['case_id'] = str(int(row_data[8]))

            if int(row_data[15]) == 1:
                test_datas['parameterize'].append(res_dic)
                ids['parameterize'].append(res_dic['case_id'])
            elif int(row_data[15]) == 0:
                test_datas['unparameterize'].append(res_dic)
                ids['unparameterize'].append(res_dic['case_id'])
        print(f'finish load {sheet.name} test data!\n')
    # return test_datas, ids
    print('success!')


def load_row_data_by_json_check(row_data, row, col, sheet_name):
    ret = row_data
    if row_data[col] == '':
        ret = ''
    elif row_data[col] == 0.0:
        ret = 0
    else:
        try:
            ret = json.loads(row_data[col])
        except json.decoder.JSONDecodeError:

            # logger.log_info(f'row:{row}, col:{col} can not json loads try
            # read direct.\\n{row_data[col]}')
            try:
                ret = eval(row_data[col])
            except SyntaxError:
                print(
                    f'sheet: {sheet_name}, row: {row}, col: {col} can not \
                    load by json and eval \n{row_data[col]}')
                raise
    return ret


def resp_obj_2_resp_json(resp_obj):
    try:
        resp_content = resp_obj.json()
    except ValueError:
        resp_content = resp_obj.text

    return {
        'status_code': resp_obj.status_code,
        'headers': resp_obj.headers,
        'content': resp_content
    }


def check_data_by_validator(resp_body, checkpoints, validators):
    if validators == 0:
        check_data(resp_body, checkpoints)
    else:
        pass


def check_data_by_validator_old(resp_body, checkpoints, validators):
    if validators == '':
        assert resp_body == checkpoints
    else:
        if ("comm_ckpts", "comm_vldts") in zip(checkpoints.keys(),
                                               validators.keys()):
            comm_ckpt_vldt(resp_body, checkpoints["comm_ckpts"],
                           validators["comm_vldts"])
        if ("spl_ckpts", "spl_vldts") in zip(checkpoints.keys(),
                                             validators.keys()):
            spl_ckpt_vldt(resp_body, checkpoints["spl_ckpts"],
                          validators["spl_vldts"])


def comm_ckpt_vldt(resp_body, comm_ckpt, comm_vldt):
    for vldt in comm_vldt.keys():
        key_path, _ = trans_dict_path(comm_vldt[vldt]["path"])
        print("path:", key_path, vldt)
        resp_data = eval(f'resp_body{key_path}')
        expect_data = comm_ckpt[vldt]
        validators_list = comm_vldt[vldt]["vldt"]
        print("val:", resp_data, expect_data, validators_list)
        check_data(resp_data, expect_data, validators_list)


def spl_ckpt_vldt(resp_body, spl_ckpt, spl_vldt):

    for vldt in spl_vldt.keys():
        datas = []
        for index in range(spl_vldt[vldt]["len"]):
            for key in spl_vldt[vldt]["vldt"]:
                data = {}
                key_path, ckpt = trans_dict_path(key, index)
                # print("path:", key_path, vldt, key)
                data["resp_data"] = eval(f'resp_body{key_path}')
                data["expect_data"] = spl_ckpt[vldt][ckpt]
                data["validators_list"] = spl_vldt[vldt]["vldt"][key]
                # print("val:", data)
                datas.append(data)
                # print(datas)
        # print(datas)
        for data in datas:
            check_data(data["resp_data"], data["expect_data"],
                       data["validators_list"])


def trans_dict_path(path, index=None):
    patterns = path.split('.')
    ckpt = patterns[-1]
    ret = ''
    for pattern in patterns:
        if pattern == '_list':
            ret = ret + f"[{index}]"
        else:
            ret = ret + f"['{pattern}']"
    return ret, ckpt


def check_data(resp_body, checkpoints):
    for checkpoint in checkpoints.keys():
        resp_data = jsonpath(resp_body, f'$..{checkpoint}')
        expect_data = checkpoints[checkpoint]
        logger.log_info(f'\nresp_data: {resp_data}\n\
expect_data: {expect_data}')
        try:
            validate(resp_data, expect_data)
        except ValidationError:
            logger.log_error(f"\nresponse_data:{resp_data}\n\
expect_data: {expect_data}")
            raise


def check_data_old(resp_data, expect_data, validators):
    for validator in validators:
        print(resp_data, expect_data, validator)
        if validator == '==':
            validate(resp_data, expect_data)
        elif validator == 'in':
            validate_in(resp_data, expect_data)
        elif validator.split('_')[0] == 'len':
            assert len(resp_data) == int(validator.split('_')[1])


def validate_in(resp_data, expect_data):
    if isinstance(resp_data, dict) and isinstance(expect_data, dict):
        for key, value in resp_data.items():
            assert key, value in expect_data.items()
    elif isinstance(resp_data, list) and isinstance(expect_data, list):
        for ele in resp_data:
            assert ele in expect_data
    else:
        assert resp_data in expect_data


def gen_init_test_code(model_name, excel_file, result_path):

    if not os.path.exists(f'{result_path}/{model_name}'):
        os.mkdir(f'{result_path}/{model_name}')
        with open(f'{result_path}/{model_name}/__init__.py', 'w') as f:
            f.write('')
    else:
        if not os.path.exists(f'{result_path}/{model_name}/__init__.py'):
            with open(f'{result_path}/{model_name}/__init__.py', 'w') as f:
                f.write('')

    if not os.path.exists(f'{result_path}/__init__.py'):
        with open(f'{result_path}/__init__.py', 'w') as f:
            f.write('')

    f = xlrd.open_workbook(excel_file)
    file_ = os.path.basename(excel_file)
    for sheet, i in zip(f.sheets(), range(len(f.sheets()))):

        model_name = model_name
        class_name = f'{model_name}Class{i}'
        method_name = f'{model_name}_method_{i}'
        file_name = f'{result_path}/{model_name}/test_{model_name}Class{i}.py'

        test_case_template = f"""
# -*-coding:utf-8-*-

import pytest
import allure
import requests
import copy

from ... import TestBaseTest
from rado.utilse import get_test_data_from_excel


# sheet_name is :{sheet.name}
@allure.feature('test {model_name} {class_name}')
class Test{class_name}(TestBaseTest):
    test_datas, ids = get_test_data_from_excel(
        'preparedData/{file_}', {i})

    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    @allure.story('test {method_name}')
    @pytest.mark.parametrize("test_data", test_datas['parameterize'],
                             ids=ids['parameterize'])
    def test_{method_name}_parameterize(self, test_data, token_admin):
        self.headers['Authorization'] = token_admin
        with allure.step('make requests'):
            resp_obj = self.make_requests(test_data)

        with allure.step('check data'):
            self.diff_response(resp_obj, test_data['response'])

    @allure.story('test {method_name} no permission')
    def no_test_{method_name}_no_permission(self):
        url = f"http://{{self.ip}}:{{self.port}}/api/v1/login"
        data = {{
            "username": "test_simple",
            "password": "test@123"
        }}
        resp = requests.post(url=url, json=data)

        self.headers['Authorization'] = f"Bearer \\
            {{resp.json()['data']['token']}}"

        test_data = self.test_datas['unparameterize'][0]
        with allure.step('make requests'):
            resp_obj = self.make_requests(test_data)

        with allure.step('check data'):
            self.diff_response(resp_obj, test_data['response'])

    @allure.story('test {method_name} no token')
    def no_test_{method_name}_no_token(self):
        self.headers['Authorization'] = None

        test_data = self.test_datas['unparameterize'][1]
        with allure.step('make requests'):
            resp_obj = self.make_requests(test_data)

        with allure.step('check data'):
            self.diff_response(resp_obj, test_data['response'])

    @allure.story('test {method_name} no token')
    def no_test_{method_name}_del_deleted(self):
        self.headers['Authorization'] = token_admin
        test_data = self.test_datas['unparameterize'][0]
        test_data1 = copy.deepcopy(test_data)

        with allure.step('make requests'):
            resp_obj = self.make_requests(test_data)
            resp_obj = self.make_requests(test_data1)

        with allure.step('check data'):
            self.diff_response(resp_obj, test_data['response'])
"""

        # print(test_case_template)
        with open(file_name, 'w') as f:
            f.write(test_case_template)


def get_excel(path):
    workBooks = []
    for f in os.listdir(path):
        if os.path.isfile(f'{path}/{f}') and f.split('.')[1] in ['xlsx', 'xls']:  # noqa
            workBook = f'{path}/{f}'
            workBooks.append(workBook)
    return workBooks


def get_model_name(excel_file):
    base_name = os.path.basename(excel_file)
    return os.path.splitext(base_name)[0].split('_')[1]


def gen_code_by_excel_dir(excel_file_dir, result_dir):
    for excel_file in get_excel(excel_file_dir):

        model_name = get_model_name(excel_file)
        gen_init_test_code(model_name, excel_file, result_dir)


def gen_code_by_excel_path(excel_file, result_path):
        model_name = get_model_name(excel_file)
        gen_init_test_code(model_name, excel_file, result_path)
