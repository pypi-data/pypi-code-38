# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines configuration for DataDriftDetector alerts."""
from azureml.contrib.datadrift._utils.parameter_validator import ParameterValidator


class AlertConfiguration:
    """Class for AzureML DataDriftDetector AlertConfiguration.

    AlertConfiguration class allows for setting configurable alerts (such as email) on DataDriftDetector jobs.
    """

    def __init__(self, email_addresses):
        """Constructor.

        Allows for setting configurable alerts (such as email) on DataDriftDetector jobs.
        :param email_addresses: List of email addresses to send DataDriftDetector alerts.
        :type email_addresses: list(str)
        """
        email_addresses = ParameterValidator.validate_email_addresses(email_addresses)
        self.email_addresses = email_addresses

    def __repr__(self):
        """Return the string representation of an AlertConfiguration object.

        :return: AlertConfiguration object string
        :rtype: str
        """
        return str(self.__dict__)
