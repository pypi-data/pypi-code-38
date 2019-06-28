# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose">
#   Copyright (c) 2018 Aspose.Slides for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from asposeslidescloud.apis.api_base import ApiBase
from asposeslidescloud.api_client import ApiClient

class SlidesApi(ApiBase):

    def __init__(self, configuration = None, app_sid = None, app_key = None):
        super(SlidesApi, self).__init__(configuration, app_sid, app_key)

    def copy_file(self, request, **kwargs):  # noqa: E501
        """Copy file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.copy_file(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param copy_fileRequest request: copy_file request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.copy_file_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.copy_file_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def copy_file_with_http_info(self, request, **kwargs):  # noqa: E501
        """Copy file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.copy_file_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param copy_fileRequest request: copy_file request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method copy_file" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'src_path' is set
        if not request.src_path:
            raise ValueError("Missing the required parameter `request.src_path` when calling `copy_file`")  # noqa: E501
        # verify the required parameter 'dest_path' is set
        if not request.dest_path:
            raise ValueError("Missing the required parameter `request.dest_path` when calling `copy_file`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['srcPath'] = request.src_path  # noqa: E501

        query_params = []
        if request.dest_path:
            query_params.append(('destPath', request.dest_path))  # noqa: E501
        if request.src_storage_name:
            query_params.append(('srcStorageName', request.src_storage_name))  # noqa: E501
        if request.dest_storage_name:
            query_params.append(('destStorageName', request.dest_storage_name))  # noqa: E501
        if request.version_id:
            query_params.append(('versionId', request.version_id))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/file/copy/{srcPath}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def copy_folder(self, request, **kwargs):  # noqa: E501
        """Copy folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.copy_folder(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param copy_folderRequest request: copy_folder request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.copy_folder_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.copy_folder_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def copy_folder_with_http_info(self, request, **kwargs):  # noqa: E501
        """Copy folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.copy_folder_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param copy_folderRequest request: copy_folder request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method copy_folder" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'src_path' is set
        if not request.src_path:
            raise ValueError("Missing the required parameter `request.src_path` when calling `copy_folder`")  # noqa: E501
        # verify the required parameter 'dest_path' is set
        if not request.dest_path:
            raise ValueError("Missing the required parameter `request.dest_path` when calling `copy_folder`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['srcPath'] = request.src_path  # noqa: E501

        query_params = []
        if request.dest_path:
            query_params.append(('destPath', request.dest_path))  # noqa: E501
        if request.src_storage_name:
            query_params.append(('srcStorageName', request.src_storage_name))  # noqa: E501
        if request.dest_storage_name:
            query_params.append(('destStorageName', request.dest_storage_name))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/folder/copy/{srcPath}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def create_folder(self, request, **kwargs):  # noqa: E501
        """Create the folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.create_folder(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param create_folderRequest request: create_folder request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.create_folder_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.create_folder_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def create_folder_with_http_info(self, request, **kwargs):  # noqa: E501
        """Create the folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.create_folder_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param create_folderRequest request: create_folder request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method create_folder" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.storage_name:
            query_params.append(('storageName', request.storage_name))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/folder/{path}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_file(self, request, **kwargs):  # noqa: E501
        """Delete file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_file(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_fileRequest request: delete_file request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_file_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_file_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_file_with_http_info(self, request, **kwargs):  # noqa: E501
        """Delete file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_file_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_fileRequest request: delete_file request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_file" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.storage_name:
            query_params.append(('storageName', request.storage_name))  # noqa: E501
        if request.version_id:
            query_params.append(('versionId', request.version_id))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/file/{path}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_folder(self, request, **kwargs):  # noqa: E501
        """Delete folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_folder(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_folderRequest request: delete_folder request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_folder_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_folder_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_folder_with_http_info(self, request, **kwargs):  # noqa: E501
        """Delete folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_folder_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_folderRequest request: delete_folder request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_folder" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.storage_name:
            query_params.append(('storageName', request.storage_name))  # noqa: E501
        if request.recursive:
            query_params.append(('recursive', request.recursive))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/folder/{path}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_notes_slide(self, request, **kwargs):  # noqa: E501
        """Remove notes slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slideRequest request: delete_notes_slide request object
        :return: Slide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_notes_slide_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_notes_slide_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_notes_slide_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove notes slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slideRequest request: delete_notes_slide request object
        :return: Slide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_notes_slide" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_notes_slide`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_notes_slide`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_notes_slide_paragraph(self, request, **kwargs):  # noqa: E501
        """Remove a paragraph.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_paragraph(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_paragraphRequest request: delete_notes_slide_paragraph request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_notes_slide_paragraph_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_notes_slide_paragraph_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_notes_slide_paragraph_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a paragraph.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_paragraph_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_paragraphRequest request: delete_notes_slide_paragraph request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_notes_slide_paragraph" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_notes_slide_paragraph`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_notes_slide_paragraph`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_notes_slide_paragraph`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `delete_notes_slide_paragraph`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraphs',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_notes_slide_paragraphs(self, request, **kwargs):  # noqa: E501
        """Remove a range of paragraphs.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_paragraphs(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_paragraphsRequest request: delete_notes_slide_paragraphs request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_notes_slide_paragraphs_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_notes_slide_paragraphs_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_notes_slide_paragraphs_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a range of paragraphs.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_paragraphs_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_paragraphsRequest request: delete_notes_slide_paragraphs request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_notes_slide_paragraphs" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_notes_slide_paragraphs`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_notes_slide_paragraphs`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_notes_slide_paragraphs`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.paragraphs:
            query_params.append(('paragraphs', request.paragraphs))  # noqa: E501
            collection_formats['paragraphs'] = ''  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraphs',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_notes_slide_portion(self, request, **kwargs):  # noqa: E501
        """Remove a portion.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_portion(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_portionRequest request: delete_notes_slide_portion request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_notes_slide_portion_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_notes_slide_portion_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_notes_slide_portion_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a portion.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_portion_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_portionRequest request: delete_notes_slide_portion request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_notes_slide_portion" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_notes_slide_portion`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_notes_slide_portion`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_notes_slide_portion`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `delete_notes_slide_portion`")  # noqa: E501
        # verify the required parameter 'portion_index' is set
        if not request.portion_index:
            raise ValueError("Missing the required parameter `request.portion_index` when calling `delete_notes_slide_portion`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501
        path_params['portionIndex'] = request.portion_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions/{portionIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portions',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_notes_slide_portions(self, request, **kwargs):  # noqa: E501
        """Remove a range of portions.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_portions(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_portionsRequest request: delete_notes_slide_portions request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_notes_slide_portions_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_notes_slide_portions_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_notes_slide_portions_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a range of portions.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_portions_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_portionsRequest request: delete_notes_slide_portions request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_notes_slide_portions" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_notes_slide_portions`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_notes_slide_portions`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_notes_slide_portions`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `delete_notes_slide_portions`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.portions:
            query_params.append(('portions', request.portions))  # noqa: E501
            collection_formats['portions'] = ''  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portions',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_notes_slide_shape(self, request, **kwargs):  # noqa: E501
        """Remove a shape.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_shape(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_shapeRequest request: delete_notes_slide_shape request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_notes_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_notes_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_notes_slide_shape_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a shape.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_shape_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_shapeRequest request: delete_notes_slide_shape request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_notes_slide_shape" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_notes_slide_shape`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_notes_slide_shape`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_notes_slide_shape`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Shapes',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_notes_slide_shapes(self, request, **kwargs):  # noqa: E501
        """Remove a range of shapes.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_shapes(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_shapesRequest request: delete_notes_slide_shapes request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_notes_slide_shapes_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_notes_slide_shapes_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_notes_slide_shapes_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a range of shapes.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_notes_slide_shapes_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_notes_slide_shapesRequest request: delete_notes_slide_shapes request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_notes_slide_shapes" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_notes_slide_shapes`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_notes_slide_shapes`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.shapes:
            query_params.append(('shapes', request.shapes))  # noqa: E501
            collection_formats['shapes'] = ''  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Shapes',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_paragraph(self, request, **kwargs):  # noqa: E501
        """Remove a paragraph.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_paragraph(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_paragraphRequest request: delete_paragraph request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_paragraph_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_paragraph_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_paragraph_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a paragraph.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_paragraph_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_paragraphRequest request: delete_paragraph request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_paragraph" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_paragraph`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_paragraph`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_paragraph`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `delete_paragraph`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraphs',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_paragraphs(self, request, **kwargs):  # noqa: E501
        """Remove a range of paragraphs.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_paragraphs(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_paragraphsRequest request: delete_paragraphs request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_paragraphs_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_paragraphs_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_paragraphs_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a range of paragraphs.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_paragraphs_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_paragraphsRequest request: delete_paragraphs request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_paragraphs" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_paragraphs`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_paragraphs`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_paragraphs`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.paragraphs:
            query_params.append(('paragraphs', request.paragraphs))  # noqa: E501
            collection_formats['paragraphs'] = ''  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraphs',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_portion(self, request, **kwargs):  # noqa: E501
        """Remove a portion.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_portion(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_portionRequest request: delete_portion request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_portion_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_portion_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_portion_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a portion.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_portion_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_portionRequest request: delete_portion request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_portion" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_portion`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_portion`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_portion`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `delete_portion`")  # noqa: E501
        # verify the required parameter 'portion_index' is set
        if not request.portion_index:
            raise ValueError("Missing the required parameter `request.portion_index` when calling `delete_portion`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501
        path_params['portionIndex'] = request.portion_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions/{portionIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portions',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_portions(self, request, **kwargs):  # noqa: E501
        """Remove a range of portions.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_portions(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_portionsRequest request: delete_portions request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_portions_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_portions_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_portions_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a range of portions.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_portions_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_portionsRequest request: delete_portions request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_portions" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_portions`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_portions`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_portions`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `delete_portions`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.portions:
            query_params.append(('portions', request.portions))  # noqa: E501
            collection_formats['portions'] = ''  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portions',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slide_animation(self, request, **kwargs):  # noqa: E501
        """Remove animation from a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animationRequest request: delete_slide_animation request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slide_animation_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slide_animation_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slide_animation_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove animation from a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animationRequest request: delete_slide_animation request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slide_animation" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slide_animation`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slide_animation`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slide_animation_effect(self, request, **kwargs):  # noqa: E501
        """Remove an effect from slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_effect(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_effectRequest request: delete_slide_animation_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slide_animation_effect_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slide_animation_effect_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slide_animation_effect_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove an effect from slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_effect_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_effectRequest request: delete_slide_animation_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slide_animation_effect" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slide_animation_effect`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slide_animation_effect`")  # noqa: E501
        # verify the required parameter 'effect_index' is set
        if not request.effect_index:
            raise ValueError("Missing the required parameter `request.effect_index` when calling `delete_slide_animation_effect`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['effectIndex'] = request.effect_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/mainSequence/{effectIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slide_animation_interactive_sequence(self, request, **kwargs):  # noqa: E501
        """Remove an interactive sequence from slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_interactive_sequence(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_interactive_sequenceRequest request: delete_slide_animation_interactive_sequence request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slide_animation_interactive_sequence_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slide_animation_interactive_sequence_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slide_animation_interactive_sequence_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove an interactive sequence from slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_interactive_sequence_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_interactive_sequenceRequest request: delete_slide_animation_interactive_sequence request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slide_animation_interactive_sequence" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slide_animation_interactive_sequence`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slide_animation_interactive_sequence`")  # noqa: E501
        # verify the required parameter 'sequence_index' is set
        if not request.sequence_index:
            raise ValueError("Missing the required parameter `request.sequence_index` when calling `delete_slide_animation_interactive_sequence`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['sequenceIndex'] = request.sequence_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/interactiveSequences/{sequenceIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slide_animation_interactive_sequence_effect(self, request, **kwargs):  # noqa: E501
        """Remove an effect from slide animation interactive sequence.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_interactive_sequence_effect(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_interactive_sequence_effectRequest request: delete_slide_animation_interactive_sequence_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slide_animation_interactive_sequence_effect_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slide_animation_interactive_sequence_effect_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slide_animation_interactive_sequence_effect_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove an effect from slide animation interactive sequence.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_interactive_sequence_effect_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_interactive_sequence_effectRequest request: delete_slide_animation_interactive_sequence_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slide_animation_interactive_sequence_effect" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slide_animation_interactive_sequence_effect`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slide_animation_interactive_sequence_effect`")  # noqa: E501
        # verify the required parameter 'sequence_index' is set
        if not request.sequence_index:
            raise ValueError("Missing the required parameter `request.sequence_index` when calling `delete_slide_animation_interactive_sequence_effect`")  # noqa: E501
        # verify the required parameter 'effect_index' is set
        if not request.effect_index:
            raise ValueError("Missing the required parameter `request.effect_index` when calling `delete_slide_animation_interactive_sequence_effect`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['sequenceIndex'] = request.sequence_index  # noqa: E501
        path_params['effectIndex'] = request.effect_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/interactiveSequences/{sequenceIndex}/{effectIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slide_animation_interactive_sequences(self, request, **kwargs):  # noqa: E501
        """Clear all interactive sequences from slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_interactive_sequences(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_interactive_sequencesRequest request: delete_slide_animation_interactive_sequences request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slide_animation_interactive_sequences_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slide_animation_interactive_sequences_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slide_animation_interactive_sequences_with_http_info(self, request, **kwargs):  # noqa: E501
        """Clear all interactive sequences from slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_interactive_sequences_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_interactive_sequencesRequest request: delete_slide_animation_interactive_sequences request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slide_animation_interactive_sequences" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slide_animation_interactive_sequences`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slide_animation_interactive_sequences`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/interactiveSequences', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slide_animation_main_sequence(self, request, **kwargs):  # noqa: E501
        """Clear main sequence in slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_main_sequence(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_main_sequenceRequest request: delete_slide_animation_main_sequence request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slide_animation_main_sequence_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slide_animation_main_sequence_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slide_animation_main_sequence_with_http_info(self, request, **kwargs):  # noqa: E501
        """Clear main sequence in slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_animation_main_sequence_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_animation_main_sequenceRequest request: delete_slide_animation_main_sequence request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slide_animation_main_sequence" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slide_animation_main_sequence`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slide_animation_main_sequence`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/mainSequence', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slide_by_index(self, request, **kwargs):  # noqa: E501
        """Delete a presentation slide by index.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_by_index(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_by_indexRequest request: delete_slide_by_index request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slide_by_index_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slide_by_index_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slide_by_index_with_http_info(self, request, **kwargs):  # noqa: E501
        """Delete a presentation slide by index.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_by_index_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_by_indexRequest request: delete_slide_by_index request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slide_by_index" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slide_by_index`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slide_by_index`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slides',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slide_shape(self, request, **kwargs):  # noqa: E501
        """Remove a shape.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_shape(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_shapeRequest request: delete_slide_shape request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slide_shape_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a shape.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_shape_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_shapeRequest request: delete_slide_shape request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slide_shape" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slide_shape`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slide_shape`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `delete_slide_shape`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Shapes',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slide_shapes(self, request, **kwargs):  # noqa: E501
        """Remove a range of shapes.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_shapes(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_shapesRequest request: delete_slide_shapes request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slide_shapes_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slide_shapes_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slide_shapes_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove a range of shapes.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slide_shapes_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slide_shapesRequest request: delete_slide_shapes request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slide_shapes" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slide_shapes`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slide_shapes`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.shapes:
            query_params.append(('shapes', request.shapes))  # noqa: E501
            collection_formats['shapes'] = ''  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Shapes',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slides_clean_slides_list(self, request, **kwargs):  # noqa: E501
        """Delete presentation slides.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slides_clean_slides_list(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slides_clean_slides_listRequest request: delete_slides_clean_slides_list request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slides_clean_slides_list_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slides_clean_slides_list_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slides_clean_slides_list_with_http_info(self, request, **kwargs):  # noqa: E501
        """Delete presentation slides.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slides_clean_slides_list_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slides_clean_slides_listRequest request: delete_slides_clean_slides_list request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slides_clean_slides_list" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slides_clean_slides_list`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.slides:
            query_params.append(('slides', request.slides))  # noqa: E501
            collection_formats['slides'] = ''  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slides',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slides_document_properties(self, request, **kwargs):  # noqa: E501
        """Clean document properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slides_document_properties(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slides_document_propertiesRequest request: delete_slides_document_properties request object
        :return: DocumentProperties
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slides_document_properties_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slides_document_properties_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slides_document_properties_with_http_info(self, request, **kwargs):  # noqa: E501
        """Clean document properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slides_document_properties_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slides_document_propertiesRequest request: delete_slides_document_properties request object
        :return: DocumentProperties
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slides_document_properties" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slides_document_properties`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/documentproperties', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='DocumentProperties',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slides_document_property(self, request, **kwargs):  # noqa: E501
        """Delete document property.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slides_document_property(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slides_document_propertyRequest request: delete_slides_document_property request object
        :return: DocumentProperties
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slides_document_property_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slides_document_property_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slides_document_property_with_http_info(self, request, **kwargs):  # noqa: E501
        """Delete document property.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slides_document_property_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slides_document_propertyRequest request: delete_slides_document_property request object
        :return: DocumentProperties
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slides_document_property" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slides_document_property`")  # noqa: E501
        # verify the required parameter 'property_name' is set
        if not request.property_name:
            raise ValueError("Missing the required parameter `request.property_name` when calling `delete_slides_document_property`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['propertyName'] = request.property_name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/documentproperties/{propertyName}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='DocumentProperties',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def delete_slides_slide_background(self, request, **kwargs):  # noqa: E501
        """Remove background from a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slides_slide_background(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slides_slide_backgroundRequest request: delete_slides_slide_background request object
        :return: SlideBackground
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.delete_slides_slide_background_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_slides_slide_background_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def delete_slides_slide_background_with_http_info(self, request, **kwargs):  # noqa: E501
        """Remove background from a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.delete_slides_slide_background_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param delete_slides_slide_backgroundRequest request: delete_slides_slide_background request object
        :return: SlideBackground
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_slides_slide_background" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `delete_slides_slide_background`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `delete_slides_slide_background`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/background', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideBackground',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def download_file(self, request, **kwargs):  # noqa: E501
        """Download file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.download_file(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param download_fileRequest request: download_file request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.download_file_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.download_file_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def download_file_with_http_info(self, request, **kwargs):  # noqa: E501
        """Download file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.download_file_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param download_fileRequest request: download_file request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method download_file" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.storage_name:
            query_params.append(('storageName', request.storage_name))  # noqa: E501
        if request.version_id:
            query_params.append(('versionId', request.version_id))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/file/{path}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_disc_usage(self, request, **kwargs):  # noqa: E501
        """Get disc usage  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_disc_usage(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_disc_usageRequest request: get_disc_usage request object
        :return: DiscUsage
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_disc_usage_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_disc_usage_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_disc_usage_with_http_info(self, request, **kwargs):  # noqa: E501
        """Get disc usage  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_disc_usage_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_disc_usageRequest request: get_disc_usage request object
        :return: DiscUsage
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_disc_usage" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if request.storage_name:
            query_params.append(('storageName', request.storage_name))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/disc', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='DiscUsage',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_file_versions(self, request, **kwargs):  # noqa: E501
        """Get file versions  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_file_versions(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_file_versionsRequest request: get_file_versions request object
        :return: FileVersions
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_file_versions_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_file_versions_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_file_versions_with_http_info(self, request, **kwargs):  # noqa: E501
        """Get file versions  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_file_versions_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_file_versionsRequest request: get_file_versions request object
        :return: FileVersions
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_file_versions" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.storage_name:
            query_params.append(('storageName', request.storage_name))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/version/{path}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='FileVersions',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_files_list(self, request, **kwargs):  # noqa: E501
        """Get all files and folders within a folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_files_list(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_files_listRequest request: get_files_list request object
        :return: FilesList
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_files_list_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_files_list_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_files_list_with_http_info(self, request, **kwargs):  # noqa: E501
        """Get all files and folders within a folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_files_list_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_files_listRequest request: get_files_list request object
        :return: FilesList
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_files_list" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.storage_name:
            query_params.append(('storageName', request.storage_name))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/folder/{path}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='FilesList',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_layout_slide(self, request, **kwargs):  # noqa: E501
        """Read presentation layoutSlide info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_layout_slide(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_layout_slideRequest request: get_layout_slide request object
        :return: LayoutSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_layout_slide_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_layout_slide_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_layout_slide_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation layoutSlide info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_layout_slide_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_layout_slideRequest request: get_layout_slide request object
        :return: LayoutSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_layout_slide" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_layout_slide`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_layout_slide`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/layoutSlides/{slideIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='LayoutSlide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_layout_slides_list(self, request, **kwargs):  # noqa: E501
        """Read presentation layoutSlides info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_layout_slides_list(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_layout_slides_listRequest request: get_layout_slides_list request object
        :return: LayoutSlides
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_layout_slides_list_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_layout_slides_list_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_layout_slides_list_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation layoutSlides info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_layout_slides_list_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_layout_slides_listRequest request: get_layout_slides_list request object
        :return: LayoutSlides
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_layout_slides_list" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_layout_slides_list`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/layoutSlides', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='LayoutSlides',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_master_slide(self, request, **kwargs):  # noqa: E501
        """Read presentation masterSlide info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_master_slide(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_master_slideRequest request: get_master_slide request object
        :return: MasterSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_master_slide_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_master_slide_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_master_slide_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation masterSlide info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_master_slide_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_master_slideRequest request: get_master_slide request object
        :return: MasterSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_master_slide" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_master_slide`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_master_slide`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/masterSlides/{slideIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='MasterSlide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_master_slides_list(self, request, **kwargs):  # noqa: E501
        """Read presentation masterSlides info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_master_slides_list(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_master_slides_listRequest request: get_master_slides_list request object
        :return: MasterSlides
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_master_slides_list_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_master_slides_list_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_master_slides_list_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation masterSlides info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_master_slides_list_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_master_slides_listRequest request: get_master_slides_list request object
        :return: MasterSlides
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_master_slides_list" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_master_slides_list`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/masterSlides', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='MasterSlides',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_notes_slide(self, request, **kwargs):  # noqa: E501
        """Read notes slide info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slideRequest request: get_notes_slide request object
        :return: NotesSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_notes_slide_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_notes_slide_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_notes_slide_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read notes slide info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slideRequest request: get_notes_slide request object
        :return: NotesSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_notes_slide" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_notes_slide`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_notes_slide`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='NotesSlide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_notes_slide_shape(self, request, **kwargs):  # noqa: E501
        """Read slide shape info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shapeRequest request: get_notes_slide_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_notes_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_notes_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_notes_slide_shape_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide shape info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shapeRequest request: get_notes_slide_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_notes_slide_shape" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_notes_slide_shape`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_notes_slide_shape`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_notes_slide_shape`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='ShapeBase',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_notes_slide_shape_paragraph(self, request, **kwargs):  # noqa: E501
        """Read shape paragraph info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape_paragraph(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shape_paragraphRequest request: get_notes_slide_shape_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_notes_slide_shape_paragraph_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_notes_slide_shape_paragraph_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_notes_slide_shape_paragraph_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read shape paragraph info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape_paragraph_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shape_paragraphRequest request: get_notes_slide_shape_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_notes_slide_shape_paragraph" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_notes_slide_shape_paragraph`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_notes_slide_shape_paragraph`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_notes_slide_shape_paragraph`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `get_notes_slide_shape_paragraph`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraph',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_notes_slide_shape_paragraphs(self, request, **kwargs):  # noqa: E501
        """Read shape paragraphs info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape_paragraphs(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shape_paragraphsRequest request: get_notes_slide_shape_paragraphs request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_notes_slide_shape_paragraphs_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_notes_slide_shape_paragraphs_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_notes_slide_shape_paragraphs_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read shape paragraphs info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape_paragraphs_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shape_paragraphsRequest request: get_notes_slide_shape_paragraphs request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_notes_slide_shape_paragraphs" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_notes_slide_shape_paragraphs`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_notes_slide_shape_paragraphs`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_notes_slide_shape_paragraphs`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraphs',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_notes_slide_shape_portion(self, request, **kwargs):  # noqa: E501
        """Read paragraph portion info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape_portion(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shape_portionRequest request: get_notes_slide_shape_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_notes_slide_shape_portion_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_notes_slide_shape_portion_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_notes_slide_shape_portion_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read paragraph portion info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape_portion_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shape_portionRequest request: get_notes_slide_shape_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_notes_slide_shape_portion" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_notes_slide_shape_portion`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_notes_slide_shape_portion`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_notes_slide_shape_portion`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `get_notes_slide_shape_portion`")  # noqa: E501
        # verify the required parameter 'portion_index' is set
        if not request.portion_index:
            raise ValueError("Missing the required parameter `request.portion_index` when calling `get_notes_slide_shape_portion`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501
        path_params['portionIndex'] = request.portion_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions/{portionIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portion',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_notes_slide_shape_portions(self, request, **kwargs):  # noqa: E501
        """Read paragraph portions info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape_portions(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shape_portionsRequest request: get_notes_slide_shape_portions request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_notes_slide_shape_portions_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_notes_slide_shape_portions_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_notes_slide_shape_portions_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read paragraph portions info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shape_portions_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shape_portionsRequest request: get_notes_slide_shape_portions request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_notes_slide_shape_portions" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_notes_slide_shape_portions`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_notes_slide_shape_portions`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_notes_slide_shape_portions`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `get_notes_slide_shape_portions`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portions',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_notes_slide_shapes(self, request, **kwargs):  # noqa: E501
        """Read slide shapes info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shapes(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shapesRequest request: get_notes_slide_shapes request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_notes_slide_shapes_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_notes_slide_shapes_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_notes_slide_shapes_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide shapes info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_shapes_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_shapesRequest request: get_notes_slide_shapes request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_notes_slide_shapes" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_notes_slide_shapes`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_notes_slide_shapes`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Shapes',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_notes_slide_with_format(self, request, **kwargs):  # noqa: E501
        """Convert notes slide to the specified image format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_with_format(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_with_formatRequest request: get_notes_slide_with_format request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_notes_slide_with_format_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_notes_slide_with_format_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_notes_slide_with_format_with_http_info(self, request, **kwargs):  # noqa: E501
        """Convert notes slide to the specified image format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_notes_slide_with_format_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_notes_slide_with_formatRequest request: get_notes_slide_with_format request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_notes_slide_with_format" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_notes_slide_with_format`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_notes_slide_with_format`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `get_notes_slide_with_format`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.width:
            query_params.append(('width', request.width))  # noqa: E501
        if request.height:
            query_params.append(('height', request.height))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/{format}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_paragraph_portion(self, request, **kwargs):  # noqa: E501
        """Read paragraph portion info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_paragraph_portion(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_paragraph_portionRequest request: get_paragraph_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_paragraph_portion_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_paragraph_portion_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_paragraph_portion_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read paragraph portion info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_paragraph_portion_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_paragraph_portionRequest request: get_paragraph_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_paragraph_portion" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_paragraph_portion`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_paragraph_portion`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_paragraph_portion`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `get_paragraph_portion`")  # noqa: E501
        # verify the required parameter 'portion_index' is set
        if not request.portion_index:
            raise ValueError("Missing the required parameter `request.portion_index` when calling `get_paragraph_portion`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501
        path_params['portionIndex'] = request.portion_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions/{portionIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portion',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_paragraph_portions(self, request, **kwargs):  # noqa: E501
        """Read paragraph portions info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_paragraph_portions(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_paragraph_portionsRequest request: get_paragraph_portions request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_paragraph_portions_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_paragraph_portions_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_paragraph_portions_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read paragraph portions info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_paragraph_portions_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_paragraph_portionsRequest request: get_paragraph_portions request object
        :return: Portions
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_paragraph_portions" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_paragraph_portions`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_paragraph_portions`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_paragraph_portions`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `get_paragraph_portions`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portions',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slide_animation(self, request, **kwargs):  # noqa: E501
        """Read slide animation effects.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_animation(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_animationRequest request: get_slide_animation request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slide_animation_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slide_animation_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slide_animation_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide animation effects.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_animation_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_animationRequest request: get_slide_animation request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slide_animation" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slide_animation`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slide_animation`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_slide_animation`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.shape_index:
            query_params.append(('shapeIndex', request.shape_index))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slide_shape(self, request, **kwargs):  # noqa: E501
        """Read slide shape info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_shape(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_shapeRequest request: get_slide_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slide_shape_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide shape info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_shape_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_shapeRequest request: get_slide_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slide_shape" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slide_shape`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slide_shape`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_slide_shape`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='ShapeBase',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slide_shape_paragraph(self, request, **kwargs):  # noqa: E501
        """Read shape paragraph info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_shape_paragraph(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_shape_paragraphRequest request: get_slide_shape_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slide_shape_paragraph_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slide_shape_paragraph_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slide_shape_paragraph_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read shape paragraph info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_shape_paragraph_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_shape_paragraphRequest request: get_slide_shape_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slide_shape_paragraph" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slide_shape_paragraph`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slide_shape_paragraph`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_slide_shape_paragraph`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `get_slide_shape_paragraph`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraph',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slide_shape_paragraphs(self, request, **kwargs):  # noqa: E501
        """Read shape paragraphs info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_shape_paragraphs(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_shape_paragraphsRequest request: get_slide_shape_paragraphs request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slide_shape_paragraphs_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slide_shape_paragraphs_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slide_shape_paragraphs_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read shape paragraphs info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_shape_paragraphs_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_shape_paragraphsRequest request: get_slide_shape_paragraphs request object
        :return: Paragraphs
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slide_shape_paragraphs" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slide_shape_paragraphs`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slide_shape_paragraphs`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `get_slide_shape_paragraphs`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraphs',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slide_shapes(self, request, **kwargs):  # noqa: E501
        """Read slide shapes info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_shapes(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_shapesRequest request: get_slide_shapes request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slide_shapes_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slide_shapes_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slide_shapes_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide shapes info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slide_shapes_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slide_shapesRequest request: get_slide_shapes request object
        :return: Shapes
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slide_shapes" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slide_shapes`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slide_shapes`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Shapes',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_api_info(self, **kwargs):  # noqa: E501
        """Get API info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_api_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        
        :return: ApiInfo
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_api_info_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_api_info_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_slides_api_info_with_http_info(self, **kwargs):  # noqa: E501
        """Get API info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_api_info_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        
        :return: ApiInfo
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_api_info" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/info', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='ApiInfo',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_document(self, request, **kwargs):  # noqa: E501
        """Read presentation info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_document(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_documentRequest request: get_slides_document request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_document_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_document_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_document_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_document_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_documentRequest request: get_slides_document request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_document" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_document`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Document',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_document_properties(self, request, **kwargs):  # noqa: E501
        """Read presentation document properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_document_properties(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_document_propertiesRequest request: get_slides_document_properties request object
        :return: DocumentProperties
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_document_properties_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_document_properties_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_document_properties_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation document properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_document_properties_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_document_propertiesRequest request: get_slides_document_properties request object
        :return: DocumentProperties
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_document_properties" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_document_properties`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/documentproperties', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='DocumentProperties',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_document_property(self, request, **kwargs):  # noqa: E501
        """Read presentation document property.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_document_property(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_document_propertyRequest request: get_slides_document_property request object
        :return: DocumentProperty
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_document_property_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_document_property_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_document_property_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation document property.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_document_property_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_document_propertyRequest request: get_slides_document_property request object
        :return: DocumentProperty
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_document_property" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_document_property`")  # noqa: E501
        # verify the required parameter 'property_name' is set
        if not request.property_name:
            raise ValueError("Missing the required parameter `request.property_name` when calling `get_slides_document_property`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['propertyName'] = request.property_name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/documentproperties/{propertyName}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='DocumentProperty',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_image_with_default_format(self, request, **kwargs):  # noqa: E501
        """Get image binary data.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_image_with_default_format(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_image_with_default_formatRequest request: get_slides_image_with_default_format request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_image_with_default_format_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_image_with_default_format_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_image_with_default_format_with_http_info(self, request, **kwargs):  # noqa: E501
        """Get image binary data.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_image_with_default_format_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_image_with_default_formatRequest request: get_slides_image_with_default_format request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_image_with_default_format" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_image_with_default_format`")  # noqa: E501
        # verify the required parameter 'index' is set
        if not request.index:
            raise ValueError("Missing the required parameter `request.index` when calling `get_slides_image_with_default_format`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['index'] = request.index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/images/{index}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_image_with_format(self, request, **kwargs):  # noqa: E501
        """Get image in specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_image_with_format(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_image_with_formatRequest request: get_slides_image_with_format request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_image_with_format_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_image_with_format_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_image_with_format_with_http_info(self, request, **kwargs):  # noqa: E501
        """Get image in specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_image_with_format_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_image_with_formatRequest request: get_slides_image_with_format request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_image_with_format" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_image_with_format`")  # noqa: E501
        # verify the required parameter 'index' is set
        if not request.index:
            raise ValueError("Missing the required parameter `request.index` when calling `get_slides_image_with_format`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `get_slides_image_with_format`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['index'] = request.index  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/images/{index}/{format}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_images(self, request, **kwargs):  # noqa: E501
        """Read presentation images info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_images(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_imagesRequest request: get_slides_images request object
        :return: Images
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_images_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_images_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_images_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation images info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_images_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_imagesRequest request: get_slides_images request object
        :return: Images
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_images" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_images`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/images', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Images',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_placeholder(self, request, **kwargs):  # noqa: E501
        """Read slide placeholder info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_placeholder(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_placeholderRequest request: get_slides_placeholder request object
        :return: Placeholder
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_placeholder_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_placeholder_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_placeholder_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide placeholder info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_placeholder_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_placeholderRequest request: get_slides_placeholder request object
        :return: Placeholder
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_placeholder" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_placeholder`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_placeholder`")  # noqa: E501
        # verify the required parameter 'placeholder_index' is set
        if not request.placeholder_index:
            raise ValueError("Missing the required parameter `request.placeholder_index` when calling `get_slides_placeholder`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['placeholderIndex'] = request.placeholder_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/placeholders/{placeholderIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Placeholder',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_placeholders(self, request, **kwargs):  # noqa: E501
        """Read slide placeholders info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_placeholders(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_placeholdersRequest request: get_slides_placeholders request object
        :return: Placeholders
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_placeholders_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_placeholders_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_placeholders_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide placeholders info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_placeholders_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_placeholdersRequest request: get_slides_placeholders request object
        :return: Placeholders
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_placeholders" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_placeholders`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_placeholders`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/placeholders', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Placeholders',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_presentation_text_items(self, request, **kwargs):  # noqa: E501
        """Extract presentation text items.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_presentation_text_items(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_presentation_text_itemsRequest request: get_slides_presentation_text_items request object
        :return: TextItems
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_presentation_text_items_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_presentation_text_items_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_presentation_text_items_with_http_info(self, request, **kwargs):  # noqa: E501
        """Extract presentation text items.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_presentation_text_items_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_presentation_text_itemsRequest request: get_slides_presentation_text_items request object
        :return: TextItems
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_presentation_text_items" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_presentation_text_items`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.with_empty:
            query_params.append(('withEmpty', request.with_empty))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/textItems', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='TextItems',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_slide(self, request, **kwargs):  # noqa: E501
        """Read presentation slide info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slideRequest request: get_slides_slide request object
        :return: Slide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_slide_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_slide_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_slide_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation slide info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slideRequest request: get_slides_slide request object
        :return: Slide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_slide" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_slide`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_slide`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_slide_background(self, request, **kwargs):  # noqa: E501
        """Read slide background info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide_background(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slide_backgroundRequest request: get_slides_slide_background request object
        :return: SlideBackground
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_slide_background_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_slide_background_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_slide_background_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide background info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide_background_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slide_backgroundRequest request: get_slides_slide_background request object
        :return: SlideBackground
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_slide_background" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_slide_background`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_slide_background`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/background', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideBackground',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_slide_comments(self, request, **kwargs):  # noqa: E501
        """Read presentation slide comments.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide_comments(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slide_commentsRequest request: get_slides_slide_comments request object
        :return: SlideComments
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_slide_comments_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_slide_comments_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_slide_comments_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation slide comments.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide_comments_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slide_commentsRequest request: get_slides_slide_comments request object
        :return: SlideComments
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_slide_comments" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_slide_comments`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_slide_comments`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/comments', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideComments',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_slide_images(self, request, **kwargs):  # noqa: E501
        """Read slide images info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide_images(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slide_imagesRequest request: get_slides_slide_images request object
        :return: Images
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_slide_images_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_slide_images_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_slide_images_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide images info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide_images_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slide_imagesRequest request: get_slides_slide_images request object
        :return: Images
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_slide_images" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_slide_images`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_slide_images`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/images', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Images',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_slide_text_items(self, request, **kwargs):  # noqa: E501
        """Extract slide text items.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide_text_items(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slide_text_itemsRequest request: get_slides_slide_text_items request object
        :return: TextItems
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_slide_text_items_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_slide_text_items_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_slide_text_items_with_http_info(self, request, **kwargs):  # noqa: E501
        """Extract slide text items.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slide_text_items_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slide_text_itemsRequest request: get_slides_slide_text_items request object
        :return: TextItems
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_slide_text_items" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_slide_text_items`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_slide_text_items`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.with_empty:
            query_params.append(('withEmpty', request.with_empty))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/textItems', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='TextItems',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_slides_list(self, request, **kwargs):  # noqa: E501
        """Read presentation slides info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slides_list(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slides_listRequest request: get_slides_slides_list request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_slides_list_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_slides_list_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_slides_list_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read presentation slides info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_slides_list_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_slides_listRequest request: get_slides_slides_list request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_slides_list" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_slides_list`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slides',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_theme(self, request, **kwargs):  # noqa: E501
        """Read slide theme info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_theme(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_themeRequest request: get_slides_theme request object
        :return: Theme
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_theme_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_theme_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_theme_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide theme info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_theme_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_themeRequest request: get_slides_theme request object
        :return: Theme
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_theme" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_theme`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_theme`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/theme', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Theme',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_theme_color_scheme(self, request, **kwargs):  # noqa: E501
        """Read slide theme color scheme info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_theme_color_scheme(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_theme_color_schemeRequest request: get_slides_theme_color_scheme request object
        :return: ColorScheme
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_theme_color_scheme_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_theme_color_scheme_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_theme_color_scheme_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide theme color scheme info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_theme_color_scheme_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_theme_color_schemeRequest request: get_slides_theme_color_scheme request object
        :return: ColorScheme
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_theme_color_scheme" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_theme_color_scheme`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_theme_color_scheme`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/theme/colorScheme', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='ColorScheme',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_theme_font_scheme(self, request, **kwargs):  # noqa: E501
        """Read slide theme font scheme info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_theme_font_scheme(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_theme_font_schemeRequest request: get_slides_theme_font_scheme request object
        :return: FontScheme
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_theme_font_scheme_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_theme_font_scheme_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_theme_font_scheme_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide theme font scheme info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_theme_font_scheme_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_theme_font_schemeRequest request: get_slides_theme_font_scheme request object
        :return: FontScheme
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_theme_font_scheme" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_theme_font_scheme`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_theme_font_scheme`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/theme/fontScheme', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='FontScheme',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_slides_theme_format_scheme(self, request, **kwargs):  # noqa: E501
        """Read slide theme format scheme info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_theme_format_scheme(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_theme_format_schemeRequest request: get_slides_theme_format_scheme request object
        :return: FormatScheme
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.get_slides_theme_format_scheme_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.get_slides_theme_format_scheme_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def get_slides_theme_format_scheme_with_http_info(self, request, **kwargs):  # noqa: E501
        """Read slide theme format scheme info.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.get_slides_theme_format_scheme_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param get_slides_theme_format_schemeRequest request: get_slides_theme_format_scheme request object
        :return: FormatScheme
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_slides_theme_format_scheme" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `get_slides_theme_format_scheme`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `get_slides_theme_format_scheme`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/theme/formatScheme', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='FormatScheme',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def move_file(self, request, **kwargs):  # noqa: E501
        """Move file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.move_file(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param move_fileRequest request: move_file request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.move_file_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.move_file_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def move_file_with_http_info(self, request, **kwargs):  # noqa: E501
        """Move file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.move_file_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param move_fileRequest request: move_file request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method move_file" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'src_path' is set
        if not request.src_path:
            raise ValueError("Missing the required parameter `request.src_path` when calling `move_file`")  # noqa: E501
        # verify the required parameter 'dest_path' is set
        if not request.dest_path:
            raise ValueError("Missing the required parameter `request.dest_path` when calling `move_file`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['srcPath'] = request.src_path  # noqa: E501

        query_params = []
        if request.dest_path:
            query_params.append(('destPath', request.dest_path))  # noqa: E501
        if request.src_storage_name:
            query_params.append(('srcStorageName', request.src_storage_name))  # noqa: E501
        if request.dest_storage_name:
            query_params.append(('destStorageName', request.dest_storage_name))  # noqa: E501
        if request.version_id:
            query_params.append(('versionId', request.version_id))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/file/move/{srcPath}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def move_folder(self, request, **kwargs):  # noqa: E501
        """Move folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.move_folder(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param move_folderRequest request: move_folder request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.move_folder_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.move_folder_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def move_folder_with_http_info(self, request, **kwargs):  # noqa: E501
        """Move folder  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.move_folder_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param move_folderRequest request: move_folder request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method move_folder" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'src_path' is set
        if not request.src_path:
            raise ValueError("Missing the required parameter `request.src_path` when calling `move_folder`")  # noqa: E501
        # verify the required parameter 'dest_path' is set
        if not request.dest_path:
            raise ValueError("Missing the required parameter `request.dest_path` when calling `move_folder`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['srcPath'] = request.src_path  # noqa: E501

        query_params = []
        if request.dest_path:
            query_params.append(('destPath', request.dest_path))  # noqa: E501
        if request.src_storage_name:
            query_params.append(('srcStorageName', request.src_storage_name))  # noqa: E501
        if request.dest_storage_name:
            query_params.append(('destStorageName', request.dest_storage_name))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/folder/move/{srcPath}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def object_exists(self, request, **kwargs):  # noqa: E501
        """Check if file or folder exists  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.object_exists(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param object_existsRequest request: object_exists request object
        :return: ObjectExist
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.object_exists_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.object_exists_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def object_exists_with_http_info(self, request, **kwargs):  # noqa: E501
        """Check if file or folder exists  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.object_exists_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param object_existsRequest request: object_exists request object
        :return: ObjectExist
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method object_exists" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.storage_name:
            query_params.append(('storageName', request.storage_name))  # noqa: E501
        if request.version_id:
            query_params.append(('versionId', request.version_id))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/exist/{path}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='ObjectExist',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_add_new_paragraph(self, request, **kwargs):  # noqa: E501
        """Creates new paragraph.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_add_new_paragraph(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_add_new_paragraphRequest request: post_add_new_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_add_new_paragraph_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_add_new_paragraph_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_add_new_paragraph_with_http_info(self, request, **kwargs):  # noqa: E501
        """Creates new paragraph.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_add_new_paragraph_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_add_new_paragraphRequest request: post_add_new_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_add_new_paragraph" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_add_new_paragraph`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_add_new_paragraph`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `post_add_new_paragraph`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.position:
            query_params.append(('position', request.position))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraph',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_add_new_portion(self, request, **kwargs):  # noqa: E501
        """Creates new portion.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_add_new_portion(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_add_new_portionRequest request: post_add_new_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_add_new_portion_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_add_new_portion_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_add_new_portion_with_http_info(self, request, **kwargs):  # noqa: E501
        """Creates new portion.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_add_new_portion_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_add_new_portionRequest request: post_add_new_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_add_new_portion" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_add_new_portion`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_add_new_portion`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `post_add_new_portion`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `post_add_new_portion`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.position:
            query_params.append(('position', request.position))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portion',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_add_new_shape(self, request, **kwargs):  # noqa: E501
        """Create new shape.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_add_new_shape(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_add_new_shapeRequest request: post_add_new_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_add_new_shape_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_add_new_shape_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_add_new_shape_with_http_info(self, request, **kwargs):  # noqa: E501
        """Create new shape.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_add_new_shape_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_add_new_shapeRequest request: post_add_new_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_add_new_shape" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_add_new_shape`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_add_new_shape`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.shape_to_clone:
            query_params.append(('shapeToClone', request.shape_to_clone))  # noqa: E501
        if request.position:
            query_params.append(('position', request.position))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='ShapeBase',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_add_notes_slide(self, request, **kwargs):  # noqa: E501
        """Add new notes slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_add_notes_slide(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_add_notes_slideRequest request: post_add_notes_slide request object
        :return: NotesSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_add_notes_slide_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_add_notes_slide_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_add_notes_slide_with_http_info(self, request, **kwargs):  # noqa: E501
        """Add new notes slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_add_notes_slide_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_add_notes_slideRequest request: post_add_notes_slide request object
        :return: NotesSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_add_notes_slide" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_add_notes_slide`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_add_notes_slide`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='NotesSlide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_copy_layout_slide_from_source_presentation(self, request, **kwargs):  # noqa: E501
        """Copy layoutSlide from source presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_copy_layout_slide_from_source_presentation(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_copy_layout_slide_from_source_presentationRequest request: post_copy_layout_slide_from_source_presentation request object
        :return: LayoutSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_copy_layout_slide_from_source_presentation_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_copy_layout_slide_from_source_presentation_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_copy_layout_slide_from_source_presentation_with_http_info(self, request, **kwargs):  # noqa: E501
        """Copy layoutSlide from source presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_copy_layout_slide_from_source_presentation_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_copy_layout_slide_from_source_presentationRequest request: post_copy_layout_slide_from_source_presentation request object
        :return: LayoutSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_copy_layout_slide_from_source_presentation" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_copy_layout_slide_from_source_presentation`")  # noqa: E501
        # verify the required parameter 'clone_from' is set
        if not request.clone_from:
            raise ValueError("Missing the required parameter `request.clone_from` when calling `post_copy_layout_slide_from_source_presentation`")  # noqa: E501
        # verify the required parameter 'clone_from_position' is set
        if not request.clone_from_position:
            raise ValueError("Missing the required parameter `request.clone_from_position` when calling `post_copy_layout_slide_from_source_presentation`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.clone_from:
            query_params.append(('cloneFrom', request.clone_from))  # noqa: E501
        if request.clone_from_position:
            query_params.append(('cloneFromPosition', request.clone_from_position))  # noqa: E501
        if request.clone_from_password:
            query_params.append(('cloneFromPassword', request.clone_from_password))  # noqa: E501
        if request.clone_from_storage:
            query_params.append(('cloneFromStorage', request.clone_from_storage))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/layoutSlides', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='LayoutSlide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_copy_master_slide_from_source_presentation(self, request, **kwargs):  # noqa: E501
        """Copy masterSlide from source presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_copy_master_slide_from_source_presentation(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_copy_master_slide_from_source_presentationRequest request: post_copy_master_slide_from_source_presentation request object
        :return: MasterSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_copy_master_slide_from_source_presentation_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_copy_master_slide_from_source_presentation_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_copy_master_slide_from_source_presentation_with_http_info(self, request, **kwargs):  # noqa: E501
        """Copy masterSlide from source presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_copy_master_slide_from_source_presentation_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_copy_master_slide_from_source_presentationRequest request: post_copy_master_slide_from_source_presentation request object
        :return: MasterSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_copy_master_slide_from_source_presentation" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_copy_master_slide_from_source_presentation`")  # noqa: E501
        # verify the required parameter 'clone_from' is set
        if not request.clone_from:
            raise ValueError("Missing the required parameter `request.clone_from` when calling `post_copy_master_slide_from_source_presentation`")  # noqa: E501
        # verify the required parameter 'clone_from_position' is set
        if not request.clone_from_position:
            raise ValueError("Missing the required parameter `request.clone_from_position` when calling `post_copy_master_slide_from_source_presentation`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.clone_from:
            query_params.append(('cloneFrom', request.clone_from))  # noqa: E501
        if request.clone_from_position:
            query_params.append(('cloneFromPosition', request.clone_from_position))  # noqa: E501
        if request.clone_from_password:
            query_params.append(('cloneFromPassword', request.clone_from_password))  # noqa: E501
        if request.clone_from_storage:
            query_params.append(('cloneFromStorage', request.clone_from_storage))  # noqa: E501
        if request.apply_to_all:
            query_params.append(('applyToAll', request.apply_to_all))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/masterSlides', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='MasterSlide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_notes_slide_add_new_paragraph(self, request, **kwargs):  # noqa: E501
        """Creates new paragraph.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_notes_slide_add_new_paragraph(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_notes_slide_add_new_paragraphRequest request: post_notes_slide_add_new_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_notes_slide_add_new_paragraph_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_notes_slide_add_new_paragraph_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_notes_slide_add_new_paragraph_with_http_info(self, request, **kwargs):  # noqa: E501
        """Creates new paragraph.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_notes_slide_add_new_paragraph_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_notes_slide_add_new_paragraphRequest request: post_notes_slide_add_new_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_notes_slide_add_new_paragraph" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_notes_slide_add_new_paragraph`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_notes_slide_add_new_paragraph`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `post_notes_slide_add_new_paragraph`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.position:
            query_params.append(('position', request.position))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraph',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_notes_slide_add_new_portion(self, request, **kwargs):  # noqa: E501
        """Creates new portion.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_notes_slide_add_new_portion(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_notes_slide_add_new_portionRequest request: post_notes_slide_add_new_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_notes_slide_add_new_portion_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_notes_slide_add_new_portion_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_notes_slide_add_new_portion_with_http_info(self, request, **kwargs):  # noqa: E501
        """Creates new portion.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_notes_slide_add_new_portion_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_notes_slide_add_new_portionRequest request: post_notes_slide_add_new_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_notes_slide_add_new_portion" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_notes_slide_add_new_portion`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_notes_slide_add_new_portion`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `post_notes_slide_add_new_portion`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `post_notes_slide_add_new_portion`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.position:
            query_params.append(('position', request.position))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portion',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_notes_slide_add_new_shape(self, request, **kwargs):  # noqa: E501
        """Create new shape.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_notes_slide_add_new_shape(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_notes_slide_add_new_shapeRequest request: post_notes_slide_add_new_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_notes_slide_add_new_shape_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_notes_slide_add_new_shape_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_notes_slide_add_new_shape_with_http_info(self, request, **kwargs):  # noqa: E501
        """Create new shape.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_notes_slide_add_new_shape_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_notes_slide_add_new_shapeRequest request: post_notes_slide_add_new_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_notes_slide_add_new_shape" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_notes_slide_add_new_shape`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_notes_slide_add_new_shape`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.shape_to_clone:
            query_params.append(('shapeToClone', request.shape_to_clone))  # noqa: E501
        if request.position:
            query_params.append(('position', request.position))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='ShapeBase',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_notes_slide_shape_save_as(self, request, **kwargs):  # noqa: E501
        """Render shape to specified picture format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_notes_slide_shape_save_as(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_notes_slide_shape_save_asRequest request: post_notes_slide_shape_save_as request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_notes_slide_shape_save_as_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_notes_slide_shape_save_as_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_notes_slide_shape_save_as_with_http_info(self, request, **kwargs):  # noqa: E501
        """Render shape to specified picture format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_notes_slide_shape_save_as_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_notes_slide_shape_save_asRequest request: post_notes_slide_shape_save_as request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_notes_slide_shape_save_as" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_notes_slide_shape_save_as`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_notes_slide_shape_save_as`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `post_notes_slide_shape_save_as`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `post_notes_slide_shape_save_as`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.scale_x:
            query_params.append(('scaleX', request.scale_x))  # noqa: E501
        if request.scale_y:
            query_params.append(('scaleY', request.scale_y))  # noqa: E501
        if request.bounds:
            query_params.append(('bounds', request.bounds))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.options:
            body_params = request.options


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/{format}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_presentation_merge(self, request, **kwargs):  # noqa: E501
        """Merge the presentation with other presentations specified in the request parameter.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_presentation_merge(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_presentation_mergeRequest request: post_presentation_merge request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_presentation_merge_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_presentation_merge_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_presentation_merge_with_http_info(self, request, **kwargs):  # noqa: E501
        """Merge the presentation with other presentations specified in the request parameter.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_presentation_merge_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_presentation_mergeRequest request: post_presentation_merge request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_presentation_merge" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_presentation_merge`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.request:
            body_params = request.request


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/merge', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Document',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_shape_save_as(self, request, **kwargs):  # noqa: E501
        """Render shape to specified picture format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_shape_save_as(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_shape_save_asRequest request: post_shape_save_as request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_shape_save_as_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_shape_save_as_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_shape_save_as_with_http_info(self, request, **kwargs):  # noqa: E501
        """Render shape to specified picture format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_shape_save_as_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_shape_save_asRequest request: post_shape_save_as request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_shape_save_as" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_shape_save_as`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_shape_save_as`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `post_shape_save_as`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `post_shape_save_as`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.scale_x:
            query_params.append(('scaleX', request.scale_x))  # noqa: E501
        if request.scale_y:
            query_params.append(('scaleY', request.scale_y))  # noqa: E501
        if request.bounds:
            query_params.append(('bounds', request.bounds))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.options:
            body_params = request.options


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/{format}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slide_animation_effect(self, request, **kwargs):  # noqa: E501
        """Add an effect to slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slide_animation_effect(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slide_animation_effectRequest request: post_slide_animation_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slide_animation_effect_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slide_animation_effect_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slide_animation_effect_with_http_info(self, request, **kwargs):  # noqa: E501
        """Add an effect to slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slide_animation_effect_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slide_animation_effectRequest request: post_slide_animation_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slide_animation_effect" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slide_animation_effect`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_slide_animation_effect`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.effect:
            body_params = request.effect


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/mainSequence', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slide_animation_interactive_sequence(self, request, **kwargs):  # noqa: E501
        """Set slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slide_animation_interactive_sequence(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slide_animation_interactive_sequenceRequest request: post_slide_animation_interactive_sequence request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slide_animation_interactive_sequence_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slide_animation_interactive_sequence_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slide_animation_interactive_sequence_with_http_info(self, request, **kwargs):  # noqa: E501
        """Set slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slide_animation_interactive_sequence_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slide_animation_interactive_sequenceRequest request: post_slide_animation_interactive_sequence request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slide_animation_interactive_sequence" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slide_animation_interactive_sequence`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_slide_animation_interactive_sequence`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.sequence:
            body_params = request.sequence


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/interactiveSequences', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slide_animation_interactive_sequence_effect(self, request, **kwargs):  # noqa: E501
        """Add an animation effect to a slide interactive sequence.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slide_animation_interactive_sequence_effect(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slide_animation_interactive_sequence_effectRequest request: post_slide_animation_interactive_sequence_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slide_animation_interactive_sequence_effect_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slide_animation_interactive_sequence_effect_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slide_animation_interactive_sequence_effect_with_http_info(self, request, **kwargs):  # noqa: E501
        """Add an animation effect to a slide interactive sequence.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slide_animation_interactive_sequence_effect_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slide_animation_interactive_sequence_effectRequest request: post_slide_animation_interactive_sequence_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slide_animation_interactive_sequence_effect" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slide_animation_interactive_sequence_effect`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_slide_animation_interactive_sequence_effect`")  # noqa: E501
        # verify the required parameter 'sequence_index' is set
        if not request.sequence_index:
            raise ValueError("Missing the required parameter `request.sequence_index` when calling `post_slide_animation_interactive_sequence_effect`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['sequenceIndex'] = request.sequence_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.effect:
            body_params = request.effect


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/interactiveSequences/{sequenceIndex}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slide_save_as(self, request, **kwargs):  # noqa: E501
        """Save a slide to a specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slide_save_as(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slide_save_asRequest request: post_slide_save_as request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slide_save_as_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slide_save_as_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slide_save_as_with_http_info(self, request, **kwargs):  # noqa: E501
        """Save a slide to a specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slide_save_as_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slide_save_asRequest request: post_slide_save_as request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slide_save_as" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slide_save_as`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_slide_save_as`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `post_slide_save_as`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.width:
            query_params.append(('width', request.width))  # noqa: E501
        if request.height:
            query_params.append(('height', request.height))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.options:
            body_params = request.options


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/{format}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_add(self, request, **kwargs):  # noqa: E501
        """Create a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_add(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_addRequest request: post_slides_add request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_add_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_add_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_add_with_http_info(self, request, **kwargs):  # noqa: E501
        """Create a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_add_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_addRequest request: post_slides_add request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_add" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_add`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.position:
            query_params.append(('position', request.position))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.layout_alias:
            query_params.append(('layoutAlias', request.layout_alias))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slides',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_convert(self, request, **kwargs):  # noqa: E501
        """Convert presentation from request content to format specified.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_convert(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_convertRequest request: post_slides_convert request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_convert_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_convert_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_convert_with_http_info(self, request, **kwargs):  # noqa: E501
        """Convert presentation from request content to format specified.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_convert_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_convertRequest request: post_slides_convert request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_convert" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `post_slides_convert`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.document:
            body_params = request.document


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/octet-stream', 'multipart/form-data'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/convert/{format}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_copy(self, request, **kwargs):  # noqa: E501
        """Copy a slide from the current or another presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_copy(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_copyRequest request: post_slides_copy request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_copy_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_copy_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_copy_with_http_info(self, request, **kwargs):  # noqa: E501
        """Copy a slide from the current or another presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_copy_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_copyRequest request: post_slides_copy request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_copy" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_copy`")  # noqa: E501
        # verify the required parameter 'slide_to_copy' is set
        if not request.slide_to_copy:
            raise ValueError("Missing the required parameter `request.slide_to_copy` when calling `post_slides_copy`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.slide_to_copy:
            query_params.append(('slideToCopy', request.slide_to_copy))  # noqa: E501
        if request.position:
            query_params.append(('position', request.position))  # noqa: E501
        if request.source:
            query_params.append(('source', request.source))  # noqa: E501
        if request.source_password:
            query_params.append(('sourcePassword', request.source_password))  # noqa: E501
        if request.source_storage:
            query_params.append(('sourceStorage', request.source_storage))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/copy', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slides',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_document(self, request, **kwargs):  # noqa: E501
        """Create a presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_document(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_documentRequest request: post_slides_document request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_document_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_document_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_document_with_http_info(self, request, **kwargs):  # noqa: E501
        """Create a presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_document_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_documentRequest request: post_slides_document request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_document" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_document`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.input_password:
            query_params.append(('inputPassword', request.input_password))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.data:
            body_params = request.data


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/octet-stream', 'multipart/form-data'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Document',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_document_from_html(self, request, **kwargs):  # noqa: E501
        """Create presentation document from html.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_document_from_html(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_document_from_htmlRequest request: post_slides_document_from_html request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_document_from_html_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_document_from_html_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_document_from_html_with_http_info(self, request, **kwargs):  # noqa: E501
        """Create presentation document from html.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_document_from_html_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_document_from_htmlRequest request: post_slides_document_from_html request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_document_from_html" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_document_from_html`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.html:
            body_params = request.html


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/fromHtml', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Document',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_document_from_source(self, request, **kwargs):  # noqa: E501
        """Create a presentation from an existing source.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_document_from_source(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_document_from_sourceRequest request: post_slides_document_from_source request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_document_from_source_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_document_from_source_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_document_from_source_with_http_info(self, request, **kwargs):  # noqa: E501
        """Create a presentation from an existing source.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_document_from_source_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_document_from_sourceRequest request: post_slides_document_from_source request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_document_from_source" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_document_from_source`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.source_path:
            query_params.append(('sourcePath', request.source_path))  # noqa: E501
        if request.source_password:
            query_params.append(('sourcePassword', request.source_password))  # noqa: E501
        if request.source_storage:
            query_params.append(('sourceStorage', request.source_storage))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/fromSource', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Document',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_document_from_template(self, request, **kwargs):  # noqa: E501
        """Create a presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_document_from_template(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_document_from_templateRequest request: post_slides_document_from_template request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_document_from_template_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_document_from_template_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_document_from_template_with_http_info(self, request, **kwargs):  # noqa: E501
        """Create a presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_document_from_template_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_document_from_templateRequest request: post_slides_document_from_template request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_document_from_template" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_document_from_template`")  # noqa: E501
        # verify the required parameter 'template_path' is set
        if not request.template_path:
            raise ValueError("Missing the required parameter `request.template_path` when calling `post_slides_document_from_template`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.template_path:
            query_params.append(('templatePath', request.template_path))  # noqa: E501
        if request.template_password:
            query_params.append(('templatePassword', request.template_password))  # noqa: E501
        if request.template_storage:
            query_params.append(('templateStorage', request.template_storage))  # noqa: E501
        if request.is_image_data_embedded:
            query_params.append(('isImageDataEmbedded', request.is_image_data_embedded))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.data:
            body_params = request.data


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/fromTemplate', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Document',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_pipeline(self, request, **kwargs):  # noqa: E501
        """Performs slides pipeline.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_pipeline(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_pipelineRequest request: post_slides_pipeline request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_pipeline_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_pipeline_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_pipeline_with_http_info(self, request, **kwargs):  # noqa: E501
        """Performs slides pipeline.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_pipeline_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_pipelineRequest request: post_slides_pipeline request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_pipeline" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.pipeline:
            body_params = request.pipeline

        files = request.files

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['multipart/form-data'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/pipeline', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_presentation_replace_text(self, request, **kwargs):  # noqa: E501
        """Replace text with a new value.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_presentation_replace_text(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_presentation_replace_textRequest request: post_slides_presentation_replace_text request object
        :return: DocumentReplaceResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_presentation_replace_text_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_presentation_replace_text_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_presentation_replace_text_with_http_info(self, request, **kwargs):  # noqa: E501
        """Replace text with a new value.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_presentation_replace_text_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_presentation_replace_textRequest request: post_slides_presentation_replace_text request object
        :return: DocumentReplaceResult
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_presentation_replace_text" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_presentation_replace_text`")  # noqa: E501
        # verify the required parameter 'old_value' is set
        if not request.old_value:
            raise ValueError("Missing the required parameter `request.old_value` when calling `post_slides_presentation_replace_text`")  # noqa: E501
        # verify the required parameter 'new_value' is set
        if not request.new_value:
            raise ValueError("Missing the required parameter `request.new_value` when calling `post_slides_presentation_replace_text`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.old_value:
            query_params.append(('oldValue', request.old_value))  # noqa: E501
        if request.new_value:
            query_params.append(('newValue', request.new_value))  # noqa: E501
        if request.ignore_case:
            query_params.append(('ignoreCase', request.ignore_case))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/replaceText', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='DocumentReplaceResult',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_reorder(self, request, **kwargs):  # noqa: E501
        """Reorder presentation slide position.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_reorder(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_reorderRequest request: post_slides_reorder request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_reorder_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_reorder_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_reorder_with_http_info(self, request, **kwargs):  # noqa: E501
        """Reorder presentation slide position.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_reorder_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_reorderRequest request: post_slides_reorder request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_reorder" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_reorder`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_slides_reorder`")  # noqa: E501
        # verify the required parameter 'new_position' is set
        if not request.new_position:
            raise ValueError("Missing the required parameter `request.new_position` when calling `post_slides_reorder`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.new_position:
            query_params.append(('newPosition', request.new_position))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/move', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slides',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_reorder_many(self, request, **kwargs):  # noqa: E501
        """Reorder presentation slides positions.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_reorder_many(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_reorder_manyRequest request: post_slides_reorder_many request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_reorder_many_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_reorder_many_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_reorder_many_with_http_info(self, request, **kwargs):  # noqa: E501
        """Reorder presentation slides positions.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_reorder_many_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_reorder_manyRequest request: post_slides_reorder_many request object
        :return: Slides
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_reorder_many" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_reorder_many`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.old_positions:
            query_params.append(('oldPositions', request.old_positions))  # noqa: E501
            collection_formats['oldPositions'] = ''  # noqa: E501
        if request.new_positions:
            query_params.append(('newPositions', request.new_positions))  # noqa: E501
            collection_formats['newPositions'] = ''  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/reorder', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slides',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_save_as(self, request, **kwargs):  # noqa: E501
        """Save a presentation to a specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_save_as(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_save_asRequest request: post_slides_save_as request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_save_as_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_save_as_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_save_as_with_http_info(self, request, **kwargs):  # noqa: E501
        """Save a presentation to a specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_save_as_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_save_asRequest request: post_slides_save_as request object
        :return: file
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_save_as" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_save_as`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `post_slides_save_as`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.options:
            body_params = request.options


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['multipart/form-data'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/{format}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='file',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_set_document_properties(self, request, **kwargs):  # noqa: E501
        """Set document properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_set_document_properties(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_set_document_propertiesRequest request: post_slides_set_document_properties request object
        :return: DocumentProperties
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_set_document_properties_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_set_document_properties_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_set_document_properties_with_http_info(self, request, **kwargs):  # noqa: E501
        """Set document properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_set_document_properties_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_set_document_propertiesRequest request: post_slides_set_document_properties request object
        :return: DocumentProperties
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_set_document_properties" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_set_document_properties`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.properties:
            body_params = request.properties


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/documentproperties', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='DocumentProperties',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_slide_replace_text(self, request, **kwargs):  # noqa: E501
        """Replace text with a new value.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_slide_replace_text(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_slide_replace_textRequest request: post_slides_slide_replace_text request object
        :return: SlideReplaceResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_slide_replace_text_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_slide_replace_text_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_slide_replace_text_with_http_info(self, request, **kwargs):  # noqa: E501
        """Replace text with a new value.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_slide_replace_text_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_slide_replace_textRequest request: post_slides_slide_replace_text request object
        :return: SlideReplaceResult
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_slide_replace_text" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_slide_replace_text`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `post_slides_slide_replace_text`")  # noqa: E501
        # verify the required parameter 'old_value' is set
        if not request.old_value:
            raise ValueError("Missing the required parameter `request.old_value` when calling `post_slides_slide_replace_text`")  # noqa: E501
        # verify the required parameter 'new_value' is set
        if not request.new_value:
            raise ValueError("Missing the required parameter `request.new_value` when calling `post_slides_slide_replace_text`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.old_value:
            query_params.append(('oldValue', request.old_value))  # noqa: E501
        if request.new_value:
            query_params.append(('newValue', request.new_value))  # noqa: E501
        if request.ignore_case:
            query_params.append(('ignoreCase', request.ignore_case))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/replaceText', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideReplaceResult',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_slides_split(self, request, **kwargs):  # noqa: E501
        """Splitting presentations. Create one image per slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_split(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_splitRequest request: post_slides_split request object
        :return: SplitDocumentResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.post_slides_split_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.post_slides_split_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def post_slides_split_with_http_info(self, request, **kwargs):  # noqa: E501
        """Splitting presentations. Create one image per slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.post_slides_split_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param post_slides_splitRequest request: post_slides_split request object
        :return: SplitDocumentResult
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_slides_split" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `post_slides_split`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.format:
            query_params.append(('format', request.format))  # noqa: E501
        if request.width:
            query_params.append(('width', request.width))  # noqa: E501
        if request.height:
            query_params.append(('height', request.height))  # noqa: E501
        if request.to:
            query_params.append(('to', request.to))  # noqa: E501
        if request._from:
            query_params.append(('from', request._from))  # noqa: E501
        if request.dest_folder:
            query_params.append(('destFolder', request.dest_folder))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.options:
            body_params = request.options


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/split', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SplitDocumentResult',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_layout_slide(self, request, **kwargs):  # noqa: E501
        """Update a layoutSlide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_layout_slide(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_layout_slideRequest request: put_layout_slide request object
        :return: LayoutSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_layout_slide_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_layout_slide_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_layout_slide_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update a layoutSlide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_layout_slide_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_layout_slideRequest request: put_layout_slide request object
        :return: LayoutSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_layout_slide" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_layout_slide`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_layout_slide`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.slide_dto:
            body_params = request.slide_dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/layoutSlides/{slideIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='LayoutSlide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_notes_slide_shape_save_as(self, request, **kwargs):  # noqa: E501
        """Render shape to specified picture format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_notes_slide_shape_save_as(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_notes_slide_shape_save_asRequest request: put_notes_slide_shape_save_as request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_notes_slide_shape_save_as_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_notes_slide_shape_save_as_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_notes_slide_shape_save_as_with_http_info(self, request, **kwargs):  # noqa: E501
        """Render shape to specified picture format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_notes_slide_shape_save_as_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_notes_slide_shape_save_asRequest request: put_notes_slide_shape_save_as request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_notes_slide_shape_save_as" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_notes_slide_shape_save_as`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_notes_slide_shape_save_as`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `put_notes_slide_shape_save_as`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `put_notes_slide_shape_save_as`")  # noqa: E501
        # verify the required parameter 'out_path' is set
        if not request.out_path:
            raise ValueError("Missing the required parameter `request.out_path` when calling `put_notes_slide_shape_save_as`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.out_path:
            query_params.append(('outPath', request.out_path))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.scale_x:
            query_params.append(('scaleX', request.scale_x))  # noqa: E501
        if request.scale_y:
            query_params.append(('scaleY', request.scale_y))  # noqa: E501
        if request.bounds:
            query_params.append(('bounds', request.bounds))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.options:
            body_params = request.options


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/{format}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_presentation_merge(self, request, **kwargs):  # noqa: E501
        """Merge the presentation with other presentations or some of their slides specified in the request parameter.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_presentation_merge(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_presentation_mergeRequest request: put_presentation_merge request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_presentation_merge_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_presentation_merge_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_presentation_merge_with_http_info(self, request, **kwargs):  # noqa: E501
        """Merge the presentation with other presentations or some of their slides specified in the request parameter.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_presentation_merge_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_presentation_mergeRequest request: put_presentation_merge request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_presentation_merge" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_presentation_merge`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.request:
            body_params = request.request


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/merge', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Document',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_set_paragraph_portion_properties(self, request, **kwargs):  # noqa: E501
        """Update portion properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_set_paragraph_portion_properties(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_set_paragraph_portion_propertiesRequest request: put_set_paragraph_portion_properties request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_set_paragraph_portion_properties_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_set_paragraph_portion_properties_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_set_paragraph_portion_properties_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update portion properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_set_paragraph_portion_properties_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_set_paragraph_portion_propertiesRequest request: put_set_paragraph_portion_properties request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_set_paragraph_portion_properties" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_set_paragraph_portion_properties`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_set_paragraph_portion_properties`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `put_set_paragraph_portion_properties`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `put_set_paragraph_portion_properties`")  # noqa: E501
        # verify the required parameter 'portion_index' is set
        if not request.portion_index:
            raise ValueError("Missing the required parameter `request.portion_index` when calling `put_set_paragraph_portion_properties`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501
        path_params['portionIndex'] = request.portion_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions/{portionIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portion',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_set_paragraph_properties(self, request, **kwargs):  # noqa: E501
        """Update paragraph properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_set_paragraph_properties(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_set_paragraph_propertiesRequest request: put_set_paragraph_properties request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_set_paragraph_properties_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_set_paragraph_properties_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_set_paragraph_properties_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update paragraph properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_set_paragraph_properties_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_set_paragraph_propertiesRequest request: put_set_paragraph_properties request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_set_paragraph_properties" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_set_paragraph_properties`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_set_paragraph_properties`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `put_set_paragraph_properties`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `put_set_paragraph_properties`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraph',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_shape_save_as(self, request, **kwargs):  # noqa: E501
        """Render shape to specified picture format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_shape_save_as(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_shape_save_asRequest request: put_shape_save_as request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_shape_save_as_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_shape_save_as_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_shape_save_as_with_http_info(self, request, **kwargs):  # noqa: E501
        """Render shape to specified picture format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_shape_save_as_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_shape_save_asRequest request: put_shape_save_as request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_shape_save_as" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_shape_save_as`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_shape_save_as`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `put_shape_save_as`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `put_shape_save_as`")  # noqa: E501
        # verify the required parameter 'out_path' is set
        if not request.out_path:
            raise ValueError("Missing the required parameter `request.out_path` when calling `put_shape_save_as`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.out_path:
            query_params.append(('outPath', request.out_path))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.scale_x:
            query_params.append(('scaleX', request.scale_x))  # noqa: E501
        if request.scale_y:
            query_params.append(('scaleY', request.scale_y))  # noqa: E501
        if request.bounds:
            query_params.append(('bounds', request.bounds))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.options:
            body_params = request.options


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}/{format}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slide_animation(self, request, **kwargs):  # noqa: E501
        """Set slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_animation(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_animationRequest request: put_slide_animation request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slide_animation_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slide_animation_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slide_animation_with_http_info(self, request, **kwargs):  # noqa: E501
        """Set slide animation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_animation_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_animationRequest request: put_slide_animation request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slide_animation" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slide_animation`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_slide_animation`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.animation:
            body_params = request.animation


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slide_animation_effect(self, request, **kwargs):  # noqa: E501
        """Modify an animation effect for a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_animation_effect(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_animation_effectRequest request: put_slide_animation_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slide_animation_effect_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slide_animation_effect_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slide_animation_effect_with_http_info(self, request, **kwargs):  # noqa: E501
        """Modify an animation effect for a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_animation_effect_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_animation_effectRequest request: put_slide_animation_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slide_animation_effect" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slide_animation_effect`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_slide_animation_effect`")  # noqa: E501
        # verify the required parameter 'effect_index' is set
        if not request.effect_index:
            raise ValueError("Missing the required parameter `request.effect_index` when calling `put_slide_animation_effect`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['effectIndex'] = request.effect_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.effect:
            body_params = request.effect


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/mainSequence/{effectIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slide_animation_interactive_sequence_effect(self, request, **kwargs):  # noqa: E501
        """Modify an animation effect for a slide interactive sequence.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_animation_interactive_sequence_effect(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_animation_interactive_sequence_effectRequest request: put_slide_animation_interactive_sequence_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slide_animation_interactive_sequence_effect_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slide_animation_interactive_sequence_effect_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slide_animation_interactive_sequence_effect_with_http_info(self, request, **kwargs):  # noqa: E501
        """Modify an animation effect for a slide interactive sequence.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_animation_interactive_sequence_effect_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_animation_interactive_sequence_effectRequest request: put_slide_animation_interactive_sequence_effect request object
        :return: SlideAnimation
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slide_animation_interactive_sequence_effect" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slide_animation_interactive_sequence_effect`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_slide_animation_interactive_sequence_effect`")  # noqa: E501
        # verify the required parameter 'sequence_index' is set
        if not request.sequence_index:
            raise ValueError("Missing the required parameter `request.sequence_index` when calling `put_slide_animation_interactive_sequence_effect`")  # noqa: E501
        # verify the required parameter 'effect_index' is set
        if not request.effect_index:
            raise ValueError("Missing the required parameter `request.effect_index` when calling `put_slide_animation_interactive_sequence_effect`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['sequenceIndex'] = request.sequence_index  # noqa: E501
        path_params['effectIndex'] = request.effect_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.effect:
            body_params = request.effect


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/animation/interactiveSequences/{sequenceIndex}/{effectIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideAnimation',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slide_save_as(self, request, **kwargs):  # noqa: E501
        """Save a slide to a specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_save_as(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_save_asRequest request: put_slide_save_as request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slide_save_as_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slide_save_as_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slide_save_as_with_http_info(self, request, **kwargs):  # noqa: E501
        """Save a slide to a specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_save_as_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_save_asRequest request: put_slide_save_as request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slide_save_as" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slide_save_as`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_slide_save_as`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `put_slide_save_as`")  # noqa: E501
        # verify the required parameter 'out_path' is set
        if not request.out_path:
            raise ValueError("Missing the required parameter `request.out_path` when calling `put_slide_save_as`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.out_path:
            query_params.append(('outPath', request.out_path))  # noqa: E501
        if request.width:
            query_params.append(('width', request.width))  # noqa: E501
        if request.height:
            query_params.append(('height', request.height))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.options:
            body_params = request.options


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/{format}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slide_shape_info(self, request, **kwargs):  # noqa: E501
        """Update shape properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_shape_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_shape_infoRequest request: put_slide_shape_info request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slide_shape_info_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slide_shape_info_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slide_shape_info_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update shape properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slide_shape_info_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slide_shape_infoRequest request: put_slide_shape_info request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slide_shape_info" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slide_shape_info`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_slide_shape_info`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `put_slide_shape_info`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/shapes/{path}/{shapeIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='ShapeBase',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slides_convert(self, request, **kwargs):  # noqa: E501
        """Convert presentation from request content to format specified.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_convert(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_convertRequest request: put_slides_convert request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slides_convert_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slides_convert_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slides_convert_with_http_info(self, request, **kwargs):  # noqa: E501
        """Convert presentation from request content to format specified.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_convert_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_convertRequest request: put_slides_convert request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slides_convert" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `put_slides_convert`")  # noqa: E501
        # verify the required parameter 'out_path' is set
        if not request.out_path:
            raise ValueError("Missing the required parameter `request.out_path` when calling `put_slides_convert`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.out_path:
            query_params.append(('outPath', request.out_path))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.document:
            body_params = request.document


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/octet-stream', 'multipart/form-data'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/convert/{format}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slides_document_from_html(self, request, **kwargs):  # noqa: E501
        """Update presentation document from html.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_document_from_html(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_document_from_htmlRequest request: put_slides_document_from_html request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slides_document_from_html_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slides_document_from_html_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slides_document_from_html_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update presentation document from html.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_document_from_html_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_document_from_htmlRequest request: put_slides_document_from_html request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slides_document_from_html" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slides_document_from_html`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.html:
            body_params = request.html


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/fromHtml', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Document',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slides_save_as(self, request, **kwargs):  # noqa: E501
        """Save a presentation to a specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_save_as(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_save_asRequest request: put_slides_save_as request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slides_save_as_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slides_save_as_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slides_save_as_with_http_info(self, request, **kwargs):  # noqa: E501
        """Save a presentation to a specified format.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_save_as_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_save_asRequest request: put_slides_save_as request object
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slides_save_as" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slides_save_as`")  # noqa: E501
        # verify the required parameter 'out_path' is set
        if not request.out_path:
            raise ValueError("Missing the required parameter `request.out_path` when calling `put_slides_save_as`")  # noqa: E501
        # verify the required parameter 'format' is set
        if not request.format:
            raise ValueError("Missing the required parameter `request.format` when calling `put_slides_save_as`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['format'] = request.format  # noqa: E501

        query_params = []
        if request.out_path:
            query_params.append(('outPath', request.out_path))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.fonts_folder:
            query_params.append(('fontsFolder', request.fonts_folder))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.options:
            body_params = request.options


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/{format}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slides_set_document_property(self, request, **kwargs):  # noqa: E501
        """Set document property.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_set_document_property(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_set_document_propertyRequest request: put_slides_set_document_property request object
        :return: DocumentProperty
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slides_set_document_property_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slides_set_document_property_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slides_set_document_property_with_http_info(self, request, **kwargs):  # noqa: E501
        """Set document property.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_set_document_property_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_set_document_propertyRequest request: put_slides_set_document_property request object
        :return: DocumentProperty
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slides_set_document_property" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slides_set_document_property`")  # noqa: E501
        # verify the required parameter 'property_name' is set
        if not request.property_name:
            raise ValueError("Missing the required parameter `request.property_name` when calling `put_slides_set_document_property`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['propertyName'] = request.property_name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request._property:
            body_params = request._property


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/documentproperties/{propertyName}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='DocumentProperty',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slides_slide(self, request, **kwargs):  # noqa: E501
        """Update a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_slide(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_slideRequest request: put_slides_slide request object
        :return: Slide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slides_slide_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slides_slide_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slides_slide_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_slide_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_slideRequest request: put_slides_slide request object
        :return: Slide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slides_slide" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slides_slide`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_slides_slide`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.slide_dto:
            body_params = request.slide_dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Slide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slides_slide_background(self, request, **kwargs):  # noqa: E501
        """Set background for a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_slide_background(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_slide_backgroundRequest request: put_slides_slide_background request object
        :return: SlideBackground
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slides_slide_background_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slides_slide_background_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slides_slide_background_with_http_info(self, request, **kwargs):  # noqa: E501
        """Set background for a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_slide_background_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_slide_backgroundRequest request: put_slides_slide_background request object
        :return: SlideBackground
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slides_slide_background" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slides_slide_background`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_slides_slide_background`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.background:
            body_params = request.background


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/background', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideBackground',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slides_slide_background_color(self, request, **kwargs):  # noqa: E501
        """Set background color for a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_slide_background_color(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_slide_background_colorRequest request: put_slides_slide_background_color request object
        :return: SlideBackground
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slides_slide_background_color_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slides_slide_background_color_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slides_slide_background_color_with_http_info(self, request, **kwargs):  # noqa: E501
        """Set background color for a slide.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_slide_background_color_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_slide_background_colorRequest request: put_slides_slide_background_color request object
        :return: SlideBackground
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slides_slide_background_color" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slides_slide_background_color`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_slides_slide_background_color`")  # noqa: E501
        # verify the required parameter 'color' is set
        if not request.color:
            raise ValueError("Missing the required parameter `request.color` when calling `put_slides_slide_background_color`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.color:
            query_params.append(('color', request.color))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/backgroundColor', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='SlideBackground',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_slides_slide_size(self, request, **kwargs):  # noqa: E501
        """Set slide size for a presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_slide_size(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_slide_sizeRequest request: put_slides_slide_size request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_slides_slide_size_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_slides_slide_size_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_slides_slide_size_with_http_info(self, request, **kwargs):  # noqa: E501
        """Set slide size for a presentation.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_slides_slide_size_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_slides_slide_sizeRequest request: put_slides_slide_size request object
        :return: Document
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_slides_slide_size" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_slides_slide_size`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.width:
            query_params.append(('width', request.width))  # noqa: E501
        if request.height:
            query_params.append(('height', request.height))  # noqa: E501
        if request.size_type:
            query_params.append(('sizeType', request.size_type))  # noqa: E501
        if request.scale_type:
            query_params.append(('scaleType', request.scale_type))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slideSize', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Document',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_update_notes_slide(self, request, **kwargs):  # noqa: E501
        """Update notes slide properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_update_notes_slide(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_update_notes_slideRequest request: put_update_notes_slide request object
        :return: NotesSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_update_notes_slide_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_update_notes_slide_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_update_notes_slide_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update notes slide properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_update_notes_slide_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_update_notes_slideRequest request: put_update_notes_slide request object
        :return: NotesSlide
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_update_notes_slide" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_update_notes_slide`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_update_notes_slide`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='NotesSlide',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_update_notes_slide_shape(self, request, **kwargs):  # noqa: E501
        """Update shape properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_update_notes_slide_shape(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_update_notes_slide_shapeRequest request: put_update_notes_slide_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_update_notes_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_update_notes_slide_shape_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_update_notes_slide_shape_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update shape properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_update_notes_slide_shape_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_update_notes_slide_shapeRequest request: put_update_notes_slide_shape request object
        :return: ShapeBase
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_update_notes_slide_shape" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_update_notes_slide_shape`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_update_notes_slide_shape`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `put_update_notes_slide_shape`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='ShapeBase',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_update_notes_slide_shape_paragraph(self, request, **kwargs):  # noqa: E501
        """Update paragraph properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_update_notes_slide_shape_paragraph(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_update_notes_slide_shape_paragraphRequest request: put_update_notes_slide_shape_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_update_notes_slide_shape_paragraph_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_update_notes_slide_shape_paragraph_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_update_notes_slide_shape_paragraph_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update paragraph properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_update_notes_slide_shape_paragraph_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_update_notes_slide_shape_paragraphRequest request: put_update_notes_slide_shape_paragraph request object
        :return: Paragraph
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_update_notes_slide_shape_paragraph" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_update_notes_slide_shape_paragraph`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_update_notes_slide_shape_paragraph`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `put_update_notes_slide_shape_paragraph`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `put_update_notes_slide_shape_paragraph`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Paragraph',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_update_notes_slide_shape_portion(self, request, **kwargs):  # noqa: E501
        """Update portion properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_update_notes_slide_shape_portion(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_update_notes_slide_shape_portionRequest request: put_update_notes_slide_shape_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.put_update_notes_slide_shape_portion_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.put_update_notes_slide_shape_portion_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def put_update_notes_slide_shape_portion_with_http_info(self, request, **kwargs):  # noqa: E501
        """Update portion properties.  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.put_update_notes_slide_shape_portion_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param put_update_notes_slide_shape_portionRequest request: put_update_notes_slide_shape_portion request object
        :return: Portion
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_update_notes_slide_shape_portion" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if not request.name:
            raise ValueError("Missing the required parameter `request.name` when calling `put_update_notes_slide_shape_portion`")  # noqa: E501
        # verify the required parameter 'slide_index' is set
        if not request.slide_index:
            raise ValueError("Missing the required parameter `request.slide_index` when calling `put_update_notes_slide_shape_portion`")  # noqa: E501
        # verify the required parameter 'shape_index' is set
        if not request.shape_index:
            raise ValueError("Missing the required parameter `request.shape_index` when calling `put_update_notes_slide_shape_portion`")  # noqa: E501
        # verify the required parameter 'paragraph_index' is set
        if not request.paragraph_index:
            raise ValueError("Missing the required parameter `request.paragraph_index` when calling `put_update_notes_slide_shape_portion`")  # noqa: E501
        # verify the required parameter 'portion_index' is set
        if not request.portion_index:
            raise ValueError("Missing the required parameter `request.portion_index` when calling `put_update_notes_slide_shape_portion`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['name'] = request.name  # noqa: E501
        path_params['slideIndex'] = request.slide_index  # noqa: E501
        path_params['path'] = request.path  # noqa: E501
        path_params['shapeIndex'] = request.shape_index  # noqa: E501
        path_params['paragraphIndex'] = request.paragraph_index  # noqa: E501
        path_params['portionIndex'] = request.portion_index  # noqa: E501

        query_params = []
        if request.password:
            query_params.append(('password', request.password))  # noqa: E501
        if request.folder:
            query_params.append(('folder', request.folder))  # noqa: E501
        if request.storage:
            query_params.append(('storage', request.storage))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}

        body_params = None
        if request.dto:
            body_params = request.dto


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/{name}/slides/{slideIndex}/notesSlide/shapes/{path}/{shapeIndex}/paragraphs/{paragraphIndex}/portions/{portionIndex}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='Portion',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def storage_exists(self, request, **kwargs):  # noqa: E501
        """Check if storage exists  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.storage_exists(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param storage_existsRequest request: storage_exists request object
        :return: StorageExist
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.storage_exists_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.storage_exists_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def storage_exists_with_http_info(self, request, **kwargs):  # noqa: E501
        """Check if storage exists  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.storage_exists_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param storage_existsRequest request: storage_exists request object
        :return: StorageExist
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method storage_exists" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'storage_name' is set
        if not request.storage_name:
            raise ValueError("Missing the required parameter `request.storage_name` when calling `storage_exists`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['storageName'] = request.storage_name  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        files = {}

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/{storageName}/exist', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='StorageExist',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def upload_file(self, request, **kwargs):  # noqa: E501
        """Upload file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.upload_file(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param upload_fileRequest request: upload_file request object
        :return: FilesUploadResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('is_async'):
            return self.upload_file_with_http_info(request, **kwargs)  # noqa: E501
        else:
            (data) = self.upload_file_with_http_info(request, **kwargs)  # noqa: E501
            return data

    def upload_file_with_http_info(self, request, **kwargs):  # noqa: E501
        """Upload file  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass is_async=True
        >>> thread = api.upload_file_with_http_info(request, is_async=True)
        >>> result = thread.get()

        :param is_async bool
        :param upload_fileRequest request: upload_file request object
        :return: FilesUploadResult
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('is_async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method upload_file" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'file' is set
        if not request.file:
            raise ValueError("Missing the required parameter `request.file` when calling `upload_file`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        path_params['path'] = request.path  # noqa: E501

        query_params = []
        if request.storage_name:
            query_params.append(('storageName', request.storage_name))  # noqa: E501

        header_params = {}

        form_params = []
        files = {}
        if request.file:
            files['file'] = request.file  # noqa: E501

        body_params = None


        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['multipart/form-data'])  # noqa: E501

        # Authentication setting
        auth_settings = ['JWT']  # noqa: E501

        return self.api_client.call_api(
            '/slides/storage/file/{path}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=files,
            response_type='FilesUploadResult',  # noqa: E501
            auth_settings=auth_settings,
            is_async=params.get('is_async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
