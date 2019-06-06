import json
from wrappers import SONATAClient 
from wrappers.SONATAClient.auth import Auth
from wrappers.SONATAClient.vnfpkgm import VnfPkgm
from wrappers.SONATAClient.nsd import Nsd
from tests.sonata.config import *
import time
class Helpers():

    def _upload_test_vnf(_token):
        time.sleep(5)
        sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
        response = json.loads(sonata_vnfpkgm.post_vnf_packages(token=_token,
                            package_path="tests/samples/vnfd_example.yml"))
        
        if response["error"]:
            return True
        else:
            return False

    def _delete_test_vnf(_token, vnfname="vnfd_example"):
        time.sleep(5)
        sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)

        _vnfd_list = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token))
        _vnfd_list = json.loads(_vnfd_list["data"])

        _vnfd = None
        for _v in _vnfd_list:
            if "vnfd_example" == _v['uuid']:            
                _vnfd = _v['uuid']

        response = None
        if _vnfd:
            response = json.loads(sonata_vnfpkgm.delete_vnf_packages_vnfpkgid(
                                    token=_token,
                                    vnfPkgId=_vnfd))

    def _upload_test_nsd(_token):
        time.sleep(5)
        sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
        sonata_nsd = Nsd(HOST_URL)

        sonata_vnfpkgm.post_vnf_packages(token=_token,
             package_path="tests/samples/vnfd_example.yml")
        
        response = json.loads(sonata_nsd.post_ns_descriptors(token=_token,
                        package_path="tests/samples/nsd_example.yml"))
        if response["error"]:
            return True
        else:
            return False

    def _delete_test_nsd(_token, nsdname="sonata-demo"):
        time.sleep(5)
        sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
        sonata_nsd = Nsd(HOST_URL)
    
        _nsd_list = json.loads(sonata_nsd.get_ns_descriptors(token=_token))
        _nsd_list = json.loads(_nsd_list["data"])

        _nsd = None
        for _n in _nsd_list:
           if "sonata-demo" == _n['nsd']['name']:
            _nsd = _n['uuid']

        time.sleep(10)
        response = json.loads(sonata_nsd.delete_ns_descriptors_nsdinfoid(
                                token=_token,
                                nsdinfoid=_nsd))

        time.sleep(5)

        _vnfd_list = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token))
        _vnfd_list = json.loads(_vnfd_list["data"])

        _vnfd = None
        for _v in _vnfd_list:
            if "vnfd_example" == _v['uuid']:            
                _vnfd = _v['uuid']

        response = None
        if _vnfd:
            response = json.loads(sonata_vnfpkgm.delete_vnf_packages_vnfpkgid(
                                token=_token,
                                vnfPkgId=_vnfd))

    
    def _upload_test_package(_token):
        time.sleep(5)
        sonata_package = SONATAClient.Package(HOST_URL)

        response = json.loads(sonata_package.post_son_packages(token=_token,
                        package_path="tests/samples/sonata_example.son"))
        
        if response["error"]:
            return True
        else:
            return False

    def _delete_test_package(_token):
        time.sleep(5)
        sonata_package = SONATAClient.Package(HOST_URL)

        _package_list = json.loads(sonata_package.get_son_packages(token=_token))
        _package_list = json.loads(_package_list["data"])

        _package = None
        for _p in _package_list:
            if "sonata_example.son" == _p['grid_fs_name']:
                _package = _p['uuid']

        response = None
        if _package:
            response = json.loads(sonata_package.delete_son_packages_PackageId(
                                    token=_token,
                                    id=_package))