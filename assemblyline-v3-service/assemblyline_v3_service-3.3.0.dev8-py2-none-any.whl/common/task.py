#!/usr/bin/env python

import os
import shutil

from easydict import EasyDict

from alv3_service.common import identify
from alv3_service.common.isotime import now_as_iso


class Task(object):
    """Task objects are an abstraction layer over a task (dict) received from the dispatcher"""

    def __init__(self, task):
        self.original_task = task
        self.classification = None
        self.deep_scan = False
        self.depth = task['depth']
        self.drop_file = False
        self.error_message = None
        self.error_status = None
        self.extracted = []
        self.max_extracted = task['max_files']
        self.max_supplementary = task['max_files']
        self.md5 = task['fileinfo']['md5']
        self.milestones = {}
        self.oversized = False
        self.result = {}
        self.score = 0
        self.service_config = task['service_config']
        self.service_context = None
        self.service_name = None
        self.service_version = None
        self.service_tool_version = None
        self.sha1 = task['fileinfo']['sha1']
        self.sha256 = task['fileinfo']['sha256']
        self.sid = task['sid']
        self.size = task['fileinfo']['size']
        self.supplementary = []
        self.tag = task['fileinfo']['type']
        self.ttl = task['ttl']

    def add_child(self, original_path, new_path, name, description, classification):
        return EasyDict({'original_path': original_path,
                         'new_path': new_path,
                         'display_name': name,
                         'description': description,
                         'classification': classification,
                         })

    def add_extracted(self, original_path, new_path, description, name, classification):
        if original_path is None:
            return False
        if self.extracted is None:
            self.clear_extracted()
        limit = self.max_extracted
        if limit and len(self.extracted) >= int(limit):
            return False
        if not classification:
            classification = self.classification

        self.extracted.append(self.add_child(original_path, new_path, name, description, classification))
        return True

    def add_supplementary(self, original_path, new_path, description, name, classification):
        if original_path is None:
            return False
        if self.supplementary is None:
            self.clear_supplementary()
        limit = self.max_supplementary
        if limit and len(self.supplementary) >= int(limit):
            return False
        if not classification:
            classification = self.classification

        self.supplementary.append(self.add_child(original_path, new_path, name, description, classification))
        return True

    def as_service_error(self):
        response = {
            'message': self.error_message,
            'service_name': self.service_name,
            'service_version': self.service_version,
            'service_tool_version': self.service_tool_version or 'empty',
            'status': self.error_status
        }

        expiry_ts = now_as_iso(self.ttl * 24 * 60 * 60)

        return {
            'expiry_ts': expiry_ts,
            'response': response,
            'sha256': self.sha256,
            'type': "EXCEPTION"
        }

    def as_service_result(self):
        if not self.extracted:
            self.extracted = []
        if not self.supplementary:
            self.supplementary = []
        if not self.result:
            self.result = []

        expiry_ts = now_as_iso(self.ttl * 24 * 60 * 60)

        response = {
            'extracted': self.extracted,
            'milestones': self.milestones,
            'service_context': self.service_context,
            'service_name': self.service_name,
            'service_version': self.service_version,
            'service_tool_version': self.service_tool_version or 'empty',
            'supplementary': self.supplementary
        }

        return {
            'classification': self.classification,
            'drop_file': self.drop_file,
            'expiry_ts': expiry_ts,
            'oversized': self.oversized, # TODO
            'response': response,
            'result': self.result,
            'sha256': self.sha256
        }

    def clear_extracted(self):
        self.extracted = []

    def clear_supplementary(self):
        self.supplementary = []

    def drop(self):
        self.drop_file = True

    def is_initial(self):
        return self.depth == 0

    def set_milestone(self, name, value):
        if not self.milestones:
            self.milestones = {}
        self.milestones[name] = value

    def success(self):
        self.finalize_extracted_supplementary()

        # Assign aggregate classification for the result based on max classification of tags and result sections
        self.classification = self.result['classification']
        del self.result['classification']

        for item in range(len(self.extracted)):
            self.extracted[item]['name'] = self.extracted[item]['display_name']
            del self.extracted[item]['display_name']

        for item in range(len(self.supplementary)):
            self.supplementary[item]['name'] = self.supplementary[item]['display_name']
            del self.extracted[item]['display_name']

            # TODO: self.score not used for anything right now
        self.score = 0
        if self.result:
            try:
                self.score = int(self.result.get('score', 0))
            except:
                self.score = 0

    def report_service_context(self, context):
        if not isinstance(context, basestring):
            raise TypeError('Expected string got %s', type(context))
        self.service_context = context

    def watermark(self, service_name, service_version, service_tool_version):
        self.service_name = service_name
        self.service_version = service_version
        self.service_tool_version = service_tool_version

    def get_service_params(self, service_name):
        if not service_name or not self.service_config:
            return {}

        return self.service_config.get(service_name, {})

    def get_submission_tags_name(self):
        return "st/%s".format(self.sha256)

    def finalize_extracted_supplementary(self):
        for item in range(len(self.extracted)):
            # self.extracted[item]['name'] = self.extracted[item].pop('display_name')
            # Move file to working directory for compatibility with ALv4
            folder_path = os.path.dirname(self.extracted[item]['new_path'])
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            if not os.path.exists(self.extracted[item]['new_path']):
                shutil.move(self.extracted[item]['original_path'], self.extracted[item]['new_path'])

            file_info = identify.fileinfo(self.extracted[item]['new_path'])
            self.extracted[item]['sha256'] = file_info['sha256']

            del self.extracted[item]['new_path']
            del self.extracted[item]['original_path']

        for item in range(len(self.supplementary)):
            # self.supplementary[item]['name'] = self.supplementary[item].pop('display_name')
            # Move file to working directory for compatibility with ALv4
            folder_path = os.path.dirname(self.supplementary[item]['new_path'])
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            if not os.path.exists(self.supplementary[item]['new_path']):
                shutil.move(self.supplementary[item]['original_path'], self.supplementary[item]['new_path'])

            file_info = identify.fileinfo(self.supplementary[item]['new_path'])
            self.supplementary[item]['sha256'] = file_info['sha256']

            del self.supplementary[item]['new_path']
            del self.supplementary[item]['original_path']
