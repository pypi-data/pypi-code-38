from __future__ import print_function

import datetime
import hashlib
import logging
from abc import ABCMeta

from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model
from halo_flask.exceptions import DbIdemError
from halo_flask.logs import log_json
from halo_flask.settingsx import settingsx

settings = settingsx()

# java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8600
# java -D"java.library.path"=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8600

logger = logging.getLogger(__name__)


class AbsModel(Model):
    __metaclass__ = ABCMeta

    halo_request_id = UnicodeAttribute(null=False)

    @classmethod
    def get_pre(cls):
        """

        :return:
        """
        hash_key_name = super(AbsModel, cls)._hash_key_attribute().attr_name
        range_key_name = None
        attr = super(AbsModel, cls)._range_key_attribute()
        if attr:
            range_key_name = attr.attr_name
        logger.debug("\nhash_key_name=" + str(hash_key_name))
        logger.debug("\nrange_key_name=" + str(range_key_name))
        return hash_key_name, range_key_name

    def get_pre_val(self):
        """

        :return:
        """
        hash_key_name, range_key_name = self.get_pre()
        hash_key_val = super(AbsModel, self).__getattribute__(hash_key_name)
        range_key_val = None
        if range_key_name:
            range_key_val = super(AbsModel, self).__getattribute__(range_key_name)
        logger.debug("\nhash_key_name=" + hash_key_name + "=" + str(hash_key_val))
        if range_key_val:
            logger.debug("\nrange_key_val=" + range_key_name + "=" + str(range_key_val))
        return hash_key_val, range_key_val

    def get_idempotent_id(self, halo_request_id):  # return fixed size id of 128 bit hash value
        """

        :param halo_request_id:
        :return:
        """
        if halo_request_id is None or halo_request_id == "":
            raise DbIdemError("empty request id")
        hash_key_val, range_key_val = self.get_pre_val()
        request_id = halo_request_id + "-" + str(hash_key_val)
        if range_key_val:
            request_id = request_id + "-" + str(range_key_val)
        idempotent_id = hashlib.md5(halo_request_id.encode() + request_id.encode()).hexdigest()
        return idempotent_id


    def save(self, halo_request_id, condition=None, conditional_operator=None, **expected_values):
        """

        :param halo_request_id:
        :param condition:
        :param conditional_operator:
        :param expected_values:
        :return:
        """
        if condition is None:
            condition = AbsModel.halo_request_id.does_not_exist()
        else:
            condition = condition & (AbsModel.halo_request_id.does_not_exist())
        self.halo_request_id = self.get_idempotent_id(halo_request_id)
        return super(AbsModel, self).save(condition, conditional_operator, **expected_values)

    def update(self, halo_request_id, attributes=None, actions=None, condition=None, conditional_operator=None,
               **expected_values):
        """

        :param halo_request_id:
        :param attributes:
        :param actions:
        :param condition:
        :param conditional_operator:
        :param expected_values:
        :return:
        """
        if condition is None:
            condition = AbsModel.halo_request_id.does_not_exist()
        else:
            condition = condition & (AbsModel.halo_request_id.does_not_exist())
        self.halo_request_id = self.get_idempotent_id(halo_request_id)
        return super(AbsModel, self).update(attributes, actions, condition, conditional_operator, **expected_values)
