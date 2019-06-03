import json
import time
from wrappers import OSMClient 
from .config import *
class Helpers():

    def _upload_test_vnf():
        time.sleep(3) # Wait 
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        response = json.loads(osm_vnfpkgm.post_vnf_packages(token=_token["id"],
                            package_path="tests/samples/test_osm_cirros_vnfd.tar.gz"))
        if response["error"]:
            return True
        else:
            return False

    def _delete_test_vnf(vnfname="test_osm_cirros_vnfd"):
        time.sleep(3) # Wait 
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        _vnfd_list = json.loads(osm_vnfpkgm.get_vnf_packages(token=_token["id"]))
        _vnfd_list = json.loads(_vnfd_list["data"])

        _vnfd = None
        for _v in _vnfd_list:
            if vnfname == _v['id']:            
                _vnfd = _v['_id']

        response = None
        if _vnfd:
            response = json.loads(osm_vnfpkgm.delete_vnf_packages_vnfpkgid(
                                    token=_token["id"], 
                                    vnfPkgId=_vnfd))

    def _upload_test_nsd():
        time.sleep(3) # Wait 
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_nsd = OSMClient.Nsd(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        osm_vnfpkgm.post_vnf_packages(token=_token["id"],
             package_path="tests/samples/test_osm_cirros_vnfd.tar.gz")

        response = json.loads(osm_nsd.post_ns_descriptors(token=_token["id"],
                        package_path="tests/samples/test_osm_cirros_nsd.tar.gz"))
        if response["error"]:
            return True
        else:
            return False

    def _delete_test_nsd(nsdname="test_osm_cirros_2vnf_nsd"):
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_nsd = OSMClient.Nsd(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        _nsd_list = json.loads(osm_nsd.get_ns_descriptors(token=_token["id"]))
        _nsd_list = json.loads(_nsd_list["data"])

        _nsd = None
        for _n in _nsd_list:
            if "test_osm_cirros_2vnf_nsd" == _n['id']:            
                _nsd = _n['_id']

        time.sleep(10) # Wait for NSD onboarding
        response = json.loads(osm_nsd.delete_ns_descriptors_nsdinfoid(
                                token=_token["id"], 
                                nsdinfoid=_nsd))

        time.sleep(2) # Wait for NSD onboarding

        _vnfd_list = json.loads(osm_vnfpkgm.get_vnf_packages(token=_token["id"]))
        _vnfd_list = json.loads(_vnfd_list["data"])

        _vnfd = None
        for _v in _vnfd_list:
            if nsdname == _v['id']:            
                _vnfd = _v['_id']

        response = None
        if _vnfd:
            response = json.loads(osm_vnfpkgm.delete_vnf_packages_vnfpkgid(
                                    token=_token["id"], 
                                    vnfPkgId=_vnfd))

    def _upload_reference_vnfd_for_nsd(_referencevnfdname="test_osm_cirros_vnfd"):
        time.sleep(3) # Wait 
        osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        if _referencevnfdname:
            response = json.loads(osm_vnfpkgm.post_vnf_packages(token=_token["id"],
                            package_path="tests/samples/test_osm_cirros_vnfd.tar.gz"))
        if response["error"]:
            return True
        else:
            return False
    
    def _upload_test_ns_instance():
        time.sleep(3) # Wait 
        osm_nslcm = OSMClient.Nslcm(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])

        response = json.loads(osm_nslcm.post_ns_instances(token=_token["id"],
                        nsDescription = NSDESCRIPTION, nsName = NSNAME, 
                        nsdId = NSDID, vimAccountId = VIMACCOUNTID))
        response = json.loads(response["data"])
        
        
    def _delete_test_ns_instance():
        time.sleep(3) # Wait 
        osm_nslcm = OSMClient.Nslcm(HOST_URL)
        osm_auth = OSMClient.Auth(HOST_URL)
        _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
        _token = json.loads(_token["data"])
        _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
        _ns_list = json.loads(_ns_list["data"])

        _ns = None
        for _n in _ns_list:
            if "test" == _n['short-name']:            
                _ns = _n['_id']
        # time.sleep(5) #wait for NS Creation
        response = None
        if _ns:
            response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_terminate(
                                    token=_token["id"], 
                                    nsInstanceId=_ns))
            _rid = response["data"]
        

        



    
            