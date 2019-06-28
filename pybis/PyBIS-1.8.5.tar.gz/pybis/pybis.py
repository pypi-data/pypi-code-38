#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pybis.py

Work with openBIS from Python.

"""

from __future__ import print_function
import os
import random

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import time
import json
import re
from urllib.parse import urlparse, urljoin, quote
import zlib
from collections import namedtuple
from texttable import Texttable
from tabulate import tabulate

from . import data_set as pbds
from .utils import parse_jackson, check_datatype, split_identifier, format_timestamp, is_identifier, is_permid, nvl, VERBOSE
from .utils import extract_attr, extract_permid, extract_code,extract_deletion,extract_identifier,extract_nested_identifier,extract_nested_permid,extract_property_assignments,extract_role_assignments,extract_person, extract_person_details,extract_id,extract_userId
from .entity_types import EntityType
from .vocabulary import Vocabulary, VocabularyTerm
from .openbis_object import OpenBisObject 
from .definitions import get_definition_for_entity, fetch_option, get_fetchoption_for_entity, get_type_for_entity, get_method_for_entity

# import the various openBIS entities
from .things import Things
from .space import Space
from .project import Project
from .experiment import Experiment
from .sample import Sample
from .dataset import DataSet
from .person import Person
from .group import Group
from .role_assignment import RoleAssignment
from .tag import Tag
from .sample_type import SampleType
from .semantic_annotation import SemanticAnnotation
from .plugin import Plugin

from pandas import DataFrame, Series
import pandas as pd

from datetime import datetime

LOG_NONE    = 0
LOG_SEVERE  = 1
LOG_ERROR   = 2
LOG_WARNING = 3
LOG_INFO    = 4
LOG_ENTRY   = 5
LOG_PARM    = 6
LOG_DEBUG   = 7

DEBUG_LEVEL = LOG_NONE


def get_search_type_for_entity(entity, operator=None):
    """ Returns a dictionary containing the correct search criteria type
    for a given entity.

    Example::
        get_search_type_for_entity('space')
        # returns:
        {'@type': 'as.dto.space.search.SpaceSearchCriteria'}
    """
    search_criteria = {
        "space": "as.dto.space.search.SpaceSearchCriteria",
        "userId": "as.dto.person.search.UserIdSearchCriteria",
        "email": "as.dto.person.search.EmailSearchCriteria",
        "firstName": "as.dto.person.search.FirstNameSearchCriteria",
        "lastName": "as.dto.person.search.LastNameSearchCriteria",
        "project": "as.dto.project.search.ProjectSearchCriteria",
        "experiment": "as.dto.experiment.search.ExperimentSearchCriteria",
        "experiment_type": "as.dto.experiment.search.ExperimentTypeSearchCriteria",
        "sample": "as.dto.sample.search.SampleSearchCriteria",
        "sample_type": "as.dto.sample.search.SampleTypeSearchCriteria",
        "dataset": "as.dto.dataset.search.DataSetSearchCriteria",
        "dataset_type": "as.dto.dataset.search.DataSetTypeSearchCriteria",
        "external_dms": "as.dto.externaldms.search.ExternalDmsSearchCriteria",
        "material": "as.dto.material.search.MaterialSearchCriteria",
        "material_type": "as.dto.material.search.MaterialTypeSearchCriteria",
        "vocabulary_term": "as.dto.vocabulary.search.VocabularyTermSearchCriteria",
        "tag": "as.dto.tag.search.TagSearchCriteria",
        "authorizationGroup": "as.dto.authorizationgroup.search.AuthorizationGroupSearchCriteria",
        "roleAssignment": "as.dto.roleassignment.search.RoleAssignmentSearchCriteria",
        "person": "as.dto.person.search.PersonSearchCriteria",
        "code": "as.dto.common.search.CodeSearchCriteria",
        "sample_type": "as.dto.sample.search.SampleTypeSearchCriteria",
        "global": "as.dto.global.GlobalSearchObject",
        "plugin": "as.dto.plugin.search.PluginSearchCriteria",
    }

    sc = { "@type": search_criteria[entity] }
    if operator is not None:
        sc["operator"] = operator

    return sc

def get_attrs_for_entity(entity):
    """ For a given entity this method returns an iterator for all searchable
    attributes.
    """
    search_args = {
        "person": ['firstName','lastName','email','userId']
    }
    for search_arg in search_args[entity]:
        yield search_arg


def _type_for_id(ident, entity):
    ident = ident.strip()
    """Returns the data type for a given identifier/permId for use with the API call, e.g.
    {
        "identifier": "/DEFAULT/SAMPLE_NAME",
        "@type": "as.dto.sample.id.SampleIdentifier"
    }
    or
    {
        "permId": "20160817175233002-331",
        "@type": "as.dto.sample.id.SamplePermId"
    }
    """
    # Tags have strange permIds...
    if entity.lower() == 'tag':
        if '/' in ident:
            if not ident.startswith('/'):
                ident = '/'+ident
            return {
                "permId": ident,
                "@type" : "as.dto.tag.id.TagPermId"
            }
        else:
            return {
                "code": ident,
                "@type": "as.dto.tag.id.TagCode"
            }

    entities = {
        "sample"            : "Sample",
        "dataset"           : "DataSet",
        "experiment"        : "Experiment",
        "plugin"            : "Plugin",
        "space"             : "Space",
        "project"           : "Project",
        "semanticannotation": "SemanticAnnotation",
    }
    search_request = {}
    if entity.lower() in entities:
        entity_capitalize = entities[entity.lower()]
    else:
        entity_capitalize = entity.capitalize()

    if is_identifier(ident):
        # people tend to omit the / prefix of an identifier...
        if not ident.startswith('/'):
            ident = '/'+ident
        # ELN-LIMS style contains also experiment in sample identifer, i.e. /space/project/experiment/sample_code
        # we have to remove the experiment-code
        if ident.count('/') == 4:
            codes = ident.split('/')
            ident = '/'.join([codes[0], codes[1], codes[2], codes[4]])

        search_request = {
            "identifier": ident.upper(),
            "@type": "as.dto.{}.id.{}Identifier".format(entity.lower(), entity_capitalize)
        }
    else:
        search_request = {
            "permId": ident,
            "@type": "as.dto.{}.id.{}PermId".format(entity.lower(), entity_capitalize)
        }
    return search_request

def get_search_criteria(entity, **search_args):
    search_criteria = get_search_type_for_entity(entity)

    criteria = []
    for attr in get_attrs_for_entity(entity):
        if attr in search_args:
            sub_crit = get_search_type_for_entity(attr)
            sub_crit['fieldValue'] = get_field_value_search(attr, search_args[attr])
            criteria.append(sub_crit)

    search_criteria['criteria'] = criteria
    search_criteria['operator'] = "AND"

    return search_criteria

def crc32(fileName):
    """since Python3 the zlib module returns unsigned integers (2.7: signed int)
    """
    prev = 0
    for eachLine in open(fileName, "rb"):
        prev = zlib.crc32(eachLine, prev)
    # return as hex
    return "%x" % (prev & 0xFFFFFFFF)


def _tagIds_for_tags(tags=None, action='Add'):
    """creates an action item to add or remove tags. 
    Action is either 'Add', 'Remove' or 'Set'
    """
    if tags is None:
        return
    if not isinstance(tags, list):
        tags = [tags]

    items = []
    for tag in tags:
        items.append({
            "code": tag,
            "@type": "as.dto.tag.id.TagCode"
        })

    tagIds = {
        "actions": [
            {
                "items": items,
                "@type": "as.dto.common.update.ListUpdateAction{}".format(action.capitalize())
            }
        ],
        "@type": "as.dto.common.update.IdListUpdateValue"
    }
    return tagIds


def _list_update(ids=None, entity=None, action='Add'):
    """creates an action item to add, set or remove ids. 
    """
    if ids is None:
        return
    if not isinstance(ids, list):
        ids = [ids]

    items = []
    for ids in ids:
        items.append({
            "code": ids,
            "@type": "as.dto.{}.id.{}Code".format(entity.lower(), entity)
        })

    list_update = {
        "actions": [
            {
                "items": items,
                "@type": "as.dto.common.update.ListUpdateAction{}".format(action.capitalize())
            }
        ],
        "@type": "as.dto.common.update.IdListUpdateValue"
    }
    return list_update


def get_field_value_search(field, value, comparison="StringEqualToValue"):
    return {
        "value": value,
        "@type": "as.dto.common.search.{}".format(comparison)
    }

def _common_search(search_type, value, comparison="StringEqualToValue"):
    sreq = {
        "@type": search_type,
        "fieldValue": {
            "value": value,
            "@type": "as.dto.common.search.{}".format(comparison)
        }
    }
    return sreq


def _criteria_for_code(code):
    return {
        "fieldValue": {
            "value": code.upper(),
            "@type": "as.dto.common.search.StringEqualToValue"
        },
        "@type": "as.dto.common.search.CodeSearchCriteria"
    }

def _subcriteria_for_userId(userId):
    return {
          "criteria": [
            {
              "fieldName": "userId",
              "fieldType": "ATTRIBUTE",
              "fieldValue": {
                "value": userId,
                "@type": "as.dto.common.search.StringEqualToValue"
              },
              "@type": "as.dto.person.search.UserIdSearchCriteria"
            }
          ],
          "@type": "as.dto.person.search.PersonSearchCriteria",
          "operator": "AND"
        }


def _subcriteria_for_type(code, entity):
    return {
        "@type": "as.dto.{}.search.{}TypeSearchCriteria".format(entity.lower(), entity),
        "criteria": [
            {
                "@type": "as.dto.common.search.CodeSearchCriteria",
                "fieldValue": {
                    "value": code.upper(),
                    "@type": "as.dto.common.search.StringEqualToValue"
                }
            }
        ]
    }


def _subcriteria_for_status(status_value):
    status_value = status_value.upper()
    valid_status = "AVAILABLE LOCKED ARCHIVED UNARCHIVE_PENDING ARCHIVE_PENDING BACKUP_PENDING".split()
    if not status_value in valid_status:
        raise ValueError("status must be one of the following: " + ", ".join(valid_status))

    return {
        "@type": "as.dto.dataset.search.PhysicalDataSearchCriteria",
        "operator": "AND",
        "criteria": [{
            "@type":
                "as.dto.dataset.search.StatusSearchCriteria",
            "fieldName": "status",
            "fieldType": "ATTRIBUTE",
            "fieldValue": status_value
        }]
    }


def _gen_search_criteria(req):
    sreq = {}
    for key, val in req.items():
        if key == "criteria":
            items = []
            for item in req['criteria']:
                items.append(_gen_search_criteria(item))
            sreq['criteria'] = items
        elif key == "code":
            sreq["criteria"] = [_common_search(
                "as.dto.common.search.CodeSearchCriteria", val.upper()
            )]
        elif key == "identifier":
            if is_identifier(val):
                # if we have an identifier, we need to search in Space and Code separately
                si = split_identifier(val)
                sreq["criteria"] = []
                if "space" in si:
                    sreq["criteria"].append(
                        _gen_search_criteria({"space": "Space", "code": si["space"]})
                    )
                if "experiment" in si:
                    pass

                if "code" in si:
                    sreq["criteria"].append(
                        _common_search(
                            "as.dto.common.search.CodeSearchCriteria", si["code"].upper()
                        )
                    )
            elif is_permid(val):
                sreq["criteria"] = [_common_search(
                    "as.dto.common.search.PermIdSearchCriteria", val
                )]
            else:
                # we assume we just got a code
                sreq["criteria"] = [_common_search(
                    "as.dto.common.search.CodeSearchCriteria", val.upper()
                )]

        elif key == "operator":
            sreq["operator"] = val.upper()
        else:
            sreq["@type"] = "as.dto.{}.search.{}SearchCriteria".format(key, val)
    return sreq


def _subcriteria_for_tags(tags):
    if not isinstance(tags, list):
        tags = [tags]

    criterias = []
    for tag in tags:
        criterias.append({
            "fieldName": "code",
            "fieldType": "ATTRIBUTE",
            "fieldValue": {
                "value": tag,
                "@type": "as.dto.common.search.StringEqualToValue"
            },
            "@type": "as.dto.common.search.CodeSearchCriteria"
        })

    return {
        "@type": "as.dto.tag.search.TagSearchCriteria",
        "operator": "AND",
        "criteria": criterias
    }


def _subcriteria_for_is_finished(is_finished):
    return {
        "@type": "as.dto.common.search.StringPropertySearchCriteria",
        "fieldName": "FINISHED_FLAG",
        "fieldType": "PROPERTY",
        "fieldValue": {
            "value": is_finished,
            "@type": "as.dto.common.search.StringEqualToValue"
        }
    }


def _subcriteria_for_properties(prop, val):
    return {
        "@type": "as.dto.common.search.StringPropertySearchCriteria",
        "fieldName": prop.upper(),
        "fieldType": "PROPERTY",
        "fieldValue": {
            "value": val,
            "@type": "as.dto.common.search.StringEqualToValue"
        }
    }


def _subcriteria_for_permid(permids, entity, parents_or_children='', operator='AND'):
    if not isinstance(permids, list):
        permids = [permids]

    criterias = []
    for permid in permids:
        criterias.append({
            "@type": "as.dto.common.search.PermIdSearchCriteria",
            "fieldValue": {
                "value": permid,
                "@type": "as.dto.common.search.StringEqualToValue"
            },
            "fieldType": "ATTRIBUTE",
            "fieldName": "code"
        })

    criteria = {
        "criteria": criterias,
        "@type": "as.dto.{}.search.{}{}SearchCriteria".format(
            entity.lower(), entity, parents_or_children
        ),
        "operator": operator
    }
    return criteria


def _subcriteria_for_code(code, object_type):
    """ Creates the often used search criteria for code values. Returns a dictionary.

    Example::
        _subcriteria_for_code("username", "space")

	{
	    "criteria": [
		{
		    "fieldType": "ATTRIBUTE",
		    "@type": "as.dto.common.search.CodeSearchCriteria",
		    "fieldName": "code",
		    "fieldValue": {
			"@type": "as.dto.common.search.StringEqualToValue",
			"value": "USERNAME"
		    }
		}
	    ],
	    "operator": "AND",
	    "@type": "as.dto.space.search.SpaceSearchCriteria"
	}
    """
    if code is not None:
        if is_permid(code):
            fieldname = "permId"
            fieldtype = "as.dto.common.search.PermIdSearchCriteria"
        else:
            fieldname = "code"
            fieldtype = "as.dto.common.search.CodeSearchCriteria"

          
        search_criteria = get_search_type_for_entity(object_type.lower())
        search_criteria['criteria'] = [{
            "fieldName": fieldname,
            "fieldType": "ATTRIBUTE",
            "fieldValue": {
                "value": code.upper(),
                "@type": "as.dto.common.search.StringEqualToValue"
            },
            "@type": fieldtype
        }]
        
        search_criteria["operator"] = "AND"
        return search_criteria
    else:
        return get_search_type_for_entity(object_type.lower())



class Openbis:
    """Interface for communicating with openBIS. 

    Note:
        * A recent version of openBIS is required (minimum 16.05.2).
        * For creation of datasets, the dataset-uploader-api ingestion plugin must be present.

    """

    def __init__(self, url=None, verify_certificates=True, token=None,
    allow_http_but_do_not_use_this_in_production_and_only_within_safe_networks=False):
        """Initialize a new connection to an openBIS server.

        Examples:
            o = Openbis('https://openbis.example.com')
            o_test = Openbis('https://test_openbis.example.com:8443', verify_certificates=False)

        Args:
            url (str): https://openbis.example.com
            verify_certificates (bool): set to False when you use self-signed certificates
            token (str): a valid openBIS token. If not set, pybis will try to read a valid token from ~/.pybis
            allow_http_but_do_not_use_this_in_production_and_only_within_safe_networks (bool): False
        """

        if url is None:
            try:
                url = os.environ["OPENBIS_URL"]
                token = os.environ["OPENBIS_TOKEN"] if "OPENBIS_TOKEN" in os.environ else None
            except KeyError:
                raise ValueError("please provide a URL you want to connect to.")

        else:
            # url has been provided. If the environment variable OPENBIS_URL points to the same URL,
            # use the OPENBIS_TOKEN as well.
            if 'OPENBIS_URL' in os.environ:
                if url == os.environ["OPENBIS_URL"]:
                    token = os.environ["OPENBIS_TOKEN"] if "OPENBIS_TOKEN" in os.environ else None


        url_obj = urlparse(url)
        if url_obj.netloc is None or url_obj.netloc == '':
            raise ValueError("please provide the url in this format: https://openbis.host.ch:8443")
        if url_obj.hostname is None:
            raise ValueError("hostname is missing")
        if url_obj.scheme == 'http' and not allow_http_but_do_not_use_this_in_production_and_only_within_safe_networks:

            raise ValueError("always use https!")
            
        
        self.url = url_obj.geturl()
        self.port = url_obj.port
        self.hostname = url_obj.hostname
        self.as_v3 = '/openbis/openbis/rmi-application-server-v3.json'
        self.as_v1 = '/openbis/openbis/rmi-general-information-v1.json'
        self.reg_v1 = '/openbis/openbis/rmi-query-v1.json'
        self.verify_certificates = verify_certificates
        self.token = token

        self.server_information = None
        self.dataset_types = None
        self.sample_types = None
        #self.files_in_wsp = []
        self.token_path = None

        # use an existing token, if available
        if self.token is None:
            self.token = self._get_cached_token()
        elif self.is_token_valid(token):
            pass
        else:
            print("Session is no longer valid. Please log in again.")


    def __dir__(self):
        return [
            'url', 'port', 'hostname',
            'login(username, password, save_token=True)', 'logout()', 'is_session_active()', 'token', 'is_token_valid("")',
            "get_server_information()",
            "get_dataset('permId')",
            "get_datasets()",
            "get_dataset_type('type')",
            "get_dataset_types()",
            "get_datastores()",
            "gen_code(entity, prefix)",
            "get_deletions()",
            "get_experiment('permId', withAttachments=False)",
            "get_experiments()",
            "get_experiment_type('type')",
            "get_experiment_types()",
            "get_collection('permId', withAttachments=False)",
            "get_collections()",
            "get_collection_type('type')",
            "get_collection_types()",
            "get_external_data_management_system(permId)",
            "get_material_type('type')",
            "get_material_types()",
            "get_project('project')",
            "get_projects(space=None, code=None)",
            "get_sample('id')",
            "get_object('id')", # "get_sample('id')" alias
            "get_samples()",
            "get_objects()", # "get_samples()" alias
            "get_sample_type('type')",
            "get_object_type('type')", # "get_sample_type(type))" alias
            "get_sample_types()",
            "get_object_types()", # "get_sample_types()" alias
            "get_semantic_annotations()",
            "get_semantic_annotation(permId, only_data = False)",
            "get_space(code)",
            "get_spaces()",
            "get_tags()",
            "get_tag(tagId)",
            "new_tag(code, description)",
            "get_terms()",
            "get_term()",
            "get_vocabularies()",
            "get_vocabulary()",
            "new_person(userId, space)",
            "get_persons()",
            "get_person(userId)",
            "get_groups()",
            "get_group(code)",
            "get_role_assignments()",
            "get_role_assignment(techId)",
            "get_plugins()",
            "get_plugin(name)",
            "new_group(code, description, userIds)",
            'new_space(name, description)',
            'new_project(space, code, description, attachments)',
            'new_experiment(type, code, project, props={})',
            'new_collection(type, code, project, props={})',
            'new_sample(type, space, project, experiment, parents)',
            'new_object(type, space, project, experiment, parents)', # 'new_sample(type, space, project, experiment)' alias
            'new_dataset(type, parent, experiment, sample, files=[], folder, props={})',
            'new_semantic_annotation(entityType, propertyType)',
            'update_sample(sampleId, space, project, experiment, parents, children, components, properties, tagIds, attachments)',
            'update_object(sampleId, space, project, experiment, parents, children, components, properties, tagIds, attachments)', # 'update_sample(sampleId, space, project, experiment, parents, children, components, properties, tagIds, attachments)' alias
        ]

    def _repr_html_(self):
        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>attribute</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        attrs = ['url', 'port', 'hostname', 'verify_certificates', 'as_v3', 'as_v1', 'reg_v1', 'token']
        for attr in attrs:
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                attr, getattr(self, attr, '')
            )

        html += """
            </tbody>
            </table>
        """
        return html


    @property
    def spaces(self):
        return self.get_spaces()

    @property
    def projects(self):
        return self.get_projects()

    def _get_cached_token(self):
        """Read the token from the cache, and set the token ivar to it, if there, otherwise None.
        If the token is not valid anymore, delete it. 
        """
        token_path = self.gen_token_path()
        if not os.path.exists(token_path):
            return None
        try:
            with open(token_path) as f:
                token = f.read()
                if token == "":
                    return None
                if not self.is_token_valid(token):
                    os.remove(token_path)
                    return None
                else:
                    return token
        except FileNotFoundError:
            return None

    def gen_token_path(self, parent_folder=None):
        """generates a path to the token file.
        The token is usually saved in a file called
        ~/.pybis/hostname.token
        """
        if parent_folder is None:
            # save token under ~/.pybis folder
            parent_folder = os.path.join(
                os.path.expanduser("~"),
                '.pybis'
            )
        path = os.path.join(parent_folder, self.hostname + '.token')
        return path

    def save_token(self, token=None, parent_folder=None):
        """ saves the session token to the disk, usually here: ~/.pybis/hostname.token. When a new Openbis instance is created, it tries to read this saved token by default.
        """
        if token is None:
            token = self.token

        token_path = None;
        if parent_folder is None:
            token_path = self.gen_token_path()
        else:
            token_path = self.gen_token_path(parent_folder)

        # create the necessary directories, if they don't exist yet
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'w') as f:
            f.write(token)
            self.token_path = token_path

    def delete_token(self, token_path=None):
        """ deletes a stored session token.
        """
        if token_path is None:
            token_path = self.token_path
        os.remove(token_path)

    def _post_request(self, resource, request):
        """ internal method, used to handle all post requests and serializing / deserializing
        data
        """
        return self._post_request_full_url(urljoin(self.url,resource), request)

    def _post_request_full_url(self, full_url, request):
        """ internal method, used to handle all post requests and serializing / deserializing
        data
        """
        if "id" not in request:
            request["id"] = "2"
        if "jsonrpc" not in request:
            request["jsonrpc"] = "2.0"
        if request["params"][0] is None:
            raise ValueError("Your session expired, please log in again")

        if DEBUG_LEVEL >=LOG_DEBUG: print(json.dumps(request))
        resp = requests.post(
            full_url,
            json.dumps(request),
            verify=self.verify_certificates
        )

        if resp.ok:
            resp = resp.json()
            if 'error' in resp:
                if DEBUG_LEVEL >= LOG_ERROR: print(json.dumps(request))
                raise ValueError(resp['error']['message'])
            elif 'result' in resp:
                return resp['result']
            else:
                raise ValueError('request did not return either result nor error')
        else:
            raise ValueError('general error while performing post request')

    def logout(self):
        """ Log out of openBIS. After logout, the session token is no longer valid.
        """
        if self.token is None:
            return

        logout_request = {
            "method": "logout",
            "params": [self.token],
        }
        resp = self._post_request(self.as_v3, logout_request)
        self.token = None
        self.token_path = None
        return resp

    def login(self, username=None, password=None, save_token=False):
        """Log into openBIS.
        Expects a username and a password and updates the token (session-ID).
        The token is then used for every request.
        Clients may want to store the credentials object in a credentials store after successful login.
        Throw a ValueError with the error message if login failed.
        """

        if password is None:
            import getpass
            password = getpass.getpass()

        login_request = {
            "method": "login",
            "params": [username, password],
        }
        result = self._post_request(self.as_v3, login_request)
        if result is None:
            raise ValueError("login to openBIS failed")
        else:
            self.token = result

            if save_token:
                self.save_token()
            # update the OPENBIS_TOKEN environment variable, if OPENBIS_URL is identical to self.url
            if os.environ.get('OPENBIS_URL') == self.url:
                os.environ['OPENBIS_TOKEN'] = self.token
            return self.token


    def get_server_information(self):
        """ Returns a dict containing the following server information:
            api-version, archiving-configured, authentication-service, enabled-technologies, project-samples-enabled
        """
        if self.server_information is not None:
            return self.server_information

        request = {
            "method": "getServerInformation",
            "params": [self.token],
        }
        resp = self._post_request(self.as_v3, request)
        if resp is not None:
            # result is a dict of strings - use more useful types
            keys_boolean = ['archiving-configured', 'project-samples-enabled']
            keys_csv = ['enabled-technologies']
            for key in keys_boolean:
                if key in resp:
                    resp[key] = resp[key] == 'true'
            for key in keys_csv:
                if key in resp:
                    resp[key] = list(map(lambda item: item.strip(), resp[key].split(',')))
            self.server_information = ServerInformation(resp)
            return self.server_information
        else:
            raise ValueError("Could not get the server information")


    def create_permId(self):
        """Have the server generate a new permId"""
        # Request just 1 permId
        request = {
            "method": "createPermIdStrings",
            "params": [self.token, 1],
        }
        resp = self._post_request(self.as_v3, request)
        if resp is not None:
            return resp[0]
        else:
            raise ValueError("Could not create permId")

    def get_datastores(self):
        """ Get a list of all available datastores. Usually there is only one, but in some cases
        there might be multiple servers. If you upload a file, you need to specifiy the datastore you want
        the file uploaded to.
        """

        request = {
            "method": "searchDataStores",
            "params": [
                self.token,
                {
                    "@type": "as.dto.datastore.search.DataStoreSearchCriteria"
                },
                {
                    "@type": "as.dto.datastore.fetchoptions.DataStoreFetchOptions"
                }
            ]
        }
        resp = self._post_request(self.as_v3, request)
        attrs=['code','downloadUrl','remoteUrl']
        if len(resp['objects']) == 0:
            raise ValueError("No datastore found!")
        else:
            objects = resp['objects']
            parse_jackson(objects)
            datastores = DataFrame(objects)
            return datastores[attrs]

    def gen_code(self, entity, prefix=""):
        """ Get the next sequence number for a Sample, Experiment, DataSet and Material. Other entities are currently not supported.
        Usage::
            gen_code('SAMPLE', 'SAM-')
            gen_code('EXPERIMENT', 'EXP-')
            gen_code('DATASET', '')
            gen_code('MATERIAL', 'MAT-')
        """

        entity = entity.upper()
        entity2enum = {
            "DATASET" : "DATA_SET",
            "OBJECT"  : "SAMPLE",
            "SAMPLE"  : "SAMPLE",
            "EXPERIMENT" : "EXPERIMENT",
            "COLLECTION" : "EXPERIMENT",
            "MATERIAL" : "MATERIAL",
        }

        if entity not in entity2enum:
            raise ValueError("no such entity: {}. Allowed entities are: DATA_SET, SAMPLE, EXPERIMENT, MATERIAL")

        request = {
            "method": "generateCode",
            "params": [
                self.token,
                prefix,
                entity2enum[entity]
            ]
        }
        try:
            return self._post_request(self.as_v1, request)
        except Exception as e:
            raise ValueError("Could not generate a code for {}: {}".format(entity, e))


    def gen_permId(self, count=1):
        """ Generate a permId (or many permIds) for a dataSet
        """

        request = {
            "method": "createPermIdStrings",
            "params": [
                self.token,
                count
            ]
        }
        try:
            return self._post_request(self.as_v3, request)
        except Exception as e:
            raise ValueError("Could not generate a code for {}: {}".format(entity, e))
            

    def new_person(self, userId, space=None):
        """ creates an openBIS person
        """
        try:
            person = self.get_person(userId=userId)
        except Exception:
            return Person(self, userId=userId, space=space) 

        raise ValueError(
            "There already exists a user with userId={}".format(userId)
        )


    def new_group(self, code, description=None, userIds=None):
        """ creates an openBIS person
        """
        return Group(self, code=code, description=description, userIds=userIds)


    def get_group(self, code, only_data=False):
        """ Get an openBIS AuthorizationGroup. Returns a Group object.
        """

        ids = [{
            "@type": "as.dto.authorizationgroup.id.AuthorizationGroupPermId",
            "permId": code
        }]

        fetchopts = {
            "@type": "as.dto.authorizationgroup.fetchoptions.AuthorizationGroupFetchOptions"
        }
        for option in ['roleAssignments', 'users', 'registrator']:
            fetchopts[option] = fetch_option[option]

        fetchopts['users']['space'] = fetch_option['space']

        request = {
            "method": "getAuthorizationGroups",
            "params": [
                self.token,
                ids,
                fetchopts
            ]
        }
        resp = self._post_request(self.as_v3, request)
        if len(resp) == 0:
            raise ValueError("No group found!")

        for permid in resp:
            group = resp[permid]
            parse_jackson(group)

            if only_data:
                return group
            else:
                return Group(self, data=group)

    def get_role_assignments(self, start_with=None, count=None, **search_args):
        """ Get the assigned roles for a given group, person or space
        """
        search_criteria = get_search_type_for_entity('roleAssignment', 'AND')
        allowed_search_attrs = ['role', 'roleLevel', 'user', 'group', 'person', 'space']

        sub_crit = []
        for attr in search_args:
            if attr in allowed_search_attrs:
                if attr == 'space':
                    sub_crit.append(
                        _subcriteria_for_code(search_args[attr], 'space')
                    )
                elif attr in ['user','person']:
                    userId = ''
                    if isinstance(search_args[attr], str):
                        userId = search_args[attr]
                    else:
                        userId = search_args[attr].userId

                    sub_crit.append(
                        _subcriteria_for_userId(userId)    
                    )
                elif attr == 'group':
                    groupId = ''
                    if isinstance(search_args[attr], str):
                        groupId = search_args[attr]
                    else:
                        groupId = search_args[attr].code
                    sub_crit.append(
                        _subcriteria_for_permid(groupId, 'AuthorizationGroup')
                    )
                elif attr == 'role':
                    # TODO
                    raise ValueError("not yet implemented")
                elif attr == 'roleLevel':
                    # TODO
                    raise ValueError("not yet implemented")
                else:
                    pass
            else:
                raise ValueError("unknown search argument {}".format(attr))

        search_criteria['criteria'] = sub_crit

        fetchopts = fetch_option['roleAssignments']
        fetchopts['from'] = start_with
        fetchopts['count'] = count
        for option in ['space', 'project', 'user', 'authorizationGroup','registrator']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchRoleAssignments",
            "params": [
                self.token,
                search_criteria,
                fetchopts
            ]
        }

        attrs=['techId', 'role', 'roleLevel', 'user', 'group', 'space', 'project']
        resp = self._post_request(self.as_v3, request)
        if len(resp['objects']) == 0:
            roles = DataFrame(columns=attrs)
        else: 
            objects = resp['objects']
            parse_jackson(objects)
            roles = DataFrame(objects)
            roles['techId'] = roles['id'].map(extract_id)
            roles['user'] = roles['user'].map(extract_userId)
            roles['group'] = roles['authorizationGroup'].map(extract_code)
            roles['space'] = roles['space'].map(extract_code)
            roles['project'] = roles['project'].map(extract_code)

        return Things(
            openbis_obj = self,
            entity='role_assignment',
            df=roles[attrs],
            identifier_name='techId',
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
        )

    def get_role_assignment(self, techId, only_data=False):
        """ Fetches one assigned role by its techId.
        """

        fetchopts = {
            "@type": "as.dto.roleassignment.fetchoptions.RoleAssignmentFetchOptions"
        }
        for option in ['roleAssignments', 'space', 'project', 'user', 'authorizationGroup','registrator']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "getRoleAssignments",
            "params": [
                self.token,
                [{
                    "techId": str(techId),
                    "@type": "as.dto.roleassignment.id.RoleAssignmentTechId"
                }],
                fetchopts
            ]
        }

        resp = self._post_request(self.as_v3, request)
        if len(resp) == 0:
            raise ValueError("No assigned role found for techId={}".format(techId))
        
        for id in resp:
            data = resp[id]
            parse_jackson(data)

            if only_data:
                return data
            else:
                return RoleAssignment(self, data=data)


    def assign_role(self, role, **args):
        """ general method to assign a role to either
            - a person
            - a group
        The scope is either
            - the whole instance
            - a space
            - a project
        """
         
        userId = None
        groupId = None
        spaceId = None
        projectId = None

        for arg in args:
            if arg in ['person', 'group', 'space', 'project']:
                permId = args[arg] if isinstance(args[arg],str) else args[arg].permId
                if arg == 'person':
                    userId = {
                        "permId": permId,
                        "@type": "as.dto.person.id.PersonPermId"
                    }
                elif arg == 'group':
                    groupId = {
                        "permId": permId,
                        "@type": "as.dto.authorizationgroup.id.AuthorizationGroupPermId"
                    }
                elif arg == 'space':
                    spaceId = {
                        "permId": permId,
                        "@type": "as.dto.space.id.SpacePermId"
                    }
                elif arg == 'project':
                    projectId = {
                        "permId": permId,
                        "@type": "as.dto.project.id.ProjectPermId"
                    }

        request = {
            "method": "createRoleAssignments",
            "params": [
                self.token,
                [
	            {
                        "role": role,
                        "userId": userId,
		        "authorizationGroupId": groupId,
                        "spaceId": spaceId,
		        "projectId": projectId,
		        "@type": "as.dto.roleassignment.create.RoleAssignmentCreation",
	            }
	        ]
	    ]
	}
        resp = self._post_request(self.as_v3, request)
        return


    def get_groups(self, start_with=None, count=None, **search_args):
        """ Get openBIS AuthorizationGroups. Returns a «Things» object.

        Usage::
            groups = e.get.groups()
            groups[0]             # select first group
            groups['GROUP_NAME']  # select group with this code
            for group in groups:
                ...               # a Group object
            groups.df             # get a DataFrame object of the group list
            print(groups)         # print a nice ASCII table (eg. in IPython)
            groups                # HTML table (in a Jupyter notebook)

        """

        criteria = []
        for search_arg in ['code']:
            # unfortunately, there aren't many search possibilities yet...
            if search_arg in search_args:
                if search_arg == 'code':
                    criteria.append(_criteria_for_code(search_args[search_arg]))

        search_criteria = get_search_type_for_entity('authorizationGroup')
        search_criteria['criteria'] = criteria
        search_criteria['operator'] = 'AND'
                
        fetchopts = fetch_option['authorizationGroup']
        fetchopts['from'] = start_with
        fetchopts['count'] = count
        for option in ['roleAssignments', 'registrator', 'users']:
            fetchopts[option] = fetch_option[option]
        request = {
            "method": "searchAuthorizationGroups",
            "params": [
                self.token,
                search_criteria,
                fetchopts
            ],
        }
        resp = self._post_request(self.as_v3, request)

        attrs = ['permId', 'code', 'description', 'users', 'registrator', 'registrationDate', 'modificationDate']
        if len(resp['objects']) == 0:
            groups = DataFrame(columns=attrs)
        else:
            objects = resp['objects']
            parse_jackson(objects)
            groups = DataFrame(objects)

            groups['permId'] = groups['permId'].map(extract_permid)
            groups['registrator'] = groups['registrator'].map(extract_person)
            groups['users'] = groups['users'].map(extract_userId)
            groups['registrationDate'] = groups['registrationDate'].map(format_timestamp)
            groups['modificationDate'] = groups['modificationDate'].map(format_timestamp)
        return Things(
            openbis_obj = self,
            entity='group',
            df=groups[attrs],
            identifier_name='permId',
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
        )


    def get_persons(self, start_with=None, count=None, **search_args):
        """ Get openBIS users
        """

        search_criteria = get_search_criteria('person', **search_args)
        fetchopts = fetch_option['person']
        fetchopts['from'] = start_with
        fetchopts['count'] = count
        for option in ['space']:
            fetchopts[option] = fetch_option[option]
        request = {
            "method": "searchPersons",
            "params": [
                self.token,
                search_criteria,
                fetchopts
            ],
        }
        resp = self._post_request(self.as_v3, request)

        attrs = ['permId', 'userId', 'firstName', 'lastName', 'email', 'space', 'registrationDate', 'active']
        if len(resp['objects']) == 0:
            persons = DataFrame(columns=attrs)
        else:
            objects = resp['objects']
            parse_jackson(objects)

            persons = DataFrame(resp['objects'])
            persons['permId'] = persons['permId'].map(extract_permid)
            persons['registrationDate'] = persons['registrationDate'].map(format_timestamp)
            persons['space'] = persons['space'].map(extract_nested_permid)

        return Things(
            openbis_obj = self,
            entity='person',
            df=persons[attrs],
            identifier_name='permId',
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
        )


    get_users = get_persons # Alias


    def get_person(self, userId, only_data=False):
        """ Get a person (user)
        """
         
        ids = [{
            "@type": "as.dto.person.id.PersonPermId",
            "permId": userId
        }]

        fetchopts = {
            "@type": "as.dto.person.fetchoptions.PersonFetchOptions"
        }
        for option in ['space', 'project']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "getPersons",
            "params": [
                self.token,
                ids,
                fetchopts,
            ],
        }
        
        resp = self._post_request(self.as_v3, request)
        if len(resp) == 0:
            raise ValueError("No person found!")


        for permid in resp:
            person = resp[permid]
            parse_jackson(person)

            if only_data:
                return person
            else:
                return Person(self, data=person)

    get_user = get_person # Alias


    def get_spaces(self, code=None, start_with=None, count=None):
        """ Get a list of all available spaces (DataFrame object). To create a sample or a
        dataset, you need to specify in which space it should live.
        """

        search_criteria = _subcriteria_for_code(code, 'space')
        fetchopts = fetch_option['space']
        fetchopts['from'] = start_with
        fetchopts['count'] = count
        request = {
            "method": "searchSpaces",
            "params": [self.token,
                       search_criteria,
                       fetchopts,
                       ],
        }
        resp = self._post_request(self.as_v3, request)

        attrs = ['code', 'description', 'registrationDate', 'modificationDate']
        if len(resp['objects']) == 0:
            spaces = DataFrame(columns=attrs)
        else:
            spaces = DataFrame(resp['objects'])
            spaces['registrationDate'] = spaces['registrationDate'].map(format_timestamp)
            spaces['modificationDate'] = spaces['modificationDate'].map(format_timestamp)
        return Things(
            openbis_obj = self,
            entity = 'space',
            df = spaces[attrs],
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
        )


    def get_space(self, code, only_data=False):
        """ Returns a Space object for a given identifier.
        """

        code = str(code).upper()
        fetchopts = {"@type": "as.dto.space.fetchoptions.SpaceFetchOptions"}
        for option in ['registrator']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "getSpaces",
            "params": [
                self.token,
                [{
                    "permId": code,
                    "@type": "as.dto.space.id.SpacePermId"
                }],
                fetchopts
            ],
        }
        resp = self._post_request(self.as_v3, request)
        if len(resp) == 0:
            raise ValueError("No such space: %s" % code)

        for permid in resp:
            if only_data:
                return resp[permid]
            else:
                return Space(self, data=resp[permid])


    def get_samples(
        self, identifier=None, code=None, permId=None,
        space=None, project=None, experiment=None, type=None,
        start_with=None, count=None,
        withParents=None, withChildren=None, tags=None, props=None, **properties
    ):
        """ Get a list of all samples for a given space/project/experiment (or any combination)
        """

        sub_criteria = []

        # v3 API does not offer a search for identifiers. We need to do a combined search instead:
        # space && code or
        # space && project && code
        if identifier:
            identifier = identifier.lstrip('/')
            elements = identifier.split('/')
            if len(elements) == 2:
                space = elements[0]
                code  = elements[1]
            elif len(elements) == 3:
                space = elements[0]
                code  = elements[2]
            else:
                raise ValueError("{} is not a valid sample identifier.".format(identifier))

        if space:
            sub_criteria.append(_subcriteria_for_code(space, 'space'))
        if project:
            proj_crit = _subcriteria_for_code(project, 'project')
            sub_criteria.append(proj_crit)
        if experiment:
            sub_criteria.append(_subcriteria_for_code(experiment, 'experiment'))
        if properties is not None:
            for prop in properties:
                sub_criteria.append(_subcriteria_for_properties(prop, properties[prop]))
        if type:
            sub_criteria.append(_subcriteria_for_code(type, 'sample_type'))
        if tags:
            sub_criteria.append(_subcriteria_for_tags(tags))
        if code:
            sub_criteria.append(_criteria_for_code(code))
        if permId:
            sub_criteria.append(_common_search("as.dto.common.search.PermIdSearchCriteria", permId))
        if withParents:
            if not isinstance(withParents, list):
                withParents = [withParents]
            for parent in withParents:
                sub_criteria.append(
                    _gen_search_criteria({
                        "sample": "SampleParents",
                        "identifier": parent
                    })
                )
        if withChildren:
            if not isinstance(withChildren, list):
                withChildren = [withChildren]
            for child in withChildren:
                sub_criteria.append(
                    _gen_search_criteria({
                        "sample": "SampleChildren",
                        "identifier": child
                    })
                )

        criteria = {
            "criteria": sub_criteria,
            "@type": "as.dto.sample.search.SampleSearchCriteria",
            "operator": "AND"
        }

        # build the various fetch options
        fetchopts = fetch_option['sample']
        fetchopts['from'] = start_with
        fetchopts['count'] = count

        for option in ['tags', 'properties', 'registrator', 'modifier', 'experiment']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchSamples",
            "params": [self.token,
                       criteria,
                       fetchopts,
                       ],
        }
        resp = self._post_request(self.as_v3, request)

        return self._sample_list_for_response(
            response=resp['objects'],
            props=props,
            start_with=start_with,
            count=count,
            totalCount=resp['totalCount'],
        )


    get_objects = get_samples # Alias


    def get_experiments(
        self, code=None, permId=None, type=None, space=None, project=None,
        start_with=None, count=None,
        tags=None, is_finished=None, props=None, **properties
    ):
        """ Searches for all experiment which match the search criteria. Returns a
        «Things» object which can be used in many different situations.

        Usage::
            experiments = get_experiments(project='PROJECT_NAME', props=['NAME','FINISHED_FLAG'])
            experiments[0]  # returns first experiment
            experiments['/MATERIALS/REAGENTS/ANTIBODY_COLLECTION']
            for experiment in experiment:
                # handle every experiment
                ...
            experiments.df      # returns DataFrame object of the experiment list
            print(experiments)  # prints a nice ASCII table
        """

        sub_criteria = []
        if space:
            sub_criteria.append(_subcriteria_for_code(space, 'space'))
        if project:
            sub_criteria.append(_subcriteria_for_code(project, 'project'))
        if code:
            sub_criteria.append(_criteria_for_code(code))
        if permId:
            sub_criteria.append(_common_search("as.dto.common.search.PermIdSearchCriteria", permId))
        if type:
            sub_criteria.append(_subcriteria_for_type(type, 'Experiment'))
        if tags:
            sub_criteria.append(_subcriteria_for_tags(tags))
        if is_finished is not None:
            sub_criteria.append(_subcriteria_for_is_finished(is_finished))
        if properties is not None:
            for prop in properties:
                sub_criteria.append(_subcriteria_for_properties(prop, properties[prop]))

        search_criteria = get_search_type_for_entity('experiment')
        search_criteria['criteria'] = sub_criteria
        search_criteria['operator'] = 'AND'

        fetchopts = fetch_option['experiment']
        fetchopts['from'] = start_with
        fetchopts['count'] = count
        for option in ['tags', 'properties', 'registrator', 'modifier', 'project']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchExperiments",
            "params": [
                self.token,
                search_criteria,
                fetchopts,
            ],
        }
        resp = self._post_request(self.as_v3, request)
        attrs = ['identifier', 'permId', 'project', 'type',
                 'registrator', 'registrationDate', 'modifier', 'modificationDate']
        if len(resp['objects']) == 0:
            experiments = DataFrame(columns=attrs)
        else:
            objects = resp['objects']
            parse_jackson(objects)

            experiments = DataFrame(objects)
            experiments['registrationDate'] = experiments['registrationDate'].map(format_timestamp)
            experiments['modificationDate'] = experiments['modificationDate'].map(format_timestamp)
            experiments['project'] = experiments['project'].map(extract_code)
            experiments['registrator'] = experiments['registrator'].map(extract_person)
            experiments['modifier'] = experiments['modifier'].map(extract_person)
            experiments['identifier'] = experiments['identifier'].map(extract_identifier)
            experiments['permId'] = experiments['permId'].map(extract_permid)
            experiments['type'] = experiments['type'].map(extract_code)

        if props is not None:
            for prop in props:
                experiments[prop.upper()] = experiments['properties'].map(lambda x: x.get(prop.upper(), ''))
                attrs.append(prop.upper())

        return Things(
            openbis_obj = self,
            entity = 'experiment',
            df = experiments[attrs],
            identifier_name ='identifier',
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
        )
    get_collections = get_experiments  # Alias


    def get_datasets(
        self, code=None, type=None, withParents=None, withChildren=None,
        start_with=None, count=None, kind=None,
        status=None, sample=None, experiment=None, project=None,
        tags=None, props=None, **properties
    ):

        sub_criteria = []

        if code:
            sub_criteria.append(_criteria_for_code(code))
        if type:
            sub_criteria.append(_subcriteria_for_type(type, 'DataSet'))
        if withParents:
            sub_criteria.append(_subcriteria_for_permid(withParents, 'DataSet', 'Parents'))
        if withChildren:
            sub_criteria.append(_subcriteria_for_permid(withChildren, 'DataSet', 'Children'))

        if sample:
            sub_criteria.append(_subcriteria_for_code(sample, 'Sample'))
        if experiment:
            sub_criteria.append(_subcriteria_for_code(experiment, 'Experiment'))
        if project:
            exp_crit = _subcriteria_for_code(experiment, 'Experiment')
            proj_crit = _subcriteria_for_code(project, 'Project')
            exp_crit['criteria'] = []
            exp_crit['criteria'].append(proj_crit)
            sub_criteria.append(exp_crit)
        if tags:
            sub_criteria.append(_subcriteria_for_tags(tags))
        if status:
            sub_criteria.append(_subcriteria_for_status(status))
        if properties is not None:
            for prop in properties:
                sub_criteria.append(_subcriteria_for_properties(prop, properties[prop]))

        search_criteria = get_search_type_for_entity('dataset')
        search_criteria['criteria'] = sub_criteria
        search_criteria['operator'] = 'AND'

        fetchopts = {
            "@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions",
            "containers": {"@type": "as.dto.dataset.fetchoptions.DataSetFetchOptions"},
            "type": {"@type": "as.dto.dataset.fetchoptions.DataSetTypeFetchOptions"}
        }
        fetchopts['from'] = start_with
        fetchopts['count'] = count
        if kind:
            kind = kind.upper()
            if kind not in ['PHYSICAL_DATA', 'CONTAINER', 'LINK']:
                raise ValueError("unknown dataSet kind: {}. It should be one of the following: PHYSICAL_DATA, CONTAINER or LINK".format(kind))
            fetchopts['kind'] = kind
            raise NotImplementedError('you cannot search for dataSet kinds yet')

        for option in ['tags', 'properties', 'sample', 'experiment', 'physicalData']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchDataSets",
            "params": [self.token,
                       search_criteria,
                       fetchopts,
                       ],
        }
        resp = self._post_request(self.as_v3, request)

        return self._dataset_list_for_response(
            response=resp['objects'],
            props=props,
            start_with=start_with,
            count=count,
            totalCount=resp['totalCount'],
        )


    def get_experiment(self, expId, withAttachments=False, only_data=False):
        """ Returns an experiment object for a given identifier (expId).
        """

        fetchopts = {
            "@type": "as.dto.experiment.fetchoptions.ExperimentFetchOptions",
            "type": {
                "@type": "as.dto.experiment.fetchoptions.ExperimentTypeFetchOptions",
            },
        }

        search_request = _type_for_id(expId, 'experiment')
        for option in ['tags', 'properties', 'attachments', 'project', 'samples', 'registrator', 'modifier']:
            fetchopts[option] = fetch_option[option]


        if withAttachments:
            fetchopts['attachments'] = fetch_option['attachmentsWithContent']

        request = {
            "method": "getExperiments",
            "params": [
                self.token,
                [search_request],
                fetchopts
            ],
        }
        resp = self._post_request(self.as_v3, request)
        if len(resp) == 0:
            raise ValueError("No such experiment: %s" % expId)

        parse_jackson(resp)
        for id in resp:
            if only_data:
                return resp[id]
            else:
                return Experiment(
                    openbis_obj = self,
                    type = self.get_experiment_type(resp[expId]["type"]["code"]),
                    data = resp[id]
                )
    get_collection = get_experiment  # Alias


    def new_experiment(self, type, code, project, props=None, **kwargs):
        """ Creates a new experiment of a given experiment type.
        """
        return Experiment(
            openbis_obj = self,
            type = self.get_experiment_type(type),
            project = project,
            data = None,
            props = props,
            code = code,
            **kwargs
        )
    new_collection = new_experiment  # Alias


    def update_experiment(self, experimentId, properties=None, tagIds=None, attachments=None):
        params = {
            "experimentId": {
                "permId": experimentId,
                "@type": "as.dto.experiment.id.ExperimentPermId"
            },
            "@type": "as.dto.experiment.update.ExperimentUpdate"
        }
        if properties is not None:
            params["properties"] = properties
        if tagIds is not None:
            params["tagIds"] = tagIds
        if attachments is not None:
            params["attachments"] = attachments

        request = {
            "method": "updateExperiments",
            "params": [
                self.token,
                [params]
            ]
        }
        self._post_request(self.as_v3, request)
    update_collection = update_experiment  # Alias


    def create_external_data_management_system(self, code, label, address, address_type='FILE_SYSTEM'):
        """Create an external DMS.
        :param code: An openBIS code for the external DMS.
        :param label: A human-readable label.
        :param address: The address for accessing the external DMS. E.g., a URL.
        :param address_type: One of OPENBIS, URL, or FILE_SYSTEM
        :return:
        """
        request = {
            "method": "createExternalDataManagementSystems",
            "params": [
                self.token,
                [
                    {
                        "code": code,
                        "label": label,
                        "addressType": address_type,
                        "address": address,
                        "@type": "as.dto.externaldms.create.ExternalDmsCreation",
                    }
                ]
            ],
        }
        resp = self._post_request(self.as_v3, request)
        return self.get_external_data_management_system(resp[0]['permId'])

    def update_sample(self, sampleId, space=None, project=None, experiment=None,
                      parents=None, children=None, components=None, properties=None, tagIds=None, attachments=None):
        params = {
            "sampleId": {
                "permId": sampleId,
                "@type": "as.dto.sample.id.SamplePermId"
            },
            "@type": "as.dto.sample.update.SampleUpdate"
        }
        if space is not None:
            params['spaceId'] = space
        if project is not None:
            params['projectId'] = project
        if properties is not None:
            params["properties"] = properties
        if tagIds is not None:
            params["tagIds"] = tagIds
        if attachments is not None:
            params["attachments"] = attachments

        request = {
            "method": "updateSamples",
            "params": [
                self.token,
                [params]
            ]
        }
        self._post_request(self.as_v3, request)

    update_object = update_sample # Alias


    def delete_entity(self, entity, id, reason, id_name='permId'):
        """Deletes Spaces, Projects, Experiments, Samples and DataSets
        """

        entity_type = "as.dto.{}.id.{}{}{}".format(
            entity.lower(), entity,
            id_name[0].upper(), id_name[1:]
        )
        request = {
            "method": "delete{}s".format(entity),
            "params": [
                self.token,
                [
                    {
                        id_name: id,
                        "@type": entity_type
                    }
                ],
                {
                    "reason": reason,
                    "@type": "as.dto.{}.delete.{}DeletionOptions".format(
                        entity.lower(), entity)
                }
            ]
        }
        resp = self._post_request(self.as_v3, request)


    def delete_openbis_entity(self, entity, objectId, reason='No reason given'):
        method = get_method_for_entity(entity, 'delete')
        delete_options = get_type_for_entity(entity, 'delete')
        delete_options['reason'] = reason

        request = {
           "method": method,
           "params": [
                self.token,
                [ objectId ],
                delete_options
            ]
        }
        resp = self._post_request(self.as_v3, request)
        return


    def get_deletions(self, start_with=None, count=None):
        search_criteria = {
            "@type": "as.dto.deletion.search.DeletionSearchCriteria"
        }
        fetchopts = fetch_option['deletion']
        fetchoptsDeleted = fetch_option['deletedObjects']
        fetchoptsDeleted['from'] = start_with
        fetchoptsDeleted['count'] = count
        fetchopts['deletedObjects'] = fetchoptsDeleted

        request = {
            "method": "searchDeletions",
            "params": [
                self.token,
                search_criteria,
                fetchopts,
            ]
        }
        resp = self._post_request(self.as_v3, request)
        objects = resp['objects']
        parse_jackson(objects)

        new_objs = []
        for value in objects:
            del_objs = extract_deletion(value)
            if len(del_objs) > 0:
                new_objs.append(*del_objs)

        return DataFrame(new_objs)

    def new_project(self, space, code, description=None, **kwargs):
        return Project(self, None, space=space, code=code, description=description, **kwargs)

    def _gen_fetchoptions(self, options, foType):
        fo = {
            "@type": foType
        }
        for option in options:
            fo[option] = fetch_option[option]
        return fo

    def get_project(self, projectId, only_data=False):
        options = ['space', 'registrator', 'modifier', 'attachments']
        if is_identifier(projectId) or is_permid(projectId):
            request = self._create_get_request(
                'getProjects', 'project', projectId, options,
                "as.dto.project.fetchoptions.ProjectFetchOptions"
            )
            resp = self._post_request(self.as_v3, request)
            if only_data:
                return resp[projectId]

            return Project(self, resp[projectId])

        else:
            search_criteria = _gen_search_criteria({
                'project': 'Project',
                'operator': 'AND',
                'code': projectId
            })
            fo = self._gen_fetchoptions(options, foType="as.dto.project.fetchoptions.ProjectFetchOptions")
            request = {
                "method": "searchProjects",
                "params": [self.token, search_criteria, fo]
            }
            resp = self._post_request(self.as_v3, request)
            if len(resp['objects']) == 0:
                raise ValueError("No such project: %s" % projectId)
            if only_data:
                return resp['objects'][0]

            return Project(self, resp['objects'][0])

    def get_projects(
        self, space=None, code=None,
        start_with=None, count=None,
    ):
        """ Get a list of all available projects (DataFrame object).
        """

        sub_criteria = []
        if space:
            sub_criteria.append(_subcriteria_for_code(space, 'space'))
        if code:
            sub_criteria.append(_criteria_for_code(code))

        criteria = {
            "criteria": sub_criteria,
            "@type": "as.dto.project.search.ProjectSearchCriteria",
            "operator": "AND"
        }

        fetchopts = {"@type": "as.dto.project.fetchoptions.ProjectFetchOptions"}
        fetchopts['from'] = start_with
        fetchopts['count'] = count
        for option in ['registrator', 'modifier', 'leader']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchProjects",
            "params": [self.token,
                       criteria,
                       fetchopts,
                       ],
        }
        resp = self._post_request(self.as_v3, request)

        attrs = ['identifier', 'permId', 'leader', 'registrator', 'registrationDate', 'modifier', 'modificationDate']
        if len(resp['objects']) == 0:
            projects = DataFrame(columns=attrs)        
        else:
            objects = resp['objects']
            parse_jackson(objects)

            projects = DataFrame(objects)

            projects['registrationDate'] = projects['registrationDate'].map(format_timestamp)
            projects['modificationDate'] = projects['modificationDate'].map(format_timestamp)
            projects['leader'] = projects['leader'].map(extract_person)
            projects['registrator'] = projects['registrator'].map(extract_person)
            projects['modifier'] = projects['modifier'].map(extract_person)
            projects['permId'] = projects['permId'].map(extract_permid)
            projects['identifier'] = projects['identifier'].map(extract_identifier)

        return Things(
            openbis_obj = self,
            entity = 'project',
            df = projects[attrs],
            identifier_name = 'identifier',
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
        )


    def _create_get_request(self, method_name, entity, permids, options, foType):

        if not isinstance(permids, list):
            permids = [permids]

        type = "as.dto.{}.id.{}".format(entity.lower(), entity.capitalize())
        search_params = []
        for permid in permids:
            # decide if we got a permId or an identifier
            match = re.match('/', permid)
            if match:
                search_params.append(
                    {"identifier": permid, "@type": type + 'Identifier'}
                )
            else:
                search_params.append(
                    {"permId": permid, "@type": type + 'PermId'}
                )

        fo = {
            "@type": foType
        }
        for option in options:
            fo[option] = fetch_option[option]

        request = {
            "method": method_name,
            "params": [
                self.token,
                search_params,
                fo
            ],
        }
        return request

    def get_terms(self, vocabulary=None, start_with=None, count=None):
        """ Returns information about existing vocabulary terms. 
        If a vocabulary code is provided, it only returns the terms of that vocabulary.
        """

        search_request = {}
        if vocabulary is not None:
            search_request = _gen_search_criteria({
                "vocabulary": "VocabularyTerm",
                "criteria": [{
                    "vocabulary": "Vocabulary",
                    "code": vocabulary
                }]
            })
        search_request["@type"] = "as.dto.vocabulary.search.VocabularyTermSearchCriteria"

        fetchopts = fetch_option['vocabularyTerm']
        fetchopts['from'] = start_with
        fetchopts['count'] = count

        request = {
            "method": "searchVocabularyTerms",
            "params": [self.token, search_request, fetchopts]
        }
        resp = self._post_request(self.as_v3, request)

        attrs = 'code vocabularyCode label description registrationDate modificationDate official ordinal'.split()

        if len(resp['objects']) == 0:
            terms = DataFrame(columns=attrs)
        else:
            objects = resp['objects']
            parse_jackson(objects)
            terms = DataFrame(objects)
            terms['vocabularyCode'] = terms['permId'].map(extract_attr('vocabularyCode'))
            terms['registrationDate'] = terms['registrationDate'].map(format_timestamp)
            terms['modificationDate'] = terms['modificationDate'].map(format_timestamp)

        return Things(
            openbis_obj = self,
            entity = 'term',
            df = terms[attrs],
            identifier_name='code',
            additional_identifier='vocabularyCode',
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
        )
        

    def new_term(self, code, vocabularyCode, label=None, description=None):
        return VocabularyTerm(
            self, data=None,
            code=code, vocabularyCode=vocabularyCode,
            label=label, description=description
        )


    def get_term(self, code, vocabularyCode=None, only_data=False):
        entity_def = get_definition_for_entity('VocabularyTerm')
        search_request = {
            "code": code,
            "vocabularyCode": vocabularyCode,
            "@type": "as.dto.vocabulary.id.VocabularyTermPermId"
        }
        fetchopts = get_fetchoption_for_entity('VocabularyTerm')
        for opt in ['registrator']:
            fetchopts[opt] = get_fetchoption_for_entity(opt)
        
        request = {
            "method": 'getVocabularyTerms',
            "params": [
                self.token,
                [search_request],
                fetchopts
            ],
        }
        resp = self._post_request(self.as_v3, request)

        if resp is None or len(resp) == 0:
            raise ValueError("no VocabularyTerm found with code='{}' and vocabularyCode='{}'".format(code, vocabularyCode))
        else:
            parse_jackson(resp)
            for ident in resp:
                if only_data:
                    return resp[ident]
                else:
                    return VocabularyTerm(self, resp[ident])


    def _get_any_entity(self, identifier, entity, only_data=False, method=None):

        entity_def = get_definition_for_entity(entity)

        # guess the method to fetch an entity
        if method is None:
            method = 'get' + entity + 's'

        search_request = _type_for_id(identifier, entity)
        fetchopts = get_fetchoption_for_entity(entity)
        
        request = {
            "method": method,
            "params": [
                self.token,
                [search_request],
                fetchopts
            ],
        }
        resp = self._post_request(self.as_v3, request)

        if resp is None or len(resp) == 0:
            raise ValueError('no {} found with identifier: {}'.format(entity, identifier))
        else:
            parse_jackson(resp)
            for ident in resp:
                if only_data:
                    return resp[ident]
                else:
                    # get a dynamic instance of that class
                    klass = globals()[entity]
                    return klass(self, resp[ident])


    def get_vocabularies(self, code=None, start_with=None, count=None):
        """ Returns information about vocabulary
        """

        sub_criteria = []
        if code:
            sub_criteria.append(_criteria_for_code(code))
        criteria = {
            "criteria": sub_criteria,
            "@type": "as.dto.vocabulary.search.VocabularySearchCriteria",
            "operator": "AND"
        }

        fetchopts = fetch_option['vocabulary']
        fetchopts['from'] = start_with
        fetchopts['count'] = count
        for option in ['registrator']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchVocabularies",
            "params": [self.token, criteria, fetchopts]
        }
        resp = self._post_request(self.as_v3, request)

        attrs = 'code description managedInternally internalNameSpace chosenFromList urlTemplate registrator registrationDate modificationDate'.split()

        if len(resp['objects']) == 0:
            vocs = DataFrame(columns=attrs)
        else:
            objects = resp['objects']
            parse_jackson(resp)
            vocs = DataFrame(objects)
            vocs['registrationDate'] = vocs['registrationDate'].map(format_timestamp)
            vocs['modificationDate'] = vocs['modificationDate'].map(format_timestamp)
            vocs['registrator']      = vocs['registrator'].map(extract_person)

        return Things(
            openbis_obj = self,
            entity = 'vocabulary',
            df = vocs[attrs],
            identifier_name = 'code',
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
            )


    def get_vocabulary(self, code, only_data=False):
        """ Returns the details of a given vocabulary (including vocabulary terms)
        """
        return self._get_any_entity(code, 'Vocabulary', only_data=only_data, method='getVocabularies')


    def new_tag(self, code, description=None):
        """ Creates a new tag (for this user)
        """
        return Tag(self, code=code, description=description)


    def get_tags(self, code=None, start_with=None, count=None):
        """ Returns a DataFrame of all tags
        """

        search_criteria = get_search_type_for_entity('tag', 'AND')

        criteria = []
        fetchopts = fetch_option['tag']
        fetchopts['from'] = start_with
        fetchopts['count'] = count
        for option in ['owner']:
            fetchopts[option] = fetch_option[option]
        if code:
            criteria.append(_criteria_for_code(code))
        search_criteria['criteria'] = criteria
        request = {
            "method": "searchTags",
            "params": [
                self.token,
                search_criteria,
                fetchopts
            ]
        }

        resp = self._post_request(self.as_v3, request)
        return self._tag_list_for_response(response=resp['objects'], totalCount=resp['totalCount'])


    def get_tag(self, permId, only_data=False):
        """ Returns a specific tag
        """

        just_one = True
        identifiers = []
        if isinstance(permId, list):
            just_one = False
            for ident in permId:
                identifiers.append(_type_for_id(ident, 'tag'))
        else:
            identifiers.append(_type_for_id(permId, 'tag'))

        fetchopts = fetch_option['tag']
        for option in ['owner']:
            fetchopts[option] = fetch_option[option]
        request = {
            "method": "getTags",
            "params": [
                self.token,
                identifiers,
                fetchopts
            ],
        }

        resp = self._post_request(self.as_v3, request)

        if just_one:
            if len(resp) == 0:
                raise ValueError('no such tag found: {}'.format(permId))

            parse_jackson(resp)
            for permId in resp:
                if only_data:
                    return resp[permId]
                else:
                    return Tag(self, data=resp[permId])
        else:
            return self._tag_list_for_response( response=list(resp.values()) )

    def _tag_list_for_response(self, response, totalCount=0):

        parse_jackson(response)
        attrs = ['permId', 'code', 'description', 'owner', 'private', 'registrationDate']
        if len(response) == 0:
            tags = DataFrame(columns = attrs)
        else: 
            tags = DataFrame(response)
            tags['registrationDate'] = tags['registrationDate'].map(format_timestamp)
            tags['permId']           = tags['permId'].map(extract_permid)
            tags['description']      = tags['description'].map(lambda x: '' if x is None else x)
            tags['owner']            = tags['owner'].map(extract_person)

        return Things(
            openbis_obj = self,
            entity = 'tag',
            df = tags[attrs],
            identifier_name ='permId',
            totalCount = totalCount,
        )


    def search_semantic_annotations(self, 
        permId=None, entityType=None, propertyType=None, only_data=False
    ):
        """ Get a list of semantic annotations for permId, entityType, propertyType or 
        property type assignment (DataFrame object).
        :param permId: permId of the semantic annotation.
        :param entityType: entity (sample) type to search for.
        :param propertyType: property type to search for
        :param only_data: return result as plain data object.
        :return:  Things of DataFrame objects or plain data object
        """

        criteria = []
        typeCriteria = []

        if permId is not None:
            criteria.append({
                "@type" : "as.dto.common.search.PermIdSearchCriteria",
                "fieldValue" : {
                    "@type" : "as.dto.common.search.StringEqualToValue",
                    "value" : permId
                }
            })

        if entityType is not None:
            typeCriteria.append({
                "@type" : "as.dto.entitytype.search.EntityTypeSearchCriteria",
                "criteria" : [_criteria_for_code(entityType)]
            })

        if propertyType is not None:
            typeCriteria.append({
                "@type" : "as.dto.property.search.PropertyTypeSearchCriteria",
                "criteria" : [_criteria_for_code(propertyType)]
            })

        if entityType is not None and propertyType is not None:
            criteria.append({
                "@type" : "as.dto.property.search.PropertyAssignmentSearchCriteria",
                "criteria" : typeCriteria
            })
        else:
            criteria += typeCriteria

        saCriteria = {
            "@type" : "as.dto.semanticannotation.search.SemanticAnnotationSearchCriteria",
            "criteria" : criteria
        }

        objects = self._search_semantic_annotations(saCriteria)

        if only_data:
            return objects

        attrs = ['permId', 'entityType', 'propertyType', 'predicateOntologyId', 'predicateOntologyVersion', 'predicateAccessionId', 'descriptorOntologyId', 'descriptorOntologyVersion', 'descriptorAccessionId', 'creationDate']
        if len(objects) == 0:
            annotations = DataFrame(columns=attrs)
        else:
            annotations = DataFrame(objects)

        return Things(
            openbis_obj = self,
            entity = 'semantic_annotation',
            df = annotations[attrs],
            identifier_name = 'permId',
        )

    def _search_semantic_annotations(self, criteria):

        fetch_options = {
            "@type": "as.dto.semanticannotation.fetchoptions.SemanticAnnotationFetchOptions",
            "entityType": {"@type": "as.dto.entitytype.fetchoptions.EntityTypeFetchOptions"},
            "propertyType": {"@type": "as.dto.property.fetchoptions.PropertyTypeFetchOptions"},
            "propertyAssignment": {
                "@type": "as.dto.property.fetchoptions.PropertyAssignmentFetchOptions",
                "entityType" : {
                    "@type" : "as.dto.entitytype.fetchoptions.EntityTypeFetchOptions"
                },
                "propertyType" : {
                    "@type" : "as.dto.property.fetchoptions.PropertyTypeFetchOptions"
                }
            }
        }

        request = {
            "method": "searchSemanticAnnotations",
            "params": [self.token, criteria, fetch_options]
        }

        resp = self._post_request(self.as_v3, request)
        if len(resp['objects']) == 0:
            return []
        else:
            objects = resp['objects']
            parse_jackson(objects)
            
            for object in objects:
                object['permId'] = object['permId']['permId']
                if object.get('entityType') is not None:
                    object['entityType'] = object['entityType']['code']
                elif object.get('propertyType') is not None:
                    object['propertyType'] = object['propertyType']['code']
                elif object.get('propertyAssignment') is not None:
                    object['entityType'] = object['propertyAssignment']['entityType']['code']
                    object['propertyType'] = object['propertyAssignment']['propertyType']['code']
                object['creationDate'] = format_timestamp(object['creationDate'])
                
            return objects


    def get_semantic_annotations(self):
        """ Get a list of all available semantic annotations (DataFrame object).
        """

        objects = self._search_semantic_annotations({
            "@type": "as.dto.semanticannotation.search.SemanticAnnotationSearchCriteria"
        })
        attrs = ['permId', 'entityType', 'propertyType', 'predicateOntologyId', 'predicateOntologyVersion', 'predicateAccessionId', 'descriptorOntologyId', 'descriptorOntologyVersion', 'descriptorAccessionId', 'creationDate']
        if len(objects) == 0:
            annotations = DataFrame(columns=attrs)
        else:
            annotations = DataFrame(objects)
        return Things(
            openbis_obj = self,
            entity = 'semantic_annotation',
            df = annotations[attrs],
            identifier_name = 'permId',
        )

    def get_semantic_annotation(self, permId, only_data = False):
        objects = self.search_semantic_annotations(permId=permId, only_data=True)
        if len(objects) == 0:
            raise ValueError("Semantic annotation with permId " + permId +  " not found.")
        object = objects[0]
        if only_data:
            return object
        else:
            return SemanticAnnotation(self, isNew=False, **object)

    def get_plugins(self, start_with=None, count=None):

        criteria = []
        search_criteria = get_search_type_for_entity('plugin', 'AND')
        search_criteria['criteria'] = criteria

        fetchopts = fetch_option['plugin']
        for option in ['registrator']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "searchPlugins",
            "params": [
                self.token,
                search_criteria,
                fetchopts,
            ],
        }
        resp = self._post_request(self.as_v3, request)
        attrs = ['name', 'description', 'pluginType', 'pluginKind',
        'entityKinds', 'registrator', 'registrationDate', 'permId']

        if len(resp['objects']) == 0:
            plugins = DataFrame(columns=attrs)
        else:
            objects = resp['objects']
            parse_jackson(objects)

            plugins = DataFrame(objects)
            plugins['permId'] = plugins['permId'].map(extract_permid)
            plugins['registrator'] = plugins['registrator'].map(extract_person)
            plugins['registrationDate'] = plugins['registrationDate'].map(format_timestamp)
            plugins['description'] = plugins['description'].map(lambda x: '' if x is None else x)
            plugins['entityKinds'] = plugins['entityKinds'].map(lambda x: '' if x is None else x)

        return Things(
            openbis_obj = self,
            entity = 'plugin',
            df = plugins[attrs],
            identifier_name = 'name',
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
        )


    def get_plugin(self, permId, only_data=False, with_script=True):
        search_request = _type_for_id(permId, 'plugin')
        fetchopts = fetch_option['plugin']
        options = ['registrator']
        if with_script:
            options.append('script')

        for option in options:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "getPlugins",
            "params": [
                self.token,
                [search_request],
                fetchopts
            ],
        }

        resp = self._post_request(self.as_v3, request)
        parse_jackson(resp)

        if resp is None or len(resp) == 0:
            raise ValueError('no such plugin found: ' + permId)
        else:
            for permId in resp:
                if only_data:
                    return resp[permId]
                else:
                    return Plugin(self, data=resp[permId])

    def new_plugin(self, pluginType= "MANAGED_PROPERTY", pluginKind = "JYTHON", **kwargs):
        """ Note: not functional yet. Creates a new Plugin in openBIS. The attribute pluginKind must be one of
        the following:
        DYNAMIC_PROPERTY, MANAGED_PROPERTY, ENTITY_VALIDATION;

        Usage::
            o.new_plugin(
                name = 'name of plugin',
                description = '...',
                pluginType  = "ENTITY_VALIDATION",
                script      = "def a():\n  pass",
                available   = True,
                entityKind  = None
            )
        """

        if pluginType not in [
            'DYNAMIC_PROPERTY', 'MANAGED_PROPERTY', 'ENTITY_VALIDATION'
        ]:
            raise ValueError(
                "pluginType must be one of the following: DYNAMIC_PROPERTY, MANAGED_PROPERTY, ENTITY_VALIDATION")
        return Plugin(self, pluginType=pluginType, pluginKind=pluginKind, **kwargs) 

    
    def get_sample_types(self, type=None, start_with=None, count=None):
        """ Returns a list of all available sample types
        """
        return self._get_types_of(
            method_name         = "searchSampleTypes",
            entity              = "Sample",
            type_name           = type,
            optional_attributes = ["generatedCodePrefix"],
            start_with          = start_with,
            count               = count,
        )

    get_object_types = get_sample_types # Alias

    def get_sample_type(self, type):
        property_asignments = self._get_types_of(
            method_name         = "searchSampleTypes",
            entity              = "Sample",
            type_name           = type,
            optional_attributes = ["generatedCodePrefix", "validationPluginId"]
        )
        return SampleType(self, property_asignments.data)
    get_object_type = get_sample_type # Alias


    def get_experiment_types(self, type=None, start_with=None, count=None):
        """ Returns a list of all available experiment types
        """
        return self._get_types_of(
            method_name         = "searchExperimentTypes",
            entity              = "Experiment",
            type_name           = type,
            start_with          = start_with,
            count               = count,
        )
    get_collection_types = get_experiment_types  # Alias


    def get_experiment_type(self, type):
        try:
            return self._get_types_of(
                method_name     = "searchExperimentTypes",
                entity          = "Experiment",
                type_name       = type
            )
        except Exception:
           raise ValueError("No such experiment type: {}".format(type))
    get_collection_type = get_experiment_type  # Alias


    def get_material_types(self, type=None, start_with=None, count=None):
        """ Returns a list of all available material types
        """
        return self._get_types_of(
            method_name         = "searchMaterialTypes",
            entity              = "Material",
            type_name           = type,
            start_with          = start_with,
            count               = count,
        )

    def get_material_type(self, type):
        try:
            return self._get_types_of(
                method_name     = "searchMaterialTypes", 
                entity          = "Material", 
                type_name       = type
            ) 
        except Exception:
            raise ValueError("No such material type: {}".format(type))

    def get_dataset_types(self, type=None, start_with=None, count=None):
        """ Returns a list (DataFrame object) of all currently available dataset types
        """
        return self._get_types_of(
            "searchDataSetTypes", "DataSet", type,
            optional_attributes=['kind'],
            start_with=start_with,
            count=count,
        )

    def get_dataset_type(self, type):
        return self._get_types_of(
            method_name         = "searchDataSetTypes", 
            entity              = "DataSet",
            type_name           = type,
            optional_attributes = ['kind']
        )

    def _get_types_of(
        self, method_name, entity, type_name=None,
        start_with=None, count=None,
        additional_attributes=None, optional_attributes=None
    ):
        """ Returns a list of all available types of an entity.
        If the name of the entity-type is given, it returns a PropertyAssignments object
        """
        if additional_attributes is None:
            additional_attributes = []

        if optional_attributes is None:
            optional_attributes = []

        search_request = {
            "@type": "as.dto.{}.search.{}TypeSearchCriteria".format(
                entity.lower(), entity
            )
        }
        fetch_options = {
            "@type": "as.dto.{}.fetchoptions.{}TypeFetchOptions".format(
                entity.lower(), entity
            )
        }
        fetch_options['from'] = start_with
        fetch_options['count'] = count

        if type_name is not None:
            search_request = _gen_search_criteria({
                entity.lower(): entity + "Type",
                "operator": "AND",
                "code": type_name
            })
            fetch_options['propertyAssignments'] = fetch_option['propertyAssignments']
            if self.get_server_information().api_version > '3.3':
                fetch_options['validationPlugin'] = fetch_option['plugin']

        request = {
            "method": method_name,
            "params": [self.token, search_request, fetch_options],
        }
        resp = self._post_request(self.as_v3, request)
        parse_jackson(resp)

        if type_name is not None:
            if len(resp['objects']) == 1:
                return EntityType(
                    openbis_obj = self,
                    data        = resp['objects'][0]
                )
            elif len(resp['objects']) == 0:
                raise ValueError("No such {} type: {}".format(entity, type_name))
            else:
                raise ValueError("There is more than one entry for entity={} and type={}".format(entity, type_name))

        types = []
        attrs = self._get_attributes(type_name, types, additional_attributes, optional_attributes)
        if len(resp['objects']) == 0:
            types = DataFrame(columns=attrs)
        else:
            objects = resp['objects']
            parse_jackson(objects)
            types = DataFrame(objects)
            types['modificationDate'] = types['modificationDate'].map(format_timestamp)
        return Things(
            openbis_obj = self,
            entity = entity.lower() + '_type',
            df = types[attrs],
            start_with = start_with,
            count = count,
            totalCount = resp.get('totalCount'),
        )


    def _get_attributes(self, type_name, types, additional_attributes, optional_attributes):
        attributes = ['code', 'description'] + additional_attributes
        attributes += [attribute for attribute in optional_attributes if attribute in types]
        attributes += ['modificationDate']
        if type_name is not None:
            attributes += ['propertyAssignments']
        return attributes

    def is_session_active(self):
        """ checks whether a session is still active. Returns true or false.
        """
        return self.is_token_valid(self.token)

    def is_token_valid(self, token=None):
        """Check if the connection to openBIS is valid.
        This method is useful to check if a token is still valid or if it has timed out,
        requiring the user to login again.
        :return: Return True if the token is valid, False if it is not valid.
        """
        if token is None:
            token = self.token

        if token is None:
            return False

        request = {
            "method": "isSessionActive",
            "params": [token],
        }
        try:
            resp = self._post_request(self.as_v1, request)
        except Exception as e:
            return False

        return resp


    def get_dataset(self, permIds, only_data=False, props=None):
        """fetch a dataset and some metadata attached to it:
        - properties
        - sample
        - parents
        - children
        - containers
        - dataStore
        - physicalData
        - linkedData
        :return: a DataSet object
        """

        just_one = True
        identifiers = []
        if isinstance(permIds, list):
            just_one = False
            for permId in permIds:
                identifiers.append(
                    _type_for_id(permId, 'dataset')
                )
        else:
            identifiers.append(
                _type_for_id(permIds, 'dataset')
            )

        fetchopts = fetch_option['dataSet']

        for option in ['tags', 'properties', 'dataStore', 'physicalData', 'linkedData',
                       'experiment', 'sample', 'registrator', 'modifier']:
            fetchopts[option] = fetch_option[option]

        request = {
            "method": "getDataSets",
            "params": [
                self.token,
                identifiers,
                fetchopts,
            ],
        }

        resp = self._post_request(self.as_v3, request)
        if just_one:
            if len(resp) == 0:
                raise ValueError('no such dataset found: {}'.format(permIds))

            parse_jackson(resp)

            for permId in resp:
                if only_data:
                    return resp[permId]
                else:
                    return DataSet(
                        openbis_obj = self,
                        type = self.get_dataset_type(resp[permId]["type"]["code"]),
                        data = resp[permId]
                    )
        else:
            return self._dataset_list_for_response(response=list(resp.values()), props=props)


    def _dataset_list_for_response(
        self, response, props=None, 
        start_with=None, count=None, totalCount=0
    ):
        """returns a Things object, containing a DataFrame plus some additional information
        """

        parse_jackson(response)
        attrs = ['permId', 'type', 'experiment', 'sample',
                 'registrationDate', 'modificationDate',
                 'location', 'status', 'presentInArchive', 'size',
                 'properties'
                ]
        if len(response) == 0:
            datasets = DataFrame(columns=attrs)
        else:
            datasets = DataFrame(response)
            datasets['registrationDate'] = datasets['registrationDate'].map(format_timestamp)
            datasets['modificationDate'] = datasets['modificationDate'].map(format_timestamp)
            datasets['experiment'] = datasets['experiment'].map(extract_nested_identifier)
            datasets['sample'] = datasets['sample'].map(extract_nested_identifier)
            datasets['type'] = datasets['type'].map(extract_code)
            datasets['permId'] = datasets['code']
            datasets['size'] = datasets['physicalData'].map(lambda x: x.get('size') if x else '')
            datasets['status'] = datasets['physicalData'].map(lambda x: x.get('status') if x else '')
            datasets['presentInArchive'] = datasets['physicalData'].map(lambda x: x.get('presentInArchive') if x else '')
            datasets['location'] = datasets['physicalData'].map(lambda x: x.get('location') if x else '')

        if props is not None:
            if isinstance(props, str):
                props = [props]
            for prop in props:
                datasets[prop.upper()] = datasets['properties'].map(lambda x: x.get(prop.upper(), ''))
                attrs.append(prop.upper())

        return Things(
            openbis_obj = self,
            entity = 'dataset',
            df = datasets[attrs],
            identifier_name = 'permId',
            start_with=start_with,
            count=count,
            totalCount=totalCount,
        )


    def get_sample(self, sample_ident, only_data=False, withAttachments=False, props=None):
        """Retrieve metadata for the sample.
        Get metadata for the sample and any directly connected parents of the sample to allow access
        to the same information visible in the ELN UI. The metadata will be on the file system.
        :param sample_identifiers: A list of sample identifiers to retrieve.
        """

        just_one = True
        identifiers = []
        if isinstance(sample_ident, list):
            just_one = False
            for ident in sample_ident:
                identifiers.append(
                    _type_for_id(ident, 'sample')
                )
        else:
            identifiers.append(
                _type_for_id(sample_ident, 'sample')
            )

        fetchopts = {"type": {"@type": "as.dto.sample.fetchoptions.SampleTypeFetchOptions"}}

        options = ['tags', 'properties', 'attachments', 'space', 'experiment', 'registrator', 'modifier', 'dataSets']
        if self.get_server_information().project_samples_enabled:
            options.append('project')
        for option in options:
            fetchopts[option] = fetch_option[option]

        if withAttachments:
            fetchopts['attachments'] = fetch_option['attachmentsWithContent']

        for key in ['parents','children','container','components']:
            fetchopts[key] = {"@type": "as.dto.sample.fetchoptions.SampleFetchOptions"}

        request = {
            "method": "getSamples",
            "params": [
                self.token,
                identifiers,
                fetchopts
            ],
        }

        resp = self._post_request(self.as_v3, request)

        if just_one:
            if len(resp) == 0:
                raise ValueError('no such sample found: {}'.format(sample_ident))

            parse_jackson(resp)
            for sample_ident in resp:
                if only_data:
                    return resp[sample_ident]
                else:
                    return Sample(
                        openbis_obj = self,
                        type = self.get_sample_type(resp[sample_ident]["type"]["code"]),
                        data = resp[sample_ident]
                    )
        else:
            return self._sample_list_for_response(
                response=list(resp.values()),
                props=props,
            )

    def _sample_list_for_response(
        self, response, props=None,
        start_with=None, count=None, totalCount=0
    ):
        """returns a Things object, containing a DataFrame plus some additional information
        """

        parse_jackson(response)
        attrs = ['identifier', 'permId', 'experiment', 'sample_type',
                 'registrator', 'registrationDate', 'modifier', 'modificationDate']
        if len(response) == 0:
            samples = DataFrame(columns=attrs)
        else:
            samples = DataFrame(response)
            samples['registrationDate'] = samples['registrationDate'].map(format_timestamp)
            samples['modificationDate'] = samples['modificationDate'].map(format_timestamp)
            samples['registrator'] = samples['registrator'].map(extract_person)
            samples['modifier'] = samples['modifier'].map(extract_person)
            samples['identifier'] = samples['identifier'].map(extract_identifier)
            samples['permId'] = samples['permId'].map(extract_permid)
            samples['experiment'] = samples['experiment'].map(extract_nested_identifier)
            samples['sample_type'] = samples['type'].map(extract_nested_permid)

        if props is not None:
            if isinstance(props, str):
                props = [props]
            for prop in props:
                samples[prop.upper()] = samples['properties'].map(lambda x: x.get(prop.upper(), ''))
                attrs.append(prop.upper())

        return Things(
            openbis_obj = self,
            entity = 'sample',
            df = samples[attrs],
            identifier_name = 'identifier',
            start_with=start_with,
            count=count,
            totalCount=totalCount,
        )


    get_object = get_sample # Alias


    def get_external_data_management_system(self, permId, only_data=False):
        """Retrieve metadata for the external data management system.
        :param permId: A permId for an external DMS.
        :param only_data: Return the result data as a hash-map, not an object.
        """

        request = {
            "method": "getExternalDataManagementSystems",
            "params": [
                self.token,
                [{
                    "@type": "as.dto.externaldms.id.ExternalDmsPermId",
                    "permId": permId
                }],
                {
                    "@type": "as.dto.externaldms.fetchoptions.ExternalDmsFetchOptions",
                },
            ],
        }

        resp = self._post_request(self.as_v3, request)
        parse_jackson(resp)

        if resp is None or len(resp) == 0:
            raise ValueError('no such external DMS found: ' + permId)
        else:
            for ident in resp:
                if only_data:
                    return resp[ident]
                else:
                    return ExternalDMS(self, resp[ident])

    def new_space(self, **kwargs):
        """ Creates a new space in the openBIS instance.
        """
        return Space(self, None, **kwargs)


    def new_git_data_set(self, data_set_type, path, commit_id, repository_id, dms, sample=None, experiment=None, properties={},
                         dss_code=None, parents=None, data_set_code=None, contents=[]):
        """ Create a link data set.
        :param data_set_type: The type of the data set
        :param data_set_type: The type of the data set
        :param path: The path to the git repository
        :param commit_id: The git commit id
        :param repository_id: The git repository id - same for copies
        :param dms: An external data managment system object or external_dms_id
        :param sample: A sample object or sample id.
        :param dss_code: Code for the DSS -- defaults to the first dss if none is supplied.
        :param properties: Properties for the data set.
        :param parents: Parents for the data set.
        :param data_set_code: A data set code -- used if provided, otherwise generated on the server
        :param contents: A list of dicts that describe the contents:
            {'file_length': [file length],
             'crc32': [crc32 checksum],
             'directory': [is path a directory?]
             'path': [the relative path string]}
        :return: A DataSet object
        """
        return pbds.GitDataSetCreation(self, data_set_type, path, commit_id, repository_id, dms, sample, experiment,
                                       properties, dss_code, parents, data_set_code, contents).new_git_data_set()

    def new_content_copy(self, path, commit_id, repository_id, edms_id, data_set_id):
        """
        Create a content copy in an existing link data set.
        :param path: path of the new content copy
        "param commit_id: commit id of the new content copy
        "param repository_id: repository id of the content copy
        "param edms_id: Id of the external data managment system of the content copy
        "param data_set_id: Id of the data set to which the new content copy belongs
        """
        return pbds.GitDataSetUpdate(self, data_set_id).new_content_copy(path, commit_id, repository_id, edms_id)

    def search_files(self, data_set_id, dss_code=None):
        return pbds.GitDataSetFileSearch(self, data_set_id).search_files()        

    def delete_content_copy(self, data_set_id, content_copy):
        """
        Deletes a content copy from a data set.
        :param data_set_id: Id of the data set containing the content copy
        :param content_copy: The content copy to be deleted
        """
        return pbds.GitDataSetUpdate(self, data_set_id).delete_content_copy(content_copy)        

    @staticmethod
    def sample_to_sample_id(sample):
        """Take sample which may be a string or object and return an identifier for it."""
        return Openbis._object_to_object_id(sample, "as.dto.sample.id.SampleIdentifier", "as.dto.sample.id.SamplePermId");

    @staticmethod
    def experiment_to_experiment_id(experiment):
        """Take experiment which may be a string or object and return an identifier for it."""
        return Openbis._object_to_object_id(experiment, "as.dto.experiment.id.ExperimentIdentifier", "as.dto.experiment.id.SamplePermId");

    @staticmethod
    def _object_to_object_id(obj, identifierType, permIdType):
        object_id = None
        if isinstance(obj, str):
            if (is_identifier(obj)):
                object_id = {
                    "identifier": obj,
                    "@type": identifierType
                }
            else:
                object_id = {
                    "permId": obj,
                    "@type": permIdType
                }
        else:
            object_id = {
                "identifier": obj.identifier,
                "@type": identifierType
            }
        return object_id

    @staticmethod
    def data_set_to_data_set_id(data_set):
        if isinstance(data_set, str):
            code = data_set
        else:
            code = data_set.permId
        return {
            "permId": code,
            "@type": "as.dto.dataset.id.DataSetPermId"
        }

    def external_data_managment_system_to_dms_id(self, dms):
        if isinstance(dms, str):
            dms_id = {
                "permId": dms,
                "@type": "as.dto.externaldms.id.ExternalDmsPermId"
            }
        else:
            dms_id = {
                "identifier": dms.code,
                "@type": "as.dto.sample.id.SampleIdentifier"
            }
        return dms_id

    def new_sample(self, type, project=None, props=None, **kwargs):
        """ Creates a new sample of a given sample type.
        """
        if 'collection' in kwargs:
            kwargs['experiment'] = kwargs['collection']
            kwargs.pop('collection', None)
        return Sample(self, type=self.get_sample_type(type), project=project, data=None, props=props, **kwargs)

    new_object = new_sample # Alias

    def new_dataset(self, type=None, kind='PHYSICAL_DATA', files=None, props=None, folder=None, **kwargs):
        """ Creates a new dataset of a given sample type.
        """

        type_obj = self.get_dataset_type(type.upper())
        if 'object' in kwargs:
            kwargs['sample'] = kwargs['object']
            kwargs.pop('object', None)
        if 'collection' in kwargs:
            kwargs['experiment'] = kwargs['collection']
            kwargs.pop('collection', None)

        return DataSet(self, type=type_obj, kind=kind, files=files, folder=folder, props=props, **kwargs)
    
    def new_semantic_annotation(self, entityType=None, propertyType=None, **kwargs):
        """ Note: not functional yet. """
        return SemanticAnnotation(
            openbis_obj=self, isNew=True,
            entityType=entityType, propertyType=propertyType, **kwargs
        )    

    def new_vocabulary(self, code, terms, managedInternally=False, internalNameSpace=False, chosenFromList=True, **kwargs):
        """ Creates a new vocabulary
        Usage::
            new_vocabulary(
                code = 'vocabulary_code',
                description = '',
                terms = [
                    { "code": "term1", "label": "label1", "description": "description1" },
                    { "code": "term2", "label": "label2", "description": "description2" },
                ]
            )
        """
        kwargs['code'] = code
        kwargs['managedInternally'] = managedInternally
        kwargs['internalNameSpace'] = internalNameSpace
        kwargs['chosenFromList'] = chosenFromList
        return Vocabulary(self, data=None, terms=terms, **kwargs)

        

    def _get_dss_url(self, dss_code=None):
        """ internal method to get the downloadURL of a datastore.
        """
        dss = self.get_datastores()
        if dss_code is None:
            return dss['downloadUrl'][0]
        else:
            return dss[dss['code'] == dss_code]['downloadUrl'][0]



class ExternalDMS():
    """ managing openBIS external data management systems
    """

    def __init__(self, openbis_obj, data=None, **kwargs):
        self.__dict__['openbis'] = openbis_obj

        if data is not None:
            self.__dict__['data'] = data

        if kwargs is not None:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def __getattr__(self, name):
        return self.__dict__['data'].get(name)

    def __dir__(self):
        """all the available methods and attributes that should be displayed
        when using the autocompletion feature (TAB) in Jupyter
        """
        return ['code', 'label', 'urlTemplate', 'address', 'addressType', 'openbis']

    def __str__(self):
        return self.data.get('code', None)


class ServerInformation():
    
    def __init__(self, info):
        self._info = info
        self.attrs = [
            'api_version', 'archiving_configured', 'authentication_service',
            'enabled_technologies', 'project_samples_enabled'
        ]

    def __dir__(self):
        return self.attrs

    def __getattr__(self, name):
        return self._info.get(name.replace('_', '-'))
    
    def get_major_version(self):
        return int(self._info["api-version"].split(".")[0]);
    
    def get_minor_version(self):
        return int(self._info["api-version"].split(".")[1]);
    
    def is_openbis_1605(self):
        return (self.get_major_version() == 3) and (self.get_minor_version() <= 2);
    
    def is_openbis_1806(self):
        return (self.get_major_version() == 3) and (self.get_minor_version() >= 5);

    def _repr_html_(self):
        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>attribute</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        for attr in self.attrs:
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                attr, getattr(self, attr, '')
            )

        html += """
            </tbody>
            </table>
        """
        return html
