import pytest
import click
import os
import xlrd
import json

from datetime import datetime
from rado.core import logger, exceptions
from rado.utilse import gen_code_by_excel_dir, gen_code_by_excel_path 

PWD = os.getcwd()


@click.group()
def cli():
    """
    run : Execution test\n
    check : check your Excel file\n
    create: create a new project \n
    gen: generate init test code based on code template
    """
    pass


@cli.command()
@click.option("--test_case", default=f'{PWD}/test_case/',
              help="The test case you want to run")
@click.option("--detaile", default=True, help="Show the detaile")
def run(test_case, detaile):
    time = datetime.now().time().strftime('%H-%M-%S-%F')
    if not os.path.exists(f'{PWD}/Result'):
        os.mkdir(f'{PWD}/Result')
    time = datetime.now().time().strftime('%H-%M-%S')
    time = datetime.now().time().strftime('%Y-%m-%d-%H-%M-%S')
    result_file = f"{PWD}/Result/result_{time}.xml"
    allure_dir = f'{PWD}/Result/result_{time}/'
    os.mkdir(allure_dir)
    if detaile:
        pytest.main(["-vv", f"--junitxml={result_file}",
                     f'--alluredir={allure_dir}', test_case])
    else:
        pytest.main([f"--junitxml={result_file}", f'--alluredir={allure_dir}',
                     test_case])


@cli.command()
@click.option("--excel_dir", default=f'{PWD}/preparedData',
              help="the excel file dir you want to check")
def check(excel_dir):
    workBooks = []
    for f in os.listdir(excel_dir):
        if os.path.isfile(os.getcwd()+excel_dir+f) \
         and f.split('.')[1] in ['xlsx', 'xls']:
            workBook = excel_dir+f
            workBooks.append(workBook)
    for workBook in workBooks:
        if get_test_data_from_excel(workBook):
            click.echo(f'check {workBook} PASS!')


@cli.command()
@click.option("--path", default=f'{PWD}',
              help="the path you want to create a project")
@click.option("--name", default='demon',
              help="the name of  you project")
def create(path, name):
    template_path = os.path.split(os.path.realpath(__file__))[0]
    cmd = f"cp -r {template_path}/template {path}/{name}"
    click.echo(f'{cmd}')
    os.system(cmd)
    click.echo(f'The Project {name} is created in {path}!')


@cli.command()
@click.option("--data_dir", default=f'{PWD}/preparedData',
              type=click.Path(exists=True),
              help="the directory of you test data file")
@click.option("--data_path", type=click.File(),
              help="the path of you test data file")
def gen_code(data_dir, data_path):
    result_dir = f'{PWD}/test_case'
    gen_code_by_excel_dir(data_dir, result_dir)
    click.echo(f'The {data_dir} test_code created !')


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


def get_test_data_from_excel(excel_file):
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

            res_dic['requests']['json'] = load_row_data_by_json(
                row_data, i, 11, sheet.name)

            res_dic['response'] = {}
            res_dic['response']['status_code'] = int(row_data[12])

            res_dic['response']['checkpoints'] = load_row_data_by_json(
                row_data, i, 13, sheet.name)
            res_dic['response']['validators'] = load_row_data_by_json(
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


def load_row_data_by_json(row_data, row, col, sheet_name):
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


if __name__ == "__main__":
    cli()
