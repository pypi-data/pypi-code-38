from pytest import fixture

@fixture
def auth_keys():
    return ['_id', 'project_id', 'admin', 'expires',
                'id', 'issued_at', 'remote_port',
                'username', 'remote_host']

@fixture
def get_ns_descriptors_keys():
    return ['id']

@fixture
def delete_ns_descriptors_nsdinfoid_keys():
    return ['']

@fixture
def post_ns_descriptors_keys():
    return ['id']

@fixture
def get_vnf_packages_keys():
    return ['name', 'id', '_id', 'description']

@fixture
def post_vnf_packages_keys():
    return ['id']

@fixture
def get_vnf_packages_vnfpkgid_keys():
    return ['id']

@fixture
def delete_vnf_packages_vnfpkgid_keys():
    return ['']

@fixture
def get_ns_instances_keys():
    return ['name', '_id']

@fixture
def post_ns_instances_nsinstanceid_terminate_keys():
    return['_id']

@fixture
def get_ns_lcm_op_ops_keys():
    return['operationParams', 'isAutomaticInvocation', 'links', 'operationState', 
            'id', '_id', 'isCancelPending', 'startTime', 'nsInstanceId', '_admin', 
              'statusEnteredTime', 'lcmOperationType', 'detailed-status']

@fixture
def get_ns_lcm_op_ops_nslcmopoccid_keys():
    return['operationParams', 'isAutomaticInvocation']

@fixture
def post_ns_instances_nsinstanceid_instantiate_keys():
    return['id']

@fixture
def get_user_list_keys():
  return ['_id', 'password', 'username', '_admin', 'projects']

@fixture()
def get_user_info_keys():
  return['_id', 'password', 'username', '_admin', 'projects']

@fixture()
def get_project_list_keys():
  return['_id', 'name', '_admin']

@fixture()
def get_project_info_keys():
  return['_id', 'name', '_admin']

@fixture()
def get_vim_list_keys():
  return ['_id', 'vim_user', 'name', '_admin', 'vim_password', 'vim_url', 
            'vim_type', 'vim_tenant_name', 'schema_version', 'config']
  
@fixture
def get_vim_info_keys():
  return ['_id', 'vim_user', 'name', '_admin', 'vim_password', 'vim_url', 
            'vim_type', 'vim_tenant_name', 'schema_version', 'config']

@fixture
def get_vnf_instances_keys():
    return ['_id', 'member-vnf-index-ref', '_admin', 'id', 'vnfd-ref', 'vnfd-id', 'ip-address', 'vim-account-id', 'created-time', 'vdur', 'nsr-id-ref', 'connection-point']

@fixture
def get_vnf_instances_vnfinstanceid_keys():
    return ['_id', 'member-vnf-index-ref', '_admin', 'id', 'vnfd-ref', 'vnfd-id', 'ip-address', 'vim-account-id', 'created-time', 'vdur', 'nsr-id-ref', 'connection-point']
    