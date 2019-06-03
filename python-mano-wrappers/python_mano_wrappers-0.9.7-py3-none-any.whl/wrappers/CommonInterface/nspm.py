""" Common Interface - nspm

Reference interface to implement REST API Wrappers
for MANO Frameworks Defined according to the
ETSI GS NFV-SOL 005  V2.4.1 (2018-02). 

Defines abstract methods which are to be implemented
by the wrappers.
"""

from abc import ABC, abstractmethod


class CommonInterfaceNspm(ABC):
    """
    NS Performance Management Interface

    Base: {apiRoot}/nspm/v1
    """

    @abstractmethod
    def get_pm_jobs(self):
        """ NS Performance Management Interface - 
        PM jobs

        /pm_jobs:
            GET - Query PM jobs

        """
        pass

    @abstractmethod
    def post_pm_jobs(self):
        """ NS Performance Management Interface - 
        PM jobs

        /pm_jobs:
            POST - Create a PM job

        """
        pass

    @abstractmethod
    def get_pm_jobs_pmjobid(self, pmJobId):
        """ NS Performance Management Interface - 
        Individual PM job

        /pm_jobs_pmjobid:
            GET - Read a single PM job

        """
        pass

    @abstractmethod
    def delete_pm_jobs_pmjobid(self, pmJobId):
        """ NS Performance Management Interface - 
        Individual PM job

        /pm_jobs_pmjobid:
            DELETE - Delete a PM job

        """
        pass

    @abstractmethod
    def get_pm_jobs_pmjobid_reports_reportid(self, pmJobId, reportId):
        """ NS Performance Management Interface - 
        Individual performance report

        /pm_jobs_pmjobid_reports_reportid:
            GET - Read an individual performance report

        """
        pass

    @abstractmethod
    def get_pm_thresholds(self):
        """ NS Performance Management Interface - 
        Thresholds

        /pm_thresholds:
            GET - Query thresholds

        """
        pass

    @abstractmethod
    def post_pm_thresholds(self):
        """ NS Performance Management Interface - 
        Thresholds

        /pm_thresholds:
            POST - Create a threshold

        """
        pass

    @abstractmethod
    def get_pm_thresholds_thresholdid(self, thresholdId):
        """ NS Performance Management Interface - 
        Individual threshold

        /pm_thresholds_thresholdid:
            GET - Query a single threshold

        """
        pass

    @abstractmethod
    def delete_pm_thresholds_thresholdid(self, thresholdId):
        """ NS Performance Management Interface - 
        Individual threshold

        /pm_thresholds_thresholdid:
            DELETE - Delete a threshold

        """
        pass

    @abstractmethod
    def get_pm_subscriptions(self):
        """ NS Performance Management Interface - 
        Subscriptions

        /pm_subscriptions:
            GET - Query PM related subscriptions

        """
        pass

    @abstractmethod
    def post_pm_subscriptions(self):
        """ NS Performance Management Interface - 
        Subscriptions

        /pm_subscriptions:
            POST - Subscribe to PM notifications

        """
        pass

    @abstractmethod
    def get_pm_subscriptions_subscriptionid(self, subscriptionId):
        """ NS Performance Management Interface - 
        Individual

        /pm_subscriptions_subscriptionid:
            GET - Query a single PM related subscription

        """
        pass

    @abstractmethod
    def delete_pm_subscriptions_subscriptionid(self, subscriptionId):
        """ NS Performance Management Interface - 
        Individual

        /pm_subscriptions_subscriptionid:
            DELETE - Terminate a subscription

        """
        pass

    # @abstractmethod
    # def get_unknown(self):
    #     """ NS Performance Management Interface - 
    #             Notification endpoint

    #     /unknown
    #         GET - Test the notification endpoint

    #     """
    #     pass

    # @abstractmethod
    # def post_unknown(self):
    #     """ NS Performance Management Interface - 
    #             Notification endpoint

    #     /unknown
    #         POST - Notify about PM related events

    #     """
    #     pass