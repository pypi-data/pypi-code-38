#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import base64
import datetime
import hmac
import json
import logging
import time
from hashlib import sha1

import requests
from munch import Munch

from api.model.Page import Page
from factdatasource.dao.FactDatasource import customer_dao_context_holder as costomer_context
from factdatasource.execptions import FDExecuteException, NotSupportedFDException
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext
from libs.utils import JSONEncoder

log = logging.getLogger('Ficus')


class SobeyHiveFactDatasourceContext(AbstractFactDatasourceContext):

    DEFAULT_CONTENT_TYPE = "application/json;charset=utf-8"
    # 数据对象字段深度，避免相互引用造成死循环
    FIELD_DEPT = 10

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """
        return 0

    def is_empty(self):
        """
        返回是否存在数据
        :return: boolean
        """
        return False

    def collect(self, size: int):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """
        return None

    def query(self, query: str, parameters: dict = None):
        """
        通过使用hive的全文检索来查询数据
        不支持 pageNum、pageSize、needCount参数
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """
        if not query:
            return None

        # 参数占位符处理
        query = self._fd_placeholder_replace(query, parameters)
        source_name = self.fd().get_source_name()
        try:
            json_query = json.loads(query)
        except Exception as e:
            error = f'事实库{source_name}执行query操作SQL错误：{query}, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)

        url = "http://"+self.fd().connection+"/sobeyhive-bp/v1/search?isCountPrivilege=false"

        # 构建http头信息, 签名5分钟失效,因此,可以只生成一次
        headers = self._build_http_headers('POST')

        try:
            r = requests.post(url, json=json_query, headers=headers)
            if r.ok and len(r.content) > 0:
                resource_search_result = Munch(r.json())
                if resource_search_result.queryResult:
                    query_result = resource_search_result.queryResult
                    page = Page(query_result.get('currentPage'), query_result.get('pageSize'), True, False)
                    page.set_result(query_result.get('result'), query_result.get('totalCount'))
                    return page
        except Exception as e:
            source_name = self.fd().get_source_name()
            error = f'事实库{source_name}执行query操作SQL：{json_query} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        return None

    def inserts(self, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """
        if not result_list:
            return
        if not isinstance(result_list, list):
            result_list = [result_list]

        url = f'http://{self.fd().connection}/sobeyhive-bp/v1/entity'

        # 构建http头信息, 签名5分钟失效,因此,可以只生成一次
        headers = self._build_http_headers('PATCH')

        i = 0
        while i < len(result_list):
            try:
                result = result_list[i]
                i += 1

                if isinstance(result, str):
                    result_str = result
                    result = json.loads(result)
                else:
                    result_str = json.dumps(result, cls=JSONEncoder)

                r = requests.patch(url, data=result_str, headers=headers)

                # 这里会返回结果，不会抛出异常
                if r.status_code == 500:
                    response = Munch(r.json())
                    code = response.code
                    # 入库验证不通过, B0005 新增验证不通过，B0192 部分更新验证不通过
                    if 'B0005' == code or 'B0192' == code:
                        if self._create_entity_obj_by_dict(result):
                            # 创建业务对象后重试一次,只有创建成功才重试，否则会导致死循环
                            i -= 1
                            continue
                elif not r.ok:
                    raise FDExecuteException(f"插入数据错误：{str(r.json())}")
            except Exception as e:
                source_name = self.fd().get_source_name()
                error = f'事实库{source_name}执行inserts操作发生异常, {str(e)}'
                log.error(error)
                raise FDExecuteException(error)

    def updates(self, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        self.inserts(result_list)

    def inserts_or_updates(self, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        self.inserts(result_list)

    def _single_thread_inserts(self, table: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """
        raise NotSupportedFDException('sobeyhive不支持该操作')

    def _single_thread_updates(self, table: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        raise NotSupportedFDException('sobeyhive不支持该操作')

    def _single_thread_inserts_or_updates(self, table: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        raise NotSupportedFDException('sobeyhive不支持该操作')

    def delete_all(self):
        """
        清空数据
        :return:
        """
        raise NotSupportedFDException('sobeyhive不支持该操作')

    def delete(self, query: str):
        """
        根据删除语句删除数据,query是完整的删除语句
        :return:
        """
        raise NotSupportedFDException('sobeyhive不支持该操作')

    def _build_http_headers(self, request_method: str) -> dict:
        """
        构造请求头
        :param request_method:
        :return:
        """
        date_string = time.strftime("%a, %d %b %Y %H:%M:%S %z")
        signature = self._build_signature(request_method, date_string, 'SobeyHive')

        headers = {
            "Content-Type": self.DEFAULT_CONTENT_TYPE,
            # 这里使用credentials来设置站点有可能从ficus的A站点向hive的B站点中入，所以不能直接使用fd的site
            "sobeyhive-http-site": self.fd().credentials,
            "sobeyhive-http-system": "SobeyHive",
            "sobeyhive-http-system_authorization": f'SobeyHive SobeyHive:{signature}',
            "sobeyhive-http-date": date_string,
            "current-user-code": "admin"
        }
        return headers

    def _build_signature(self, request_method: str, date_string: str, s3secretkey: str):
        to_signature = f'{request_method}\n\n{self.DEFAULT_CONTENT_TYPE}\n{date_string}'
        hmac_code = hmac.new(s3secretkey.encode(), to_signature.encode(), sha1).digest()
        return base64.b64encode(hmac_code).decode()

    def _create_entity_obj_by_dict(self, entity: dict) -> bool:
        if 'entityData' not in entity:
            raise FDExecuteException(f'未设置entityData值，无法创建业务对象。{entity}')

        type_name = self.fd().target
        entity_data: dict = entity.get('entityData')

        # 1. 创建数据对象
        resource_type_id = self._create_resource_obj(type_name)
        if resource_type_id <= 0:
            return False

        # 2. 创建数据对象的字段
        self._create_resource_field_by_dict(resource_type_id, entity_data)

        # 3. 创建业务对象
        self._create_entity_obj(type_name, resource_type_id)

        return True

    def _create_resource_obj(self, type_name):
        """
        创建数据对象
        :param type_name:
        :return: success: id  fail: -1
        """
        headers = self._build_http_headers('POST')
        url = f'http://{self.fd().connection}/sobeyhive-bp/v1/resourceobj'

        # 构建请求参数
        request_params = {
            'resourceType': {
                'typeName': type_name
            }
        }

        r = requests.post(url, json=request_params, headers=headers)
        if r.ok and len(r.content) > 0:
            response_obj = r.json()
            if 'id' in response_obj:
                return int(response_obj.get('id'))

        return -1

    def _create_resource_field_by_dict(self, resource_type_id: int, entity_data: dict):
        """
        创建数据对象的字段
        :param resource_type_id:
        :param entity_data:
        :return:
        """
        if resource_type_id <= 0 or not entity_data:
            return

        for key, value in entity_data.items():
            field_name = str(key)

            # 跳过hive的内置字段
            if field_name.endswith('_'):
                continue
            if value is None:
                continue

            data_type = self._class2type(value)

            meta_model_field = dict()
            meta_model_field['fieldName'] = field_name

            if isinstance(value, dict):
                sub_resource_type_id = self._create_resource_obj(field_name)
                if resource_type_id <= 0:
                    continue

                self._create_resource_field_by_dict(sub_resource_type_id, value)
                meta_model_field['refModel'] = field_name
                data_type = 'object'
            elif isinstance(value, list):
                meta_model_field['multiple'] = True
                obj = value[0]
                if obj is None:
                    # TODO 这里就直接返回了吗？
                    continue

                if isinstance(obj, dict):
                    if obj is None:
                        return
                    sub_resource_type_id = self._create_resource_obj(field_name)
                    if resource_type_id <= 0:
                        continue

                    self._create_resource_field_by_dict(sub_resource_type_id, value)
                    meta_model_field['refModel'] = field_name
                    data_type = 'object'
                else:
                    data_type = self._class2type(obj)

            self._create_resource_field(resource_type_id, data_type, meta_model_field)

    def _class2type(self, obj) -> str:
        if isinstance(obj, bool):
            return 'boolean'
        elif isinstance(obj, bytes) or isinstance(obj, str):
            return 'string'
        elif isinstance(obj, float):
            return 'double'
        elif isinstance(obj, int):
            return 'long'
        elif isinstance(obj, datetime.date):
            return 'date'
        else:
            return 'string'

    def _create_entity_obj(self, type_name, resource_type_id):
        """
        创建业务对象
        :param type_name:
        :param resource_type_id:
        :return:
        """
        headers = self._build_http_headers('POST')
        url = f'http://{self.fd().connection}/sobeyhive-bp/v1/entityobj'

        # 构建请求参数
        request_params = {
            'entityTypeVO': {
                'typeName': type_name
            },
            'entityTypeAndResourceTypes': [{'mainData': 1, 'resourceTypeId': resource_type_id}]
        }

        try:
            r = requests.post(url, json=request_params, headers=headers)
            if not r.ok:
                raise FDExecuteException(f'数据源{self.fd().get_source_name()}创建业务对象失败,{str(r.content)}')
        except Exception as e:
            raise FDExecuteException(f'数据源{self.fd().get_source_name()}创建业务对象失败,{str(e)}')

    def _create_resource_field(self, resource_type_id, data_type, meta_model_field: dict):
        """
        创建数据对象字段
        :param resource_type_id:
        :param data_type:
        :param meta_model_field:
        :return:
        """
        headers = self._build_http_headers('POST')
        url = f'http://{self.fd().connection}/sobeyhive-bp/v1/resourceobj/field'
        # 构建请求参数
        request_params = {
            'resourceTypeId': resource_type_id,
            'fieldName': meta_model_field.get('fieldName')
        }

        try:
            if data_type:
                request_params['dataType'] = data_type
            if 'alias' in meta_model_field:
                request_params['alias'] = meta_model_field['alias']
            if 'description' in meta_model_field:
                request_params['description'] = meta_model_field['description']
            if 'minLength' in meta_model_field:
                request_params['minLen'] = meta_model_field['minLength']
            if 'maxLength' in meta_model_field:
                request_params['maxLen'] = meta_model_field['maxLength']
            if 'nullable' in meta_model_field:
                nullable = bool(meta_model_field['nullable'])
                must_input = 0 if nullable else 1
                request_params['mustInput'] = must_input
            if 'multiple' in meta_model_field:
                multiple = bool(meta_model_field['multiple'])
                is_array = 1 if multiple else 0
                request_params['isArray'] = is_array
            if 'refModel' in meta_model_field:
                request_params['refResourceTypeName'] = meta_model_field['refModel']

            r = requests.post(url, json=request_params, headers=headers)
            if not r.ok:
                raise FDExecuteException(f'数据源{self.fd().get_source_name()}创建数据对象字段失败,对象字段值：{str(meta_model_field)},{str(e)}')
        except Exception as e:
            raise FDExecuteException(f'数据源{self.fd().get_source_name()}创建数据对象字段失败,对象字段值：{str(meta_model_field)},{str(e)}')








