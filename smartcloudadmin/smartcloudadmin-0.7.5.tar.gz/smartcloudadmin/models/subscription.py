import smartcloudadmin.http_requests as bss_api
from smartcloudadmin.utils.json_constructor import register_subscription_json
from smartcloudadmin.enums import State
from smartcloudadmin.utils.qol import parse_time
from datetime import datetime
import logging
from smartcloudadmin.config import BssConfig


logging.basicConfig(level=BssConfig.log_level)
logger = logging.getLogger(__name__)


class Subscription:
    """
    Represents an `Subscription <https://www-10.lotus.com/ldd/appdevwiki.nsf/xpAPIViewer.xsp?lookupName=API+Reference#action=openDocument&res\_title=Create_subscription_bss&content=apicontent>`_within IBM Social Cloud.
    Supported Operations:

    +-----------+-------------------------------------------------------------+
    | Operation |              Description                                    |
    +===========+=============================================================+
    | x == y    | Test whether 2 Contact objects contain the same data        |
    +-----------+-------------------------------------------------------------+
    | x != y    | Test whether 2 Contact objects do not contain the same data |
    +-----------+-------------------------------------------------------------+
    | str(x)    | Returns basic details about the Contact                     |
    +-----------+-------------------------------------------------------------+
    Attributes
    ----------
    environment : str
        Datacenter where the Subscription resides
    part_number : str
         Subscription part_number, e.g. D0NPULL, D0NRILL
    id : int
        Subscription id
    customer_id : id
        Organization id
    created : :class:`.Datetime`
        Creation date for the Subscription.
    modified : :class:`Datetime`
        Modification date for the Subscription.
    part_quantity : int
        Number of Seats to be created for the Subscription
    available_numbers_of_seats : int
        Unoccupied seats for Subscription
    state : str
        Current state of Subscription
    deleted : bool
        Whether the Subscription user still exists.
    duration_length : int
        Lifespan of Subscription in duration_units
    duration_unit : str
        Units of time duration_length is measured in. MONTHS/YEARS
    entitlement_quantity_available : int
        entitlement quantity
    max_number_of_seats : int
        Max seats on Subscription
    is_automatically_renewed : bool
        Weather the subscription will renew or expire at expiration date.
    purchase_date : :class:`.Datetime`
        Purchase date
    is_trial : bool
        Is Subscription trial
    is_beta : bool
        Is Subscription beta
    is_free : bool
        Is Subscription free
    parent_subscription_id : str
        -1 for standard Subscriptions. Child Subscriptions will have a parent id
    billing_frequency : str
        Frequency
    effective_date : :class:`.Datetime`
        Subscription start date
    expiration_date : :class:`.Datetime`
        Subscription end date
   """
    def __init__(self, environment: str, customer_id: int=0,  part_number="", id=0, part_quantity=0, state=State.UNSET.value,
                 available_seats=0, modified="01/01/1970 00:00:00", created="01/01/1970 00:00:00", duration_length=0,
                 duration_unit=0, entitlement_quantity_available=0, max_number_of_seats=0,
                 is_automatically_renewed=False, purchase_date="01/01/1970 00:00:00", is_trial=False, deleted=False
                 , is_beta=False, is_free=False, parent_subscription_id=0,
                 billing_frequency="", effective_date="01/01/1970 00:00:00", expiration_date="01/01/1970 00:00:00"
                 ):
        self.environment: str = environment
        self.part_number: str = part_number
        self.id: int = id
        self.customer_id: int = customer_id
        self.part_quantity: int = part_quantity

        self.state: State = state
        self.available_numbers_of_seats: int = available_seats
        self.modified: datetime = parse_time(modified)
        self.created: datetime = parse_time(created)
        self.duration_length: int = duration_length
        self.duration_unit: int = duration_unit

        self.entitlement_quantity_available: int = entitlement_quantity_available
        self.max_number_of_seats: int = max_number_of_seats
        self.is_automatically_renewed: bool = is_automatically_renewed
        self.purchase_date: datetime = parse_time(purchase_date)
        self.is_trial: bool = is_trial
        self.deleted: bool = deleted
        self.is_beta: bool = is_beta
        self.is_free: bool = is_free
        self.parent_subscription_id: int = parent_subscription_id
        self.billing_frequency: str = billing_frequency
        self.effective_date: datetime = parse_time(effective_date)
        self.expiration_date: datetime = parse_time(expiration_date)

        # todo: sub-subscription support

    def __lt__(self, other) -> bool:  # most recent first
        """
        Compares the IDs of Organizations and returns true if the Organization
        :param other:
        :return:
        """
        return self.id > other.id

    @property
    def modified_epoch(self) -> float:
        """
        :return: modified date in epoch format
        """
        return self.modified.timestamp()

    @property
    def created_epoch(self) -> float:
        """
        :return: created date in epoch format
        """
        return self.created.timestamp()

    def __eq__(self, other) -> bool:  # mostly for verifying different initialisation classmethods return the same obj
        return self.__dict__ == other.__dict__

    def __repr__(self) -> str:
            return f"{self.part_number} {self.id} {self.state}  {self.available_numbers_of_seats}/{self.max_number_of_seats} {self.modified}"

    def show_as_row(self) -> str:
        return f"{self.part_number} {self.id} {self.state}  {self.available_numbers_of_seats}/{self.max_number_of_seats} {self.modified}"

    def show_as_summary(self) -> str:
        return f"Part Number: {self.part_number}\n" \
               f"Subscription Id: {self.id}\n" \
               f"State: {self.state}\n" \
               f"Seats: {self.max_number_of_seats}\n" \
               f"Available Seats: {self.entitlement_quantity_available}\n" \
               f"Created: {self.created}\n" \
               f"Modified: {self.modified}\n"

    def _get_details(self, *, json_payload: {}=None) -> None:  # todo: handle paging
        if json_payload:
            json_body = json_payload
        else:
            json_body = bss_api.get_subscription_by_subscription_id(self.environment, self.id)

        self.part_number = json_body.get("PartNumber")
        self.id = json_body.get("Id")
        self.part_quantity = json_body.get("EntitlementQuantity")
        self.customer_id = json_body.get("CustomerId")
        self.state = json_body.get("SubscriptionState")
        self.available_numbers_of_seats = json_body.get("NumberOfAvailableSeats")
        self.modified = parse_time(json_body.get("Modified"))
        self.created = parse_time(json_body.get("Created"))
        self.duration_length = json_body.get("DurationLength")
        self.duration_unit = json_body.get("DurationUnits")
        self.entitlement_quantity_available = json_body.get("EntitlementQuantityAvailable")
        self.max_number_of_seats = json_body.get("MaxNumberOfSeats")
        self.is_automatically_renewed = json_body.get("IsAutomaticallyRenewed")
        self.purchase_date = parse_time(json_body.get("PurchaseDate"))
        self.is_trial = json_body.get("IsTrial")
        self.deleted = json_body.get("Deleted")
        self.is_beta = json_body.get("IsBeta")
        self.is_free = json_body.get("IsFree")
        self.parent_subscription_id = json_body.get("ParentSubscriptionId")
        self.billing_frequency = json_body.get("BillingFrequency")
        self.expiration_date = parse_time(json_body.get("ExpirationDate"))
        self.effective_date = parse_time(json_body.get("EffectiveDate"))

    @classmethod
    def get(cls, environment, subscription_id) -> 'Subscription':
        """ Populates subscription with an existing subcription details using BSS API
             :param environment: Datacenter Subscription resides on
             :type: str
             :param subscription_id: subscription id to retrieve
             :type: int
             :returns: Subscription
             :rtype: Subscription
         """
        resp = bss_api.get_subscription_by_subscription_id(environment, subscription_id)
        return Subscription.from_json(environment, resp)

    @classmethod
    def create(cls, environment, customer_id, part_number, part_quantity,duration_units, duration_length, **kwargs) -> 'Subscription':
        """
        Creates a new subscription

        :param environment: Datacenter
        :param customer_id: Organization_id
        :param part_number: Part Number for Subscription
        :param part_quantity: Number of Seats for Subscription
        :param duration_units: Months/Years
        :param duration_length: Duration length in Units
        :param kwargs:
        :return: Newly created Subscription
        :rtype: Subscription
        """
        body = register_subscription_json(part_number=part_number, part_quantity=part_quantity,
                                          customer_id=customer_id, duration_units=duration_units,
                                          duration_length=duration_length)
        resp = bss_api.create_subscription(environment, body)
        new_subscription = cls(environment, customer_id=customer_id)
        new_subscription.id = resp.get("SubscriptionId")
        new_subscription._get_details()
        return new_subscription

    def suspend(self) -> None:
        bss_api.suspend_subscription(self.environment, self.id)
        self.state = State.SUSPENDED.value  # todo: this should really poll to make sure. Verification step.

    def unsuspend(self) -> None:
        bss_api.unsuspend_subscription(self.environment, self.id)
        self.state = State.ACTIVE.value  # todo: again add polling.

    def delete(self) -> None:
        bss_api.delete_subscription(self.environment, self.id)
        self._cleanup()

    @classmethod
    def from_json(cls, environment, json_body) -> 'Subscription':
        new_subscription = cls(environment)
        new_subscription._get_details(json_payload=json_body)
        return new_subscription
        # cls._get_details(json_payload=json_body)
        # return cls(environment=environment, part_number=json_body.get("PartNumber"), id=json_body.get("Id"),
        #            part_quantity=json_body.get("EntitlementQuantity"),
        #            customer_id=json_body.get("CustomerId"),
        #            state=json_body.get("SubscriptionState"), available_seats=json_body.get("NumberOfAvailableSeats"),
        #            modified=json_body.get("Modified"), created=json_body.get("Created"),
        #            duration_length=json_body.get("DurationLength"), duration_unit=json_body.get("DurationUnits"),
        #            entitlement_quantity_available=json_body.get("EntitlementQuantityAvailable"),
        #            max_number_of_seats=json_body.get("MaxNumberOfSeats"),
        #            is_automatically_renewed=json_body.get("IsAutomaticallyRenewed"),
        #            purchase_date=json_body.get("PurchaseDate", "01/01/1970 00:00:00"),
        #            is_trial=json_body.get("IsTrial"),
        #            deleted=json_body.get("Deleted"),
        #            is_beta=json_body.get("IsBeta"),
        #            is_free=json_body.get("IsFree"),
        #            parent_subscription_id=json_body.get("ParentSubscriptionId"),
        #            billing_frequency=json_body.get("BillingFrequency"),
        #            expiration_date=json_body.get("ExpirationDate"),
        #            effective_date=json_body.get("EffectiveDate")
        #            )

    def _cleanup(self, *, environment="", customer_id=0, part_number="", id=0, part_quantity=0, state=State.UNSET.value,
                 available_seats=0, modified="01/01/1970 00:00:00", created="01/01/1970 00:00:00", duration_length=0,
                 duration_unit=0, entitlement_quantity_available=0, max_number_of_seats=0,
                 is_automatically_renewed=False, purchase_date="01/01/1970 00:00:00", is_trial=False, deleted=False
                 , is_beta=False, is_free=False, parent_subscription_id=0,
                 billing_frequency="", effective_date="01/01/1970 00:00:00", expiration_date="01/01/1970 00:00:00"
                 ) -> None:
        self.environment: str = environment
        self.part_number: str = part_number
        self.id: int = id
        self.customer_id: int = customer_id
        self.part_quantity: int = part_quantity

        self.state: State = state
        self.available_numbers_of_seats: int = available_seats
        self.modified: datetime = parse_time(modified)
        self.created: datetime = parse_time(created)
        self.duration_length: int = duration_length
        self.duration_unit: int = duration_unit

        self.entitlement_quantity_available: int = entitlement_quantity_available
        self.max_number_of_seats: int = max_number_of_seats
        self.is_automatically_renewed: bool = is_automatically_renewed
        self.purchase_date: datetime = parse_time(purchase_date)
        self.is_trial: bool = is_trial
        self.deleted: bool = deleted
        self.is_beta: bool = is_beta
        self.is_free: bool = is_free
        self.parent_subscription_id: int = parent_subscription_id
        self.billing_frequency: str = billing_frequency

        self.effective_date: datetime = parse_time(effective_date)
        self.expiration_date: datetime = parse_time(expiration_date)

    # Sends a seat from one sub to another.
    def transfer_seat(self, seat_id, target_subscription) -> None:
        bss_api.transfer_subscription_seat(self.environment, self.id, seat_id,
                                           target_subscription)
        self._get_details()  # todo: potential oddity - should get sub details for both

    def _dump_details(self) -> None:
        print(f"""
        Environment : {self.environment}
        Id : {self.id}
        Part Number : {self.part_number}
        Customer Id : {self.customer_id}
        Part Quantity : {self.part_quantity}
        State : {self.state}
        Available Seats : {self.available_numbers_of_seats}
        Modified : {self.modified}
        Created : {self.created}
        Duration Length : {self.duration_length}
        Duration Unit : {self.duration_unit}
        Entitlement Quantity Available : {self.entitlement_quantity_available}
        Max Number of Seats : {self.max_number_of_seats}
        Is Automatically Renewed : {self.is_automatically_renewed}
        Purchase Date : {self.purchase_date}
        Is Trial : {self.is_trial}
        Deleted : {self.deleted}
        Is Beta : {self.is_beta}
        Is Free : {self.is_free}
        Parent Subscription Id : {self.parent_subscription_id}
        Billing Frequency : {self.billing_frequency}
        Effective Date : {self.effective_date}
        Expiration Date : {self.expiration_date} 
        """.ljust(15))

    # get_seat is missing