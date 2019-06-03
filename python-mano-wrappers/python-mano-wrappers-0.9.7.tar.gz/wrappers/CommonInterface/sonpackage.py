""" Common Interface - nslcm

Reference interface to implement REST API Wrappers
for MANO Frameworks Defined according to the
ETSI GS NFV-SOL 005  V2.4.1 (2018-02). 

Defines abstract methods which are to be implemented
by the wrappers.
"""

from abc import ABC, abstractmethod

class CommonInterfaceSonPackage(ABC):

    @abstractmethod
    def get_son_packages(self):
        """  Receive the list of stored packages
        """
        pass


    @abstractmethod
    def post_son_packages(self):
        """  Send a particular package

        """
        pass

    @abstractmethod
    def delete_son_packages_PackageId(self, PackageId):
        """  Delete a particular sonata package

        """
        pass

    @abstractmethod
    def get_son_packages_PackageId(self, PackageId):
        """  Receive a particular stored packages
        """
        pass
    

    


