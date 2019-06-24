#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


# This file is part of Linshare api.
#
# LinShare api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinShare api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare api.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


from __future__ import unicode_literals

import urllib2
import urllib
import os
import datetime
import poster

from linshareapi.core import ResourceBuilder
from linshareapi.core import LinShareException
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time
from linshareapi.admin.core import Cache


class MailAttachments(GenericClass):
    """MailAttachments"""

    # Mandatory: define the base api for the REST resource
    local_base_url = "mail_attachments"
    cache = {"familly": "mail_attachments"}

    def get_rbu(self):
        rbu = ResourceBuilder("mail_attachments")
        rbu.add_field('uuid')
        rbu.add_field('name')
        rbu.add_field('cid')
        rbu.add_field('enable', value="True")
        rbu.add_field('enableForAll', value="True")
        rbu.add_field('language')
        rbu.add_field('description')
        rbu.add_field('mailConfig', extended=True)
        return rbu

    @Time('list')
    @Cache(discriminant=True)
    def list(self, config_uuid):
        # pylint: disable=arguments-differ
        url = "{base}".format(
            base=self.local_base_url
        )
        param = {}
        param['configUuid'] = config_uuid
        encode = urllib.urlencode(param)
        if encode:
            url += "?"
            url += encode
        return self.core.list(url)

    @Time('create')
    def create(self, file_path, mp_params, file_name=None):
        self.last_req_time = None
        url = "{base}".format(
            base=self.local_base_url
        )
        url = self.core.get_full_url(url)
        self.log.debug("upload url : " + url)
        # Generating datas and headers
        file_size = os.path.getsize(file_path)
        self.log.debug("file_path is : " + file_path)
        if not file_name:
            file_name = os.path.basename(file_path)
        self.log.debug("file_name is : " + file_name)
        if file_size <= 0:
            msg = "The file '%(filename)s' can not be uploaded because its size is less or equal to zero." % {"filename": str(file_name)}
            raise LinShareException("-1", msg)
        stream = file(file_path, 'rb')
        post = poster.encode.MultipartParam(
            "file",
            filename=file_name,
            fileobj=stream
        )
        params = [
            post,
            ("filesize", file_size),
        ]
        for field, value in mp_params.items():
            if value is not None:
                if field == "mailConfig":
                    params.append(("mail_config", value))
                else:
                    params.append((field, value))
        datagen, headers = poster.encode.multipart_encode(params)
        # Building request
        request = urllib2.Request(url, datagen, headers)
        request.add_header('Accept', 'application/json')
        request.get_method = lambda: 'POST'
        # request start
        starttime = datetime.datetime.now()
        resultq = None
        try:
            # doRequest
            resultq = urllib2.urlopen(request)
            code = resultq.getcode()
            self.log.debug("http return code : " + str(code))
            if code == 200:
                json_obj = self.core.get_json_result(resultq)
        except urllib2.HTTPError as ex:
            msg = ex.msg.decode('unicode-escape').strip('"')
            if self.core.verbose:
                self.log.info(
                    "Http error : " + msg + " (" + str(ex.code) + ")")
            else:
                self.log.debug(
                    "Http error : " + msg + " (" + str(ex.code) + ")")
            json_obj = self.core.get_json_result(ex)
            code = json_obj.get('errCode')
            msg = json_obj.get('message')
            self.log.debug("Server error code : " + str(code))
            self.log.debug("Server error message : " + str(msg))
            # request end
            endtime = datetime.datetime.now()
            self.last_req_time = str(endtime - starttime)
            self.log.debug(
                "Can not upload file %(filename)s (%(filepath)s)",
                {
                    "filename": file_name,
                    "filepath": file_path
                }
            )
            raise LinShareException(code, msg)
        # request end
        endtime = datetime.datetime.now()
        self.last_req_time = str(endtime - starttime)
        self.log.debug(
            "upload url : %(url)s : request time : %(time)s",
            {
                "url": url,
                "time": self.last_req_time
            }
        )
        return json_obj
