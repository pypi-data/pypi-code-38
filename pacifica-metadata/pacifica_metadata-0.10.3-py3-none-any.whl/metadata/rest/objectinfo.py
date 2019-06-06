#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Core interface for the uploader metadata objects to interface with CherryPy."""
import cherrypy
from cherrypy import tools
import pacifica.metadata.orm.all_objects as orm_obj_module
from pacifica.metadata.orm.base import db_connection_decorator


# pylint: disable=too-few-public-methods
class ObjectInfoAPI(object):
    """ObjectInfoAPI API."""

    lower_obj = {
        obj.__module__.split('.').pop().lower(): obj.__name__ for obj in orm_obj_module.ORM_OBJECTS
    }
    exposed = True

    @classmethod
    def get_class_object_from_name(cls, object_class_name):
        """Return a metadata model class for a given class name string."""
        if object_class_name is not None:
            try:
                myclass = getattr(
                    orm_obj_module,
                    cls.lower_obj[object_class_name.lower()]
                )
            except KeyError:
                myclass = None
        else:
            myclass = None

        return myclass

    # CherryPy requires these named methods.
    # pylint: disable=invalid-name, protected-access
    @classmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(cls, object_class_name=None, operation=None, **where_clause):
        """
        Implement the GET HTTP method.

        Returns the json object based on fields passed into kwargs.
        """
        if object_class_name == 'list':
            return {'available_objects': cls.lower_obj}

        myclass = ObjectInfoAPI.get_class_object_from_name(object_class_name)
        if operation == 'hashlist':
            available_hash_list, hash_dict = myclass.available_hash_list()
            js_object = {
                'hash_list': available_hash_list,
                'hash_lookup': hash_dict
            }
        else:  # operation is None or operation == 'overview':
            if myclass is None:
                if object_class_name is not None:
                    message = "'{0}' is not a valid class object name".format(object_class_name)
                    raise cherrypy.HTTPError(404, message)
                return list(cls.lower_obj.keys())
            else:
                js_object = myclass.get_object_info(where_clause)
        return js_object
