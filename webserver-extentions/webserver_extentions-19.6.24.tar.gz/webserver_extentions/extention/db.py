#!/usr/bin/python
# coding:utf-8

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""

import os
import sys
import json
import random
import logging
import pymysql
import cx_Oracle
import pymongo
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass

params = {}


class MysqlDB():
    """
    Mainly for batch read-write encapsulation of database, reduce the load of database
    http://mysql-python.sourceforge.net/MySQLdb.html#
    """

    def __init__(self, host=None, port=3306, user="root", password="123456", db="test",
                 ssl_ca="", ssl_cert="", ssl_key="",
                 cursorclass="pymysql.cursors.SSCursor", conf=params.get("mysql")):
        self.db = conf.get("db", db)
        host = conf.get("host", host)
        port = int(conf.get("port", port))
        user = conf.get("user", user)
        password = conf.get("password", password)
        cursorclass = eval(conf.get("cursorclass", cursorclass))
        ssl_ca = conf.get("ssl_ca", ssl_ca)
        ssl_cert = conf.get("ssl_cert", ssl_cert)
        ssl_key = conf.get("ssl_key", ssl_key)
        if ssl_ca:
            ssl = {"ssl": {"ca": ssl_ca, "cert": ssl_cert, "ssl_key": ssl_key}}
        else:
            ssl = None
        try:
            self.client = pymysql.connect(host=host, port=port, passwd=password, user=user,
                                          ssl=ssl,
                                          cursorclass=cursorclass)
            self.cursor = self.client.cursor()
            self.create_database()
        except Exception as e:
            raise Exception("---Connect MysqlServer Error--- [%s]" % str(e))

    def create_database(self):
        try:
            self.cursor.execute('CREATE DATABASE IF NOT EXISTS %s' % self.db)
        except Exception as e:
            self.output(str(e))
        self.client.select_db(self.db)

    def create_table(self, sql=""):
        """
        create table
        :param sql: CREATE TABLE test (id int primary key,name varchar(30))
        :return:
        """
        try:
            self.cursor.execute(sql)
        except Exception as e:
            self.output(str(e))

    def fetch(self, query=""):
        """
        fetch data by sql (select)
        :param query: fetchmany(size=20)
        :return:
        """
        try:
            return eval("self.cursor.%s" % query)
        except Exception as e:
            self.output(str(e))

    def execute(self, query="", args=None):
        """
        excute sql
        :param query:
        :param args:
        :return:
        """
        try:
            self.cursor.execute(query=query, args=args)
        except Exception as e:
            self.output(str(e))

    def commit(self):
        """commit insert sql"""
        try:
            self.client.commit()
        except Exception as e:
            self.output(str(e))

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def close(self):
        try:
            self.cursor.close()
        except Exception as e:
            pass
        try:
            self.client.close()
        except Exception as e:
            pass

    def output(self, arg):
        # print(str(arg))
        logging.exception(str(arg))


class Oracle():
    def __init__(self, host="116.62.186.185", port="1521", service_name="ORCL", user=None, password=None,
                 conf=params.get("oracle")):
        host = conf.get("host", host)
        port = conf.get("port", port)
        service_name = conf.get("ORCL", service_name)
        user = conf.get("user", user)
        password = conf.get("password", password)
        try:
            dsn_tns = cx_Oracle.makedsn(host, port, service_name=service_name)
            self.client = cx_Oracle.connect(
                user=user, password=password, dsn=dsn_tns)
            self.cursor = self.client.cursor()
        except Exception as e:
            self.output(str(e))
            raise Exception("---Connnect Error---")

    def fetch(self, query=""):
        """
        fetch data by sql (select)
        :param query: fetchmany(size=20)
        :return:
        """
        try:
            return eval("self.cursor.%s" % query)
        except Exception as e:
            self.output(str(e))

    def execute(self, query="", args=None):
        """
        excute sql
        :param query:
        :param args:
        :return:
        """
        try:
            self.cursor.execute(query=query, args=args)
        except Exception as e:
            self.output(str(e))

    def commit(self):
        """commit insert sql"""
        try:
            self.client.commit()
        except Exception as e:
            self.output(str(e))

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def close(self):
        try:
            self.cursor.close()
        except Exception as e:
            pass
        try:
            self.client.close()
        except Exception as e:
            pass

    def output(self, arg):
        # print(str(arg))
        logging.exception(str(arg))


