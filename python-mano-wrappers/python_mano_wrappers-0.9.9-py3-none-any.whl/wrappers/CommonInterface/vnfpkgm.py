""" Common Interface - vnfpkgm

Reference interface to implement REST API Wrappers
for MANO Frameworks Defined according to the
ETSI GS NFV-SOL 005  V2.4.1 (2018-02). 

Defines abstract methods which are to be implemented
by the wrappers.
"""

from abc import ABC, abstractmethod


class CommonInterfaceVnfPkgm(ABC):
    """
    VNF Package Management Interfaces

    Base: {apiRoot}/vnfpkgm/v1
    """

    @abstractmethod
    def get_vnf_packages(self):
        """ VNF Package Management Interface - VNF packages

        /vnf_packages:
            GET - Query VNF packages information

        """
        pass

    @abstractmethod
    def post_vnf_packages(self):
        """ VNF Package Management Interface - VNF packages

        /vnf_packages:
            POST - Create a new individual 
            VNFpackage resource

        """
        pass

    @abstractmethod
    def get_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
        Individual VNF package

        /vnf_packages/{vnfPkgId}:
            GET - Read information about an 
            individual VNF package
   
        """
        pass

    @abstractmethod
    def patch_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
        Individual VNF package

        /vnf_packages/{vnfPkgId}:
            PATCH - Update information about an
            individual VNF package

        """
        pass

    @abstractmethod
    def delete_vnf_packages_vnfpkgid(self, vnfPkgId):
        """ VNF Package Management Interface - 
        Individual VNF package

        /vnf_packages/{vnfPkgId}:
            DELETE - Delete an individual VNF package

        """
        pass

    @abstractmethod
    def get_vnf_packages_vnfpkgid_vnfd(self, vnfPkgId):
        """ VNF Package Management Interface - 
        VNFD of an individual VNF package

        /vnf_packages/{vnfPkgId}/vnfd:
            GET - Read VNFD of an on-boarded VNF package
   
        """
        pass

    @abstractmethod
    def get_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
        VNF package content

        /vnf_packages/{vnfPkgId}/package_content:
            GET - Fetch an on-boarded VNF package
   
        """
        pass

    @abstractmethod
    def put_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
        VNF package content

        /vnf_packages/{vnfPkgId}/package_content:
            PUT - Upload a VNF package by providing 
            the content of the VNF package
   
        """
        pass

    @abstractmethod
    def post_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        """ VNF Package Management Interface - 
        Upload VNF package from URI task

        /vnf_packages/{vnfPkgId}/package_content/upload_from_uri:
            POST - Upload a VNF package by providing
            the address information of the VNF package
   
        """
        pass

    @abstractmethod
    def get_vnf_packages_vnfpkgid_artifacts_artifactpath(self, 
            vnfPkgId, artifactPath):
        """ VNF Package Management Interface - 
        Individual VNF package artifact

        /vnf_packages/{vnfPkgId}/artifacts/{artifactPath}:
            GET - Fetch individual VNF package artifact
   
        """
        pass

    @abstractmethod
    def get_vnf_packages_subscriptions(self):
        """ VNF Package Management Interface - 
        Subscriptions

        /subscriptions:
            GET - Query multiple subscriptions
   
        """
        pass

    @abstractmethod
    def post_vnf_packages_subscriptions(self):
        """ VNF Package Management Interface - 
        Subscriptions

        /subscriptions:
            POST - Subscribe to notifications related
            to on-boarding and/or changes of VNF packages
   
        """
        pass