""" Common Interface - nsfm

Reference interface to implement REST API Wrappers
for MANO Frameworks Defined according to the
ETSI GS NFV-SOL 005  V2.4.1 (2018-02). 

Defines abstract methods which are to be implemented
by the wrappers.
"""

from abc import ABC, abstractmethod


class CommonInterfaceNsfm(ABC):
    """
    NS Fault Management interface

    Base: {apiRoot}/nsfm/v1
    """

    @abstractmethod
    def get_nsfm_alarms(self):
        """  NS Fault Management interface - 
        Alarms

        /nsfm_alarms:
            GET - Query alarms related to NS instances.

        """
        pass


    @abstractmethod
    def get_nsfm_alarms_alarmid(self, alarmId):
        """  NS Fault Management interface - 
        Individual alarm

        /nsfm_alarms_alarmid:
            GET - Read individual alarm.

        """
        pass


    @abstractmethod
    def patch_nsfm_alarms_alarmid(self, alarmId):
        """  NS Fault Management interface - 
        Individual alarm

        /nsfm_alarms_alarmid:
            PATCH - Acknowledge individual alarm.

        """
        pass


    @abstractmethod
    def get_nsfm_subscriptions(self):
        """  NS Fault Management interface - 
        Subscriptions

        /nsfm_subscriptions:
            GET - Query multiple subscriptions.

        """
        pass


    @abstractmethod
    def post_nsfm_subscriptions(self):
        """  NS Fault Management interface - 
        Subscriptions

        /nsfm_subscriptions:
            POST - Subscribe to alarms related to NSs.

        """
        pass


    @abstractmethod
    def get_nsfm_subscriptions_subscriptionid(self, subscriptionId):
        """  NS Fault Management interface - 
        Individual subscription

        /nsfm_subscriptions_subscriptionid:
            GET - Read an individual subscription.

        """
        pass


    @abstractmethod
    def delete_nsfm_subscriptions_subscriptionid(self, subscriptionId):
        """  NS Fault Management interface - 
        Individual subscription

        /nsfm_subscriptions_subscriptionid:
            DELETE - Terminate a subscription.

        """
        pass


    # @abstractmethod
    # def get_nsfm_unknown(self):
    #     """  NS Fault Management interface - 
    #             Notification endpoint

    #     /nsfm_unknown
    #         GET - Test the notification endpoint.

    #     """
    #     pass


    # @abstractmethod
    # def post_nsfm_unknown(self):
    #     """  NS Fault Management interface - 
    #             Notification endpoint

    #     /nsfm_unknown
    #         POST - Notify about NS alarms.

    #     """
    #     pass