class MongoDB():
    """
    Mainly for batch read-write encapsulation of database, reduce the load of database
    api document: http://api.mongodb.com/python/current/examples/bulk.html
    """

    def __init__(self, host=None,
                 port=None,
                 document_class=dict,
                 tz_aware=None,
                 connect=None,
                 type_registry=None,
                 db=None,
                 collection=None,
                 auth_user=None,
                 auth_password=None,
                 auth_db=None,
                 auth_method="SCRAM-SHA-1",
                 **kwargs):
        try:
            self.client = pymongo.MongoClient(host=host,
                                              port=int(port),
                                              document_class=document_class,
                                              tz_aware=tz_aware,
                                              connect=connect,
                                              type_registry=type_registry,
                                              **kwargs)
            if all([auth_db, auth_user, auth_password]):
                self.auth_db = eval("self.client.%s" % auth_db)
                self.auth_db.authenticate(
                    auth_user, auth_password, mechanism=auth_method)

            self.db = eval("self.client.%s" % db)
            self.collection = eval("self.db.%s" % collection)
        except Exception as e:
            raise Exception("---Connect Error---\
                            \n[ %s ]" % str(e))

    def write(self, data):
        """
        write data to Mongodb
        :param data: [{"a":1},{"b":2}]
        :return: None
        """
        try:
            self.collection.insert(data)
        except Exception as e:
            self.output(str(e))

    def read(self, search_method="find()"):
        """
        read data from Mongodb
        :param search_method:
            1.find()
            2.find().limit(2)
            3.find().skip(2)
            4.find({"a": 1})
            and so on...
        :return: result by search
        """
        try:
            result = eval("self.collection.%s" % search_method)
            return result
        except Exception as e:
            print(str(e))

    def update(self, before, after, **kwargs):
        try:
            self.collection.update(before, after, **kwargs)
        except Exception as e:
            self.output(str(e))

    def collection_operator(self, operation, **kwargs):
        try:
            return eval("self.collection.%s" % operation)
        except Exception as e:
            print(str(e))

    def database_operator(self, operation, **kwargs):
        try:
            return eval("self.db.%s" % operation)
        except Exception as e:
            self.output(str(e))

    def get_collection(self):
        return self.collection

    def get_database(self):
        return self.db

    def __del__(self):
        try:
            self.close()
        except Exception as e:
            pass

    def close(self):
        self.client.close()

    def output(self, arg):
        print(str(arg))


class EsDB():
    """
    Mainly for batch read-write encapsulation of database, reduce the load of database
    """

    def __init__(self, cluster=None, index_name=None, schema_mapping=None, **kwargs):
        self.index_name = index_name
        self.cluster = cluster
        self.schema_mapping = schema_mapping
        try:
            self.client = Elasticsearch(cluster, **kwargs)
            if not self.index_exist():
                self.create_index(body=schema_mapping)
            else:
                print("Current index already exists(index name = %s)" %
                      self.index_name)
        except Exception as e:
            self.output(str(e))

    def write(self, data):
        """
        data = [{
                "_index": "1234",
                "_type": "1234",
                "_id": 111,
                "_source": {
                    "1": 1
                    }
                }]
        :param data:
        :return:
        """
        try:
            helpers.bulk(self.client, actions=data)
        except Exception as e:
            self.output(str(e))

    def readByApi(self, query):
        """
        https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-body.html
        :param query:
        :return:
        """
        try:
            response = self.client.search(index=self.index_name, body=query)
            return response
        except Exception as e:
            self.output(str(e))

    def readByUri(self, query):
        """
        https://www.elastic.co/guide/en/elasticsearch/reference/current/search-uri-request.html
        :param query:
        :return:
        """
        try:
            response = requests.get(random.choice(
                self.cluster) + self.index_name + "/_search?%s" % query)
            return response.json()
        except Exception as e:
            self.output(str(e))

    def __del__(self):
        pass

    def close(self):
        pass

    def index_exist(self):
        return self.client.indices.exists(self.index_name)

    def create_index(self, body):
        self.client.indices.create(index=self.index_name, body=body)

    def delete_index(self):
        self.client.indices.delete(index=self.index_name)
        return True

    def output(self, arg):
        print(str(arg))


def test_es():
    cluster = ["http://106.12.217.41:9200/"]
    index_name = "1234"
    es = EsDB(cluster=cluster, index_name=index_name)
    data = [{
        "_index": "1234",
        "_type": "1234",
        "_id": 111,
        "_source": {
            "1": 1
        }
    }]
    # es.write(data)
    print(es.readByUri(query="q= 1:1"))
    query = {
        "query": {
            "term": {"1": 2}
        }
    }
    print(es.readByApi(query=query))


def test_mongo():
    host = "52.82.8.245"
    port = "9099"
    auth_user = "root"
    auth_password = "N2m3a6b9k7x"
    auth_db = "admin"
    db = "lijiacai_test"
    collection = "test"
    mongodb = MongoDB(host=host, port=port, auth_user=auth_user, auth_password=auth_password, auth_db=auth_db, db=db,
                      collection=collection)
    data = [{"1": "1", "2": "2"}, {"3": "3"}]
    # mongodb.write(data=data)
    # print(list(mongodb.read()))
    before = {"1": "1", "2": "2"}
    after = {"1": "31111111111"}
    mongodb.update(before, after)


def test_mysql():
    host = "52.82.8.156"
    port = 9906
    user = "root"
    password = "123456"
    db = "lijiacai_test"
    mysql = MysqlDB(host=host, port=port, user=user, password=password, db=db)
    mysql.execute(query='insert into test(phone, content) values ("123", "qqq");')
    # mysql.commit()
    mysql.execute(query="select * from test;")
    print(list(mysql.fetch(query="fetchall()")))
    mysql.close()


def test_oracle():
    host = "116.62.186.185"
    port = "1521"
    service_name = "ORCL"
    user = "devcq"
    password = "baIaGbnx9C"
    oracle = Oracle(host=host, port=port,
                    service_name=service_name, user=user, password=password)


if __name__ == '__main__':
    test_mysql()
