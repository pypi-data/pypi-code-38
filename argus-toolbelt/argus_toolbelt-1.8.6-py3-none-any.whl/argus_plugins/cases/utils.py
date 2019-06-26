"""This is a helper module for all things case related"""
import time
from datetime import datetime

from argus_api.api.customers.v1.customer import get_customer_by_shortname

STATUSES = ["pendingCustomer", "pendingSoc", "pendingVendor", "workingSoc", "workingCustomer", "pendingClose", "closed"]
CASE_TYPES = ["securityIncident", "operationalIncident", "informational", "change"]
PRIORITIES = ["low", "medium", "high", "critical"]
KEYWORD_FIELDS = ["subject", "description", "comments", "id", "all"]


def customer_from_shortname(name: str) -> dict:
    customer = get_customer_by_shortname(shortName=name.lower())["data"]
    return customer


def get_customer_id(name: str) -> int:
    """Gets a customer's ID from their name

    :param name: The name of the customer
    """
    return customer_from_shortname(name)["id"]
