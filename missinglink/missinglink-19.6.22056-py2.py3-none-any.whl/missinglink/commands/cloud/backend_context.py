from missinglink.crypto import Asymmetric
from missinglink.commands.utilities import TupleArray


class BackendContext(object):
    def __init__(self, ctx, kwargs):
        self.org = kwargs['org']
        self.ctx = ctx

    def change_local_server(self, server, new_group):
        return self._handle_api_call('put', '{}/resource/{}/change_local_group'.format(self.org, server), {'group': new_group})

    def create_queue(self, name, updates):
        updates['display'] = name
        return self._queue_action(name, method='post', updates=updates)

    def update_queue(self, name, updates):
        return self._queue_action(name, method='put', updates=updates)

    def get_queue(self, name):
        return self._queue_action(name, method='get')

    def _queue_action(self, queue_id, method='get', updates=None):
        url = '{}/queue/{}'.format(self.org, queue_id)
        return self._handle_api_call(method, url, data=updates)

    @classmethod
    def b64encode_name(cls, group_name):
        return Asymmetric.bytes_to_b64str(group_name.encode('utf-8'))

    def resource_group_description(self, group_id):
        group_description = self._handle_api_call('get', '{}/aws/resource_group/{}?b64name=True'.format(self.org, self.b64encode_name(group_id)))

        return {k.pop('key'): k for k in group_description['data']}

    def put_resource_group_parameters(self, group_id, params, new_cloud_type=None):
        data = TupleArray.dict_to_tuple_array(params, key='key', value='values')
        is_new = new_cloud_type is not None
        if not is_new:
            new_cloud_type = 'all'
        group_description = self._handle_api_call(
            'post' if is_new else 'put',
            '{}/{}/resource_group/{}?b64name=True'.format(self.org, new_cloud_type, self.b64encode_name(group_id)),
            data={'params': data})

        return {k.pop('key'): k for k in group_description['data']}

    def _handle_api_call(self, method, url, data=None):
        from missinglink.core.api import ApiCaller

        return ApiCaller.call(self.ctx.obj, self.ctx.obj.session, method, url, data)

    def _update_org_metadata_ssh_key(self, ssh_key_pub):
        url = 'orgs/{org}/metadata'.format(org=self.org)

        metadata_request = {
            'metadata': [
                {
                    'name': 'ssh_public_key',
                    'value': ssh_key_pub,
                    'operation': 'REPLACE'
                }
            ]
        }
        self._handle_api_call('post', url, metadata_request)

    @classmethod
    def encrypt(cls, kms, data):
        return kms.convert_encrypted_envelope_data_to_triple(kms.encrypt(data))

    @classmethod
    def decrypt(cls, kms, data):
        if len(data) == 3:
            iv, key, en_data = data
            return kms.decrypt(kms.convert_triple_to_encrypted_envelope_data({'iv': iv, 'key': key, 'data': en_data}))
