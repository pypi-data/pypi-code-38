import pytest
from mlcore.datahelper.s3.mllearningdb.s3_path_helper import RawDataPathHelper


class TestRawDataPathHelper:
    # def test_get_rawdata_key(self):
    #     assert RawDataPathHelper().get_rawdata_key('vm_list') == 'vm-list'

    def test_get_dirs_by_name(self):
        path = RawDataPathHelper().get_dirs_by_name('vm_list')
        assert path is not None
        assert 's3folder' in path
        assert 'local_dir' in path
        assert 's3prefix' in path
        assert 'local_prefix' in path

        s3_root_dir = RawDataPathHelper().s3_root_dir
        assert s3_root_dir in path['s3folder'] 
        assert s3_root_dir in path['s3prefix'] 
        local_root_dir = RawDataPathHelper().local_root_dir
        assert local_root_dir in path['local_dir'] 
        assert local_root_dir in path['local_prefix'] 