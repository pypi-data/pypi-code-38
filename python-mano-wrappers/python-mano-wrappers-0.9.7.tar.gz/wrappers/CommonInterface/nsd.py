""" Common Interface - nsd

Reference interface to implement REST API Wrappers
for MANO Frameworks Defined according to the
ETSI GS NFV-SOL 005  V2.4.1 (2018-02). 

Defines abstract methods which are to be implemented
by the wrappers.
"""

from abc import ABC, abstractmethod


class CommonInterfaceNsd(ABC):
    """
    NSD Management Interfaces
        
    Base: {apiRoot}/nsd/v1
    """

    @abstractmethod
    def get_ns_descriptors(self):
        """ NSD Management Interface - NS Descriptors

        /ns_descriptors:
            GET - Query information about multiple
            NS descriptor resources.

        """
        pass

    @abstractmethod
    def post_ns_descriptors(self):
        """ NSD Management Interface - NS Descriptors

        /ns_descriptors:
            POST - Create a new NS descriptor resource.
        """
        pass

    @abstractmethod
    def get_ns_descriptors_nsdinfoid(self):
        """ NSD Management Interface -  Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}:
            Read information about an individual NS
            descriptor resource.
        """
        pass

    @abstractmethod
    def patch_ns_descriptors_nsdinfoid(self):
        """ NSD Management Interface - Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}:
            PATCH - Modify the operational state and/or 
            the user defined data of an individual
            NS descriptor resource.
        """
        pass

    def delete_ns_descriptors_nsdinfoid(self):
        """ NSD Management Interface - Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}:
            DELETE - Delete the content of NSD
        """
        pass

    @abstractmethod
    def get_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - NSD Content
        
        /ns_descriptors/{nsdInfoId}/nsd_c:
            GET - Fetch the content of a NSD.
        """
        pass

    @abstractmethod
    def put_ns_descriptors_nsd_content(self):
        """ NSD Management Interface - NSD Content
        
        /ns_descriptors/{nsdInfoId}/nsd_c:
            PUT - Upload the content of NSD
        """
        pass


    @abstractmethod
    def get_pnf_descriptors(self):
        """ NSD Management interface -
        PNF Descriptors

        /pnf_descriptors:
            GET - Query information about multiple
            PNF descriptor resources.

        """
        pass

    @abstractmethod
    def post_pnf_descriptors(self):
        """ NSD Management interface -
        PNF Descriptors

        /pnf_descriptors:
            POST - Create a new PNF descriptor resource.

        """
        pass

    @abstractmethod
    def get_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
        Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid:
            GET - Read an individual PNFD resource.

        """
        pass

    @abstractmethod
    def patch_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
        Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid:
            PATCH - Modify the user defined data of an 
            individual PNF descriptor resource.

        """
        pass

    @abstractmethod
    def delete_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        """ NSD Management interface -
        Individual PNF Descriptor

        /pnf_descriptors/pnfdinfoid:
            DELETE - Delete an individual PNF descriptor resource.

        """
        pass

    @abstractmethod
    def get_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        """ NSD Management interface -
        PNFD Content

        /pnf_descriptors/pnfdinfoid/pnfd_content:
            GET - Fetch the content of a PNFD.

        """
        pass

    @abstractmethod
    def put_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        """ NSD Management interface -
        PNFD Content

        /pnf_descriptors/pnfdinfoid/pnfd_content:
            PUT - Upload the content of a PNFD.

        """
        pass

    @abstractmethod
    def post_subscriptions(self, pnfdInfoId):
        """ NSD Management interface -
        Subscriptions

        /subscriptions:
            POST - Subscribe to NSD and PNFD change notifications.

        """
        pass

    @abstractmethod
    def get_subscriptions(self, subscriptionId):
        """ NSD Management interface -
        Subscriptions

        /subscriptions:
            GET - Query multiple subscriptions.

        """
        pass

    @abstractmethod
    def get_subscriptions_subscriptionid(self, subscriptionid):
        """ NSD Management interface -
        Individual Subscription

        /subscriptions/subscriptionId:
            GET - Read an individual subscription resource

        """
        pass

    @abstractmethod
    def delete_subscriptions_subscriptionid(self, subscriptionid):
        """ NSD Management interface -
        Individual Subscription

        /subscriptions/subscriptionId:
            DELETE - Terminate a subscription.

        """
        pass

