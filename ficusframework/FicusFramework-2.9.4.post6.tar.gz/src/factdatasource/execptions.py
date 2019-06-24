#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22


class FactDatasourceException(Exception):
    pass


class CustomerDaoContextNotFoundException(FactDatasourceException):
    pass


class DatasourceNotFoundException(FactDatasourceException):
    pass


class FDExecuteException(FactDatasourceException):
    pass


class NotSupportedFDException(FactDatasourceException):
    pass


class FDNotExistsException(FactDatasourceException):
    pass


class FDConfigException(FactDatasourceException):
    pass


class FDOperationException(FactDatasourceException):
    pass
