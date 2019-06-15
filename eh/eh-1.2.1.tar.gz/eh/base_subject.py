# coding: utf-8
# Copyright (c) 2016 Justin L. Hammond
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import os 

import mdv

class BaseSubject(object):

    def __init__(self):
        #reload(sys); sys.setdefaultencoding('utf-8')
        self._subjects = {}
        self._parents = {}

    @property
    def subjects(self):
        return self._subjects.keys()

    @property
    def parents(self):
        return self._parents.keys()

    def get_children_for_parent(self, parent):
        return self._parents[parent].keys()

    def has_parent(self, parent_key):
        return parent_key in self._parents.keys()

    def comment_is_valid_format(self, comment):
        if '[//]' not in comment or '#' not in comment:
            return False
        pound_split = [x.strip() for x in comment.split('#')]
        if len(pound_split) != 2:
            return False
        paren_side = pound_split[1]
        if paren_side.count('(') != 1 or paren_side.count(')') != 1:
            return False
        if paren_side[:1] != '(' or paren_side[-1] != ')':
            return False
        return True

    def _pull_subjects_from_md_comment(self, comment):
        if not self.comment_is_valid_format(comment):
            return []
        paren_side = [x.strip() for x in comment.split('#')][1]
        comment_internal = paren_side[1:len(paren_side)-1]
        return [x.strip() for x in comment_internal.split(',')]

    def _create_subject_dict_with_file(self, file):
        out = {}
        with open(file, 'r') as myfile:
            data = myfile.read().splitlines()
            top_line = data.pop(0)
            if '[//]' in top_line:  # using comment format
                subjects = self._pull_subjects_from_md_comment(top_line)
            else:
                subjects = [x.strip() for x in top_line.split(',')]
            if not subjects:
                return None
            full_text = "\n".join(data)
            for subject in subjects:
                out[subject] = full_text
        return out

    def _get_subjects_in_parent(self, path, full_parent_path):
        subs = self._gather_subjects(full_parent_path, in_parent=True)
        for child, text in subs.items():
            self._parents[path][child] = text
        return subs

    def _get_parent_fulltext(self, path, full_parent_path):
        children = self._get_subjects_in_parent(path, full_parent_path)
        out = ["%s has more detailed subjects:" % path]
        for subject, text in children.items():
            out.append("- %s" % subject)
        return "\n".join(out)

    def _gather_subjects(self, target_path, in_parent=False):
        file_paths = []
        out = {}
        for file in os.listdir(target_path):
            if file.endswith(".md"):
                file_paths.append(os.path.join(target_path, file))
        for file in file_paths:
            s = self._create_subject_dict_with_file(file)
            if not s:
                continue
            out.update(s)
        if in_parent:
            return out
        for path in os.listdir(target_path):
            if os.path.isdir(os.path.join(target_path, path)):
                # path is a directory, and also the parent subject key
                self._parents[path] = {}
                parent_path = os.path.join(target_path, path)
                out[path] = self._get_parent_fulltext(path, parent_path)
        return out

    def populate_subjects(self, target_path):
        self._subjects = self._gather_subjects(target_path)

    def get_childsubject_unformatted(self, parent, subject):
        pre_md = self._parents[parent][subject]
        return pre_md

    def get_subject_unformatted(self, subject):
        pre_md = self._subjects[subject]
        return pre_md

    @staticmethod
    def md_output(subject, text, no_colors=False):
        pre_md = "Reminding you about **%s**\n%s" % (subject, text)
        md = mdv.main(pre_md, no_colors=no_colors)
        lines = md.splitlines()
        lines = [line for line in lines if line.strip()]
        return "\n".join(lines)

    def output(self, subject, text="", no_colors=False):
        if subject not in self.subjects:
            return None
        pre_md = self._subjects[subject]
        if text:
            pre_md = text
        pre_md = "Reminding you about **%s**\n%s" % (subject, pre_md)
        md = mdv.main(pre_md, no_colors=no_colors)
        lines = md.splitlines()
        lines = [line for line in lines if line.strip()]
        return "\n".join(lines)
