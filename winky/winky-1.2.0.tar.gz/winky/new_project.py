import os
import shutil
import pip
import pip._internal


class NewProject:
    __folders = ['enviroments', 'other', 'report', 'stubs', 'templates', 'tests', 'xpath']

    @staticmethod
    def create(demo = False):
        answer = input('Creating a template will remove files if there are any. [y\\n]')
        if answer.lower() != 'y':
            return 0
        # if hasattr(pip, 'main'):
        #     pip.main(['install', 'pytest'])
        #     pip.main(['install', 'allure-pytest'])
        # else:
        #     pip._internal.main(['install', 'pytest'])
        #     pip._internal.main(['install', 'allure-pytest'])

        for folder in NewProject.__folders:
            if os.path.exists(f'./{folder}'):
                shutil.rmtree(f'./{folder}')
            os.mkdir(folder)

        with open('./enviroments/env.py', 'w') as file:
            file.write(file_env)
        with open('./enviroments/server.py', 'w') as file:
            file.write(file_server)

        if not demo:
            with open('./enviroments/local.py', 'w') as file:
                file.write(file_local)
            with open('./stubs/mock.py', 'w') as file:
                file.write(file_mock)
            with open('./tests/test_positive.py', 'w') as file:
                file.write(file_test)
            with open('./conftest.py', 'w') as file:
                file.write(file_conftest)

        else:
            with open('./enviroments/local.py', 'w') as file:
                file.write(file_local_demo)
            with open('./stubs/mock_json.py', 'w') as file:
                file.write(file_mock_json_demo)
            with open('./stubs/mock_xml.py', 'w') as file:
                file.write(file_mock_xml_demo)
            with open('./tests/test_positive_json.py', 'w') as file:
                file.write(file_test_positive_json_demo)
            with open('./tests/test_positive_xml.py', 'w') as file:
                file.write(file_test_positive_xml_demo)
            with open('./templates/request_service_json.json', 'w') as file:
                file.write(file_request_service_json_demo)
            with open('./templates/request_service_xml.xml', 'w') as file:
                file.write(file_request_service_xml_demo)
            with open('./templates/response_service_json.json', 'w') as file:
                file.write(file_response_service_json_demo)
            with open('./templates/response_service_xml.xml', 'w') as file:
                file.write(file_response_service_xml_demo)
            with open('./xpath/response_service_xml.xpath', 'w') as file:
                file.write(file_response_service_xml_xpath_demo)
            with open('./xpath/request_service_xml.xpath', 'w') as file:
                file.write(file_request_service_xml_xpath_demo)
            with open('./conftest.py', 'w') as file:
                file.write(file_conftest_demo)

        print('success')


file_env = \
    '''from enviroments.local import EnvLocal
from enviroments.server import EnvServer
import os


def get_env():
    if 'TEST_ENV' not in os.environ:
        return EnvLocal
    if os.environ['TEST_ENV'] == 'server':
        return EnvServer
    else:
        raise EnvironmentError("Set enviroment vatiable 'TEST_ENV' = server")
'''

file_local = \
    '''class EnvLocal:
    base_path = '<path to the project on the local PC>'
'''

file_server = \
    '''class EnvServer:
    base_path = '<path to the project on the server>'
'''

file_mock = \
    '''import winky
from enviroments.env import get_env

env = get_env()


def logic(input: winky.HTTPMessage, output: winky.HTTPMessage):
    pass


mock = winky.HTTPStub(logic, 8080)

if __name__ == "__main__":
    mock.run()
    input()
'''

file_test = \
    '''import winky
import allure


def test_positive(env):
    with allure.step("Step name"):
        pass
'''

file_conftest = \
    '''from stubs.mock import mock
from enviroments.env import get_env
import pytest


class Config(get_env()):
    mock = mock


@pytest.fixture()
def env(request):
    def fin():
        mock.stop()

    request.addfinalizer(fin)
    return Config
'''

file_local_demo = \
    '''class EnvLocal:
    base_path = '../'

    mock_json_port = 8080
    mock_xml_port = 8090

    service_json_host = 'http://localhost'
    service_json_port = 8080

    service_xml_host = 'http://localhost'
    service_xml_port = 8090
'''

file_mock_json_demo = \
    '''import winky
from enviroments.env import get_env

env = get_env()


def logic(input: winky.HTTPMessage, output: winky.HTTPMessage):
    tmp_request = winky.TemplateJSON(input.body)
    tmp_response = winky.TemplateJSON()
    tmp_response.set_body_from_file(f'{env.base_path}templates/response_service_json.json')

    try:
        tmp_response['firstName'] = tmp_request['firstName']
        tmp_response['lastName'] = tmp_request['lastName']
        tmp_response['status']['home'] = 'OK'
        tmp_response['status']['city'] = 'OK'
    except KeyError:
        output.code = 400
        return 0

    output.code = 200
    output.headers["Content-Type"] = "application/json"
    output.body = tmp_response.body


mock_json = winky.HTTPStub(logic, env.mock_json_port)

if __name__ == "__main__":
    mock_json.run()
    input()
'''

