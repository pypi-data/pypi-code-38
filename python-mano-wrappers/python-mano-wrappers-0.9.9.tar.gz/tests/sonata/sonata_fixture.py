from pytest import fixture

@fixture
def auth_keys():
    return ['username', 'session_began_at', 'token']

@fixture
def get_vnf_packages_keys():
    return ['created_at', 'md5', 'signature', 'status', 'updated_at', 'username', 'vnfd', 'uuid']

@fixture
def get_ns_descriptors_keys():
    return ['created_at', 'md5', 'nsd', 'signature', 'status',
                'updated_at', 'username', 'uuid'] 

@fixture
def delete_ns_descriptors_keys():
    return ['']

@fixture
def post_ns_descriptors_keys():
    return ['id']

@fixture
def post_vnf_packages_keys():
    return ['id']

@fixture
def delete_ns_descriptors_nsdinfoid_keys():
    return ['']

@fixture
def delete_vnf_packages_vnfpkgid_keys():
    return ['']

@fixture
def get_vnf_packages_vnfpkgid_keys():
    return ['id']

@fixture
def post_ns_instances_nsinstanceid_terminate_keys():
    return ['id', 'created_at', 'updated_at', 'service_uuid', 'status', 'request_type', 'service_instance_uuid', 'began_at', 'callback']


@fixture
def post_ns_instances_nsinstanceid_instantiate_keys():
    return ['id', 'created_at', 'updated_at', 'service_uuid', 'status', 'request_type', 'service_instance_uuid', 'began_at', 'callback']

@fixture
def get_ns_instances_keys():
    return ['created_at', 'descriptor_reference', 'descriptor_version', 'network_functions', 'status', 'updated_at', 'version', 'uuid']
                
@fixture
def test_get_ns_instances_nsinstanceid_keys():
    return ['created_at', 'descriptor_reference', 'descriptor_version', 'network_functions', 'status', 'updated_at', 'version', 'uuid']

@fixture
def get_son_packages_keys():
    return ['created_at', 'grid_fs_id', 'grid_fs_name', 'md5', 'signature', 'updated_at', 'username', 'uuid']

@fixture
def post_son_packages_keys():
    return ['id']

@fixture
def delete_son_packages_PackageId_keys():
    return ['']

@fixture
def get_son_packages_PackageId_keys():
    return ['id']

@fixture
def get_user_list_keys():
    return ['username', 'uuid', 'created_at', 'user_type', 'email', 'last_name', 'first_name']

@fixture
def get_user_info_keys():
    return ['id']

@fixture
def get_nsinstances_records_keys():
    return ['created_at', 'descriptor_reference', 'descriptor_version', 'network_functions', 'status', 'updated_at', 'version', 'uuid']

@fixture
def get_nsinstances_records_instanceId_keys():
    return ['id']

@fixture
def get_vims_list_keys():
    return ['status', 'count', 'items', 'message']

@fixture
def get_instantions_requests_keys():
    return ['id', 'created_at', 'updated_at', 'service_uuid', 'status', 'request_type', 'service_instance_uuid', 'began_at', 'callback']

@fixture
def get_instantions_requests_requestId_keys():
    return ['id']

@fixture
def get_functions_keys():
    return ['created_at', 'md5', 'signature', 'status', 'updated_at', 'username', 'vnfd', 'uuid']

@fixture
def get_functions_functionId_keys():
    return ['id']

@fixture
def get_packages_keys():
    return ['descriptor_version', 'package_group', 'package_name', 'package_version', 'package_maintainer', 'package_description', 
    'entry_service_template', 'sealed', 'package_content', 'artifact_dependencies']

@fixture
def get_vnf_instances_keys():
    return ['created_at', 'descriptor_reference', 'descriptor_version', 'status', 'updated_at', 'version', 'virtual_deployment_units', 'uuid']

@fixture
def get_vnf_instances_vnfinstanceid_keys():
    return ['created_at', 'descriptor_reference', 'descriptor_version', 'status', 'updated_at', 'version', 'virtual_deployment_units', 'uuid']