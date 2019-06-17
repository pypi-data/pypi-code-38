import pytest
import click
import os

from datetime import datetime
from rado.core import logger, exceptions
from rado.utilse import (gen_code_by_excel_dir,
                         gen_code_by_excel_path,
                         get_test_data_from_excel_check)

PWD = os.getcwd()


@click.group()
def cli():
    """
    Rado. \n
    The interface test and interface performance automation test framework
    based on pytest + requests + excel/json/yaml + locust + allure.
    """
    pass


@cli.command()
@click.option("--test_case", default=f'{PWD}/test_case/',
              help="The test case you want to run")
@click.option("--detaile", default=True, help="Show the detaile")
def run(test_case, detaile):
    """
    Execute test cases.
    """
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
    """
    Check your testcase file(excel).
    """
    workBooks = []
    for f in os.listdir(excel_dir):
        if os.path.isfile(os.getcwd()+excel_dir+f) \
         and f.split('.')[1] in ['xlsx', 'xls']:
            workBook = excel_dir+f
            workBooks.append(workBook)
    for workBook in workBooks:
        if get_test_data_from_excel_check(workBook):
            click.echo(f'check {workBook} PASS!')


@cli.command()
@click.option("--path", default=f'{PWD}',
              help="the path you want to create a project")
@click.option("--name", default='demon',
              help="the name of  you project")
def create(path, name):
    """
    Create a new project.
    """
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
def gen(data_dir, data_path):
    """
    Generate init test code based on code template
    """
    result_dir = f'{PWD}/test_case'
    gen_code_by_excel_dir(data_dir, result_dir)
    click.echo(f'The {data_dir} test_code created !')


if __name__ == "__main__":
    cli()
