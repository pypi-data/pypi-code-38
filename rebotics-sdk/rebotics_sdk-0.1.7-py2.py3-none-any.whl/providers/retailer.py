import json

import six

from rebotics_sdk.utils import accept_file
from .base import ReboticsBaseProvider, remote_service, PageResult
from ..utils import hash_file


class RetailerProvider(ReboticsBaseProvider):
    @remote_service('/api/v4/')
    def api_v4_root(self, **kwargs):
        return self.session.get()

    @remote_service('/api/v4/version/')
    def version(self, *kwargs):
        return self.session.get()

    @remote_service('/api/v4/token-auth/')
    def token_auth(self, username, password):
        json_data = self.session.post(data={
            'username': username,
            'password': password
        })
        self.set_token(json_data['token'])
        return json_data

    def api_login(self, username, password):
        return self.token_auth(username, password)

    def get_token(self, username, password):
        response = self.api_login(username, password)
        return response['token']

    @remote_service('/api/v4/processing/actions/{id}/requeue/')
    def requeue(self, processing_action_id, requeue_type=None):
        data = {}

        if requeue_type is not None:
            data['requeue_type'] = requeue_type

        return self.session.post(id=processing_action_id, data=data)

    @remote_service('/api/v4/processing/actions/{id}/cancel/')
    def cancel(self, processing_action_id):
        return self.session.post(id=processing_action_id)

    @remote_service('/api/v4/processing/actions/{id}/')
    def processing_action_detail(self, processing_action_id):
        return self.session.get(id=processing_action_id)

    @remote_service('/api/v4/processing/actions/')
    def create_processing_action(
        self, store_id, files, input_type='image',
        store_planogram=None,
        aisle=None, section=None,
        klt_json=None, lens_used=None,
    ):
        """
        Create processing action for store using list of files
        :param int store_id:
        :param list<int> files:
        :param str input_type:
        :param int store_planogram:
        :param str aisle:
        :param str section:
        :param klt_json:
        :param lens_used:
        :return:
        """
        for f_ in files:
            assert isinstance(f_, int), "Should send IDs of uploaded files"

        assert input_type in ('video', 'image', 'keyframe')

        data = {
            'store': store_id,
            'files': files,
            'input_type': input_type
        }
        if store_planogram:
            assert isinstance(store_planogram, int)
            data['store_planogram'] = store_planogram
        if aisle:
            assert isinstance(aisle, six.string_types)
            data['aisle'] = aisle
        if section:
            assert isinstance(section, six.string_types)
            data['section'] = section

        if klt_json:
            # encode KLT to string as it is accepted in API
            if isinstance(klt_json, dict):
                klt = json.dumps(klt_json)
            elif isinstance(klt_json, six.string_types):
                klt = klt_json
            else:
                # TODO: add path support and IO support
                raise ValueError('Unsupported value type for KLT.jsons')
            data['klt_json'] = klt

        if lens_used is not None:
            data['lens_used'] = lens_used
        return self.session.post(data=data)

    @remote_service('/api/v4/processing/upload/')
    def processing_upload(self, store_id, input_file, input_type='image'):
        """Upload files that can be used for processing action creation"""
        assert isinstance(store_id, int), 'You need to specify store_id as int'
        assert input_type in (
            'image', 'video', 'keyframe'
        ), "File type should one of (image|video|keyframe) not %s" % input_type

        checksum = hash_file(input_file)
        input_file.seek(0)

        return self.session.post(data={
            'checksum': checksum,
            'input_type': input_type,
            'store': store_id
        }, files={
            'file': input_file
        })

    @remote_service('/api/v4/export/products/')
    def export_products(self, products_filter=None, page=1):
        params = {
            'page': page,
        }
        if products_filter:
            params['filter'] = products_filter
        return PageResult(self.session.get(params=params))

    @remote_service('/api/v4/export/products/{product_id}/previews/')
    def get_product_previews(self, product_id, is_removed=None, page=1):
        params = {
            'page': page,
        }
        if is_removed:
            assert isinstance(is_removed, bool)
            params['is_removed'] = is_removed

        return PageResult(self.session.get(
            product_id=product_id,
            url=self.session.host,
            params=params
        ))

    @remote_service('/api/v4/export/products/previews/', timeout=30000)
    def get_product_previews_bulk(self, product_id_list):
        filter_params = {'id': product_id_list}
        return self.session.post(data=filter_params)

    @remote_service('/api/v4/products/previews/')
    def upload_product_preview(self, upc, image_file):
        return self.session.post(data={
            'product_unique_id': upc,
        }, files={
            'image': image_file,
        })

    @remote_service('/api/v4/products/previews/delete/')
    def delete_product_previews(self, upc):
        return self.session.post(data={
            'product_unique_id': upc
        })

    @remote_service('/api/v4/product/previews/{preview_id}/add_feature_reference/')
    def set_product_preview_feature_id(self, preview_id, feature_id, facenet):
        return self.session.post(
            preview_id=preview_id,
            data={
                'feature_id': feature_id,
                'facenet': facenet,
            }
        )

    @remote_service('/api/v4/processing/actions/')
    def get_processing_action_list(self, store=None, status=None, page=1, page_size=100):
        """Request processing action list"""
        params = {
            'page': page,
            'page_size': page_size,
        }
        if store:
            params['store'] = store

        if status:
            params['status'] = status

        data = self.session.get(params=params)
        return PageResult(data)

    @remote_service('api/v4/imports/planogram/assign/')
    def assign_planogram_with_file(self, assign_file, deactivate_old_planograms=False):

        file_io = None

        result = self.session.post(data={
            'deactivate_old_planograms': deactivate_old_planograms
        }, files={
            assign_file: file_io
        })

        file_io.close()
        return result

    @remote_service('api/v4/imports/planogram/')
    def import_planogram(
        self,
        planogram_file, title, description='',
        mappings=None,
        vertical_direction='top-to-bottom',
        horizontal_direction='left-to-right',
        horizontal_direction_shelf_bay='left-to-right',
        is_zig_zag=False,
        convert_upc=False,
    ):
        """
        This will also close your file after transmission

        :param planogram_file: Planogram file as path, as StringIO/ByteIO, as URL
        :param str title: Planogram title, that you can use
        :param str description:
        :param dict mappings:
        :param str vertical_direction:
        :param str horizontal_direction:
        :param str horizontal_direction_shelf_bay:
        :param bool is_zig_zag:
        :param bool convert_upc: This flag will indicate that we need to convert what ever UPC to UPC-A format.
                                Please do not check if you provide EAN or other than UPC code.
        :return:
        """
        schema = self.session.post()
        post_schema = schema['actions']['POST']
        mapping_fields = post_schema['mappings']['children']
        option_fields = post_schema['options']['children']
        default_required_mappings = {key: key for key, value in mapping_fields.items() if value['required']}
        if mappings is None:
            mappings = default_required_mappings

        assert isinstance(mappings, dict)
        for key, value in mappings.items():
            if key not in default_required_mappings:
                raise AssertionError('You have not provided required key %s for API' % key)

        def get_choice_values(fields, key):
            return (choice['value'] for choice in fields[key]['choices'])

        assert vertical_direction in get_choice_values(option_fields, 'vertical_direction')
        assert horizontal_direction in get_choice_values(option_fields, 'horizontal_direction')
        assert horizontal_direction_shelf_bay in get_choice_values(option_fields, 'horizontal_direction_shelf_bay')
        assert isinstance(is_zig_zag, bool)
        assert isinstance(convert_upc, bool)
        assert isinstance(title, str), 'You need to specify title, instead %s with type %s was provided' % (
            title, type(title))
        assert isinstance(description, str), 'You need to specify description'

        file_io = accept_file(self, planogram_file)

        file_io.seek(0)

        response = self.session.post(json={
            'mappings': mappings,
            'options': {
                'vertical_direction': vertical_direction,
                'horizontal_direction': horizontal_direction,
                'horizontal_direction_shelf_bay': horizontal_direction_shelf_bay,
                'is_zig_zag': is_zig_zag,
                'convert_upc': convert_upc,
            },
            'title': title,
            'description': description,
        },
            files={
                'planogram_file': file_io
            })
        file_io.close()

        return response

    @remote_service('api/v4/imports/planogram-assign-file/')
    def assign_planogram(self, assign_file, deactivate=False):
        """
        Uploads an assign planogram file to retailer. Be careful to upload it.
        :param assign_file: file-like object
        :param bool deactivate: flag to deactivate old existing store planograms
        :return:
        """
        assert isinstance(deactivate, bool)
        file_io = accept_file(self, assign_file)
        file_io.seek(0)

        response = self.session.post(data={
            'deactivate_old_planogram': deactivate
        }, files={
            'assign_file': file_io
        })

        file_io.close()
        return response
