import requests
import os

from datetime import datetime

from .utilse import resp_obj_2_resp_json, \
        check_data_by_validator
from .core import exceptions, logger


class BaseTest:
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }

    verify_ssl = False
    https = False

    log_file = f'./logs/rado_\
{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log_level = "DEBUG"
    logger.setup_logger(log_level, log_file)

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        print('\n{}::{}'.format(type(self).__name__, method.__name__))
        logger.log_debug(
            '\n\n{}::{}'.format(type(self).__name__, method.__name__))

    def teardown_method(self, method):
        pass

    def diff_response(self, resp_obj, response):
        resp_json = resp_obj_2_resp_json(resp_obj)

        print('resp_json: ', resp_json)
        logger.log_debug(f'resp_json:\n{resp_json}')
        print('status_code: ', resp_json['status_code'],
              response['status_code'])

        try:
            logger.log_info(
                f"\nresponse_data:{resp_json['status_code']}\n\
expect_data: {response['status_code']}")
            assert resp_json['status_code'] == response['status_code']
        except AssertionError:
            logger.log_error(
                f"\nresponse_data:{resp_json['status_code']}\n\
expect_data: {response['status_code']}")
            raise
        if response['checkpoints'] == '' and response['validators'] == '':
            pass
        elif response['checkpoints'] != '' and response['validators'] == '':
            try:
                logger.log_info(f"\nresponse_data:{resp_json['content']}\n\
expect_data:{response['checkpoints']}")
                assert resp_json['content'] == response['checkpoints']
            except AssertionError:
                logger.log_error(f"\nresponse_data:{resp_json['content']}\n\
expect_data:{response['checkpoints']}")
                raise
        else:
            check_data_by_validator(
                resp_json['content'], response['checkpoints'],
                response['validators'])

    def compose_url(self, url_str):
        if self.https:
            url = f"https://{self.ip}:{self.port}{url_str}"
        else:
            url = f"http://{self.ip}:{self.port}{url_str}"
        return url

    def make_requests(self, test_data):
        logger.log_debug(f"{test_data['test_case_name']}\n")
        try:
            req_kwargs = test_data['requests']
            url = self.compose_url(req_kwargs.pop('url'))
            method = req_kwargs.pop('method')
        except KeyError:
            raise exceptions.ParamsError("URL or METHOD missed!")

        valid_methods = ["GET", "HEAD", "POST", "PUT", "PATCH",
                         "DELETE", "OPTIONS"]

        if method.upper() not in valid_methods:
            err_msg = u"Invalid HTTP method! => {}\n".format(method)
            err_msg += "Available HTTP methods: {}".format(
                "/".join(valid_methods))
            logger.log_error(err_msg)
            raise exceptions.ParamsError(err_msg)

        logger.log_debug("{method} {url}".format(method=method, url=url))
        logger.log_debug("request kwargs(raw):{kwargs}".format(
            kwargs=req_kwargs))

        if method == 'GET':
            resp_obj = requests.request(
                url=url, method=method, verify=self.verify_ssl,
                headers=self.headers, params=req_kwargs['json'])
            print(resp_obj.url)
            logger.log_debug(f"{method} {resp_obj.url}")
        else:
            resp_obj = requests.request(
                url=url, method=method,  verify=self.verify_ssl,
                headers=self.headers, **req_kwargs)
        return resp_obj
