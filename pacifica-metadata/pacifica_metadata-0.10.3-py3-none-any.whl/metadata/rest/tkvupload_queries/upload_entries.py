#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy TKV Metadata object class."""
from cherrypy import tools, request
from pacifica.metadata.orm import TransactionKeyValue, Keys, Values
from pacifica.metadata.orm.utils import unicode_type
from pacifica.metadata.orm.base import DB


# pylint: disable=too-few-public-methods
class UploadEntries(object):
    """Uploads new transaction key/value pairs to Pacifica."""

    upload_keys_cache = {}
    exposed = True

    @staticmethod
    def add_or_update(item_list):
        """Add or update transacton key value items."""
        key_cache = {}
        value_cache = {}
        for transaction in item_list:
            item = item_list[transaction]
            key_diff = list(set(item.keys()) - set(key_cache.keys()))
            if key_diff:
                key_cache = UploadEntries._update_id_list(
                    item.keys(), Keys, 'key')
            value_diff = list(set(item.values()) - set(value_cache.keys()))
            if value_diff:
                value_cache = UploadEntries._update_id_list(
                    item.values(), Values, 'value')
            UploadEntries._insert_kv_mappings(
                item, key_cache, value_cache, transaction)
        return {'status': 'success'}

    # we should have a complete set of key ids now
    @staticmethod
    def _get_id_list(names_list, model_obj, field_name):
        field_attr = getattr(model_obj, field_name)
        id_attr = getattr(model_obj, 'id')
        query = (model_obj
                 .select()
                 .distinct()
                 .where(field_attr << list(names_list))
                 .order_by(id_attr)).dicts()
        return {o[field_name]: o['id'] for o in query}

    @staticmethod
    def _update_id_list(names_list, model_obj, field_name):
        names_list = list(map(unicode_type, list(names_list)))
        local_list = UploadEntries._get_id_list(
            names_list, model_obj, field_name)
        diff = list(set(list(names_list)) - set(local_list.keys()))
        insert_list = [{field_name: str(o)} for o in diff]
        if insert_list:
            with DB.atomic():
                model_obj.insert_many(insert_list).execute()

        return UploadEntries._get_id_list(names_list, model_obj, field_name)

    @staticmethod
    def _insert_kv_mappings(item, key_cache, value_cache, transaction_id):
        insert_list = []
        for field in item:
            value = str(item[str(field)])
            key_id = key_cache[str(field)]
            value_id = value_cache[value]
            insert_list.append({
                'key': key_id,
                'value': value_id,
                'transaction': transaction_id
            })
        insert_count = 0
        if insert_list:
            with DB.atomic():
                for insert_item in insert_list:
                    TransactionKeyValue.get_or_create(**insert_item)
                    insert_count += 1
        return insert_count

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_in()
    @tools.json_out()
    def POST():
        """Return file details for the list of file id's."""
        items = request.json
        return UploadEntries.add_or_update(items)
