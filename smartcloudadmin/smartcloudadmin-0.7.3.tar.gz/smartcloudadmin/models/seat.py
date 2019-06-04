from datetime import datetime
from smartcloudadmin.utils.qol import parse_time
import logging
from smartcloudadmin.config import BssConfig

logging.basicConfig(level=BssConfig.log_level)
logger = logging.getLogger(__name__)


class Seat:
    """
    Represents an Seat within an IBM Social CLoud Subscription.

    Supported Operations:

    +-----------+------------------------------------------------------------------+
    | Operation |              Description                                         |
    +===========+==================================================================+
    | x == y    | Test whether 2 Seat objects contain the same data                |
    +-----------+------------------------------------------------------------------+
    | x != y    | Test whether 2 Seat objects do not contain the same data         |
    +-----------+------------------------------------------------------------------+
    | str(x)    | Returns basic details about the Seat                             |
    +-----------+------------------------------------------------------------------+

    Attributes
    ----------
    owner : int
        Id of the seat owner.
    terms_of_user_id : int
        update_this
    vendor_id : int
        Id of the Organization Vendor.
    seat_state : :class:`.State`
        Users fully quantified domain name as it is in IBM SmartCloud's LDAP server.
    created : :class:`.Datetime`
        Creation date for the Seat record.
    modified : :class:`Datetime`
        Modification date for the Seat record.
    subscription_id : int
        Subscription id of the seat instance
    subscriber_id : int
        Subscriber id of the seat instance
    entitlement_quantity_allocated : int
        update_this
    version : int
        update_this
    provisioning_workflow_id : int
        update_this
    seat_service_product_attribute_set : str
        update_this
    workflow_id_list : str
        update_this
    deleted : bool
        Is the seat deleted
    id : int
        Seat Id
    has_accepted_terms_of_use : int
        update_this

   """

    def __int__(self):
        self.owner: int = 0
        self.modified: datetime = parse_time("01/01/1970 00:00:00")
        self.terms_of_use_id: int = 0
        self.vendor_id: int = 0
        self.created: datetime = parse_time("01/01/1970 00:00:00")
        self.seat_state: str = 'SeatState'  # ASSIGNED
        self.subscription_id: int = 0
        self.entitlement_quantity_allocated: int = 0
        self.version: int = 0
        self.provisioning_workflow_id: int = 0
        self.subscriber_id: int = 0
        self.seat_service_product_attribute_set: [] = []  # [],
        self.workflow_id_list: [] = []  # [],
        self.deleted: bool = False
        self.id: int = 0
        self.terms_of_user_id: int = 0
        self.has_accepted_terms_of_use: bool = True

    @classmethod
    def from_json(cls, json_body) -> 'Seat':
        new_seat = cls()
        new_seat._get_details_by_id(json_body)
        return new_seat

    def _get_details_by_id(self, json_body):
        self.owner = json_body.get('Owner', 0)
        self.modified = parse_time(json_body.get('Modified', parse_time("01/01/1970 00:00:00")))
        self.terms_of_use_id = json_body.get('TermsOfUseId', 0)
        self.vendor_id = json_body.get('VendorId', 0)
        self.created = parse_time(json_body.get('Created', parse_time("01/01/1970 00:00:00")))
        self.seat_state = json_body.get('SeatState', '')  # ASSIGNED
        self.subscription_id = json_body.get('SubscriptionId', 0)
        self.entitlement_quantity_allocated = json_body.get('EntitlementQuantityAllocated', 0)
        self.version = json_body.get('Version', 0)
        self.provisioning_workflow_id = json_body.get('ProvisioningWorkflowId', 0)
        self.subscriber_id = json_body.get('SubscriberId', 0)
        self.seat_service_product_attribute_set = json_body.get('SeatServiceProductAttributeSet', [])  # [],
        self.workflow_id_list = json_body.get('WorkflowIdList', [])  # [],
        self.deleted = json_body.get('Deleted', 'False')
        self.id = json_body.get('Id', 0)
        self.has_accepted_terms_of_use = json_body.get('HasAcceptedTermsOfUse', 0)

    def __repr__(self):
        return f"Seat id:{self.id} is part of subscription {self.subscription_id} created {self.created}"