file_mock_xml_demo = \
    '''import winky
from enviroments.env import get_env

env = get_env()


def logic(input: winky.HTTPMessage, output: winky.HTTPMessage):
    tmp_request = winky.TemplateXML(input.body)
    tmp_request.set_xpath_mask(f'{env.base_path}xpath/request_service_xml.xpath')
    tmp_response = winky.TemplateXML()
    tmp_response.set_body_from_file(f'{env.base_path}templates/response_service_xml.xml')
    tmp_response.set_xpath_mask(f'{env.base_path}xpath/response_service_xml.xpath')

    try:
        tmp_response['firstName'] = tmp_request['firstName']
        tmp_response['lastName'] = tmp_request['lastName']
        tmp_response['home'] = 'OK'
        tmp_response['city'] = 'OK'
    except KeyError:
        output.code = 400
        return 0

    output.code = 200
    output.headers["Content-Type"] = "application/xml"
    output.body = tmp_response.body


mock_xml = winky.HTTPStub(logic, env.mock_xml_port)

if __name__ == "__main__":
    mock_xml.run()
    input()
'''

file_request_service_json_demo = \
    '''{
   "firstName": "Ivan",
   "lastName": "Ivanov",
   "address": {
       "streetAddress": "Lenina",
       "city": "Moscow",
       "postalCode": "101101"
   },
   "phoneNumbers": [
       "812 123-1234",
       "916 123-4567"
   ]
}
'''

file_request_service_xml_demo = \
    '''<person>
  <firstName>Ivan</firstName>
  <lastName>Ivanov</lastName>
  <address>
    <streetAddress>Lenina</streetAddress>
    <city>Moscow</city>
    <postalCode>101101</postalCode>
  </address>
  <phoneNumbers>
    <phoneNumber>812 123-1234</phoneNumber>
    <phoneNumber>916 123-4567</phoneNumber>
  </phoneNumbers>
</person>
'''

file_response_service_json_demo = \
    '''{
   "firstName": "Ivan",
   "lastName": "Ivanov",
   "status": {
     "home": "OK",
     "city": "OK"
   }
}
'''

file_response_service_xml_demo = \
    '''<person>
  <firstName>Ivan</firstName>
  <lastName>Ivanov</lastName>
  <status>
    <home>OK</home>
    <city>OK</city>
  </status>
</person>
'''

file_test_positive_json_demo = \
    '''import winky
import allure


def test_positive_json(env):
    env.mock_json.run()

    with allure.step("Отправка запроса сервису mock_json"):
        request = winky.HTTPMessage()
        request.set_body_from_file(f'{env.base_path}templates/request_service_json.json')
        request.headers["Content-Type"] = "application/json"
        response = request.post(env.service_json_host, env.service_json_port)

    with allure.step("Валидация ответа сервиса mock_json"):
        tmp_response_json = winky.TemplateJSON()
        tmp_response_json.set_body_from_file(f'{env.base_path}templates/response_service_json.json')
        assert (response.code == 200)
        assert (response.headers["Content-Type"] == "application/json")
        assert (response.body == tmp_response_json.body)

    env.mock_json.stop()
'''

file_test_positive_xml_demo = \
    '''import winky
import allure


def test_positive_json(env):
    env.mock_xml.run()

    with allure.step("Отправка запроса сервису mock_json"):
        request = winky.HTTPMessage()
        request.set_body_from_file(f'{env.base_path}templates/request_service_xml.xml')
        request.headers["Content-Type"] = "application/xml"
        response = request.post(env.service_xml_host, env.service_xml_port)

    with allure.step("Валидация ответа сервиса mock_json"):
        tmp_response_json = winky.TemplateXML()
        tmp_response_json.set_body_from_file(f'{env.base_path}templates/response_service_xml.xml')
        assert (response.code == 200)
        assert (response.headers["Content-Type"] == "application/xml")
        assert (response.body == tmp_response_json.body)

    env.mock_xml.stop()
'''

file_request_service_xml_xpath_demo = \
    '''{
  "firstName": "/*[local-name()='person']/*[local-name()='firstName']",
  "lastName": "/*[local-name()='person']/*[local-name()='lastName']"
}
'''

file_response_service_xml_xpath_demo = \
    '''{
  "firstName": "/*[local-name()='person']/*[local-name()='firstName']",
  "lastName": "/*[local-name()='person']/*[local-name()='lastName']",
  "city": "/*[local-name()='person']/*[local-name()='status']/*[local-name()='city']",
  "home": "/*[local-name()='person']/*[local-name()='status']/*[local-name()='home']"
}
'''

file_conftest_demo = \
    '''from stubs.mock_json import mock_json
from stubs.mock_xml import mock_xml
from enviroments.env import get_env
import pytest


class Config(get_env()):
    mock_json = mock_json
    mock_xml = mock_xml


@pytest.fixture()
def env(request):
    def fin():
        mock_json.stop()
        mock_xml.stop()

    request.addfinalizer(fin)
    return Config
'''