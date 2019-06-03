""" Common Interface - nslcm

Reference interface to implement REST API Wrappers
for MANO Frameworks Defined according to the
ETSI GS NFV-SOL 005  V2.4.1 (2018-02). 

Defines abstract methods which are to be implemented
by the wrappers.
"""

from abc import ABC, abstractmethod

class CommonInterfaceNslcm(ABC):
    """
    Lifecycle Management interface

    Base: {apiRoot}/nslcm/v1
    """

    @abstractmethod
    def get_ns_instances(self):
        """  NS Lifecycle Management interface - 
        NS instances

        /ns_instances:
            GET - Query multiple NS instances.

        """
        pass


    @abstractmethod
    def post_ns_instances(self):
        """  NS Lifecycle Management interface - 
        NS instances

        /ns_instances:
            POST - Create a NS instance resource.

        """
        pass


    @abstractmethod
    def get_ns_instances_nsinstanceid(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
        Individual NS instance

        /ns_instances_nsinstanceid:
            GET - Read an individual NS instance resource.

        """
        pass


    @abstractmethod
    def delete_ns_instances_nsinstanceid(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
        Individual NS instance

        /ns_instances_nsinstanceid:
            DELETE - Delete NS instance resource.

        """
        pass


    @abstractmethod
    def post_ns_instances_nsinstanceid_instantiate(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
        Instantiate NS task

        /ns_instances_nsinstanceid_instantiate:
            POST - Instantiate a NS instance.

        """
        pass


    @abstractmethod
    def post_ns_instances_nsinstanceid_scale(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
        Scale NS task

        /ns_instances_nsinstanceid_scale:
            POST - Scale a NS instance.

        """
        pass


    @abstractmethod
    def post_ns_instances_nsinstanceid_update(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
        Update NS task

        /ns_instances_nsinstanceid_update:
            POST - Updates a NS instance.

        """
        pass


    @abstractmethod
    def post_ns_instances_nsinstanceid_terminate(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
        Terminate NS task

        /ns_instances_nsinstanceid_terminate:
            POST - Terminate a NS instance.

        """
        pass


    @abstractmethod
    def post_ns_instances_nsinstanceid_heal(self, nsInstanceId):
        """  NS Lifecycle Management interface - 
        Heal NS task

        /ns_instances_nsinstanceid_heal:
            POST - Heal a NS instance.

        """
        pass


    @abstractmethod
    def get_ns_lcm_op_ops(self):
        """  NS Lifecycle Management interface - 
        NS lifecycle operation occurrences

        /ns_lcm_op_ops:
            GET - Query multiple NS LCM operation occurrences.

        """
        pass


    @abstractmethod
    def get_ns_lcm_op_ops_nslcmopoccid(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
        Individual NS lifecycle operation occurrence

        /ns_lcm_op_ops_nslcmopoccid:
            GET - Read an individual NS LCM operation occurrence resource.

        """
        pass


    @abstractmethod
    def post_ns_lcm_op_occs_nslcmopoccid_retry(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
        Retry operation task

        /ns_lcm_op_occs_nslcmopoccid_retry:
            POST - Retry a NS lifecycle management operation occurrence.

        """
        pass


    @abstractmethod
    def post_ns_lcm_op_occs_nslcmopoccid_rollback(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
        Rollback operation task

        /ns_lcm_op_occs_nslcmopoccid_rollback:
            POST - Rollback a NS lifecycle management operation occurrence.

        """
        pass


    @abstractmethod
    def post_ns_lcm_op_occs_nslcmopoccid_continue(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
        Continue operation task

        /ns_lcm_op_occs_nslcmopoccid_continue:
            POST - Continue a NS lifecycle management operation occurrence.

        """
        pass


    @abstractmethod
    def post_ns_lcm_op_occs_nslcmopoccid_fail(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
        Fail operation task

        /ns_lcm_op_occs_nslcmopoccid_fail:
            POST - Mark a NS lifecycle management operation occurrence as failed.

        """
        pass


    @abstractmethod
    def post_ns_lcm_op_occs_nslcmopoccid_cancel(self, nsLcmOpOccId):
        """  NS Lifecycle Management interface - 
        Cancel operation task

        /ns_lcm_op_occs_nslcmopoccid_cancel:
            POST - Cancel a NS lifecycle management operation occurrence.

        """
        pass


    @abstractmethod
    def post_ns_lcm_subscriptions(self):
        """  NS Lifecycle Management interface - 
        Subscriptions

        /ns_lcm_subscriptions:
            POST - Subscribe to NS lifecycle change notifications.

        """
        pass


    @abstractmethod
    def get_ns_lcm_subscriptions(self):
        """  NS Lifecycle Management interface - 
        Subscriptions

        /ns_lcm_subscriptions:
            GET - Query multiple subscriptions.

        """
        pass


    @abstractmethod
    def get_ns_lcm_subscriptions_subscriptionid(self, subscriptionId):
        """  NS Lifecycle Management interface - 
        Individual subscription

        /ns_lcm_subscriptions_subscriptionid:
            GET - Read an individual subscription resource.

        """
        pass


    @abstractmethod
    def delete_ns_lcm_subscriptions_subscriptionid(self, subscriptionId):
        """  NS Lifecycle Management interface - 
        Individual subscription

        /ns_lcm_subscriptions_subscriptionid:
            DELETE - Terminate a subscription.

        """
        pass


    # @abstractmethod
    # def get_unknown(self):
    #     """  NS Lifecycle Management interface - 
    #             Notification endpoint

    #     /unknown
    #         GET - Test the notification endpoint.

    #     """
    #     pass


    # @abstractmethod
    # def post_unknown(self):
    #     """  NS Lifecycle Management interface - 
    #             Notification endpoint

    #     /unknown
    #         POST - Notify about NS lifecycle change.

    #     """
    #     pass
