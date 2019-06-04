import smartcloudadmin.http_requests as bss_api
import textwrap
import operator
import logging
from typing import List, Dict

from smartcloudadmin.utils.json_constructor import register_customer_json
from smartcloudadmin.models.subscription import Subscription
from smartcloudadmin.models.subscriber import Subscriber
from smartcloudadmin.models.address_set import AddressSet
from smartcloudadmin.models.contact import Contact

import smartcloudadmin.enums as bss_enums
from smartcloudadmin.utils.qol import parse_time
from datetime import datetime

from smartcloudadmin.config import BssConfig

logging.basicConfig(level=BssConfig.log_level)
logger = logging.getLogger(__name__)


class Organization:
    """
        Represents an Organization within IBM Social CLoud.

        Supported Operations:

        +-----------+------------------------------------------------------------------+
        | Operation |              Description                                         |
        +===========+==================================================================+
        | x == y    | Test whether 2 Organization objects contain the same data        |
        +-----------+------------------------------------------------------------------+
        | x != y    | Test whether 2 Organization objects do not contain the same data |
        +-----------+------------------------------------------------------------------+
        | str(x)    | Returns basic details about the Organization                     |
        +-----------+------------------------------------------------------------------+
        Attributes
        ----------
        id : int
            The id of the Organization. May be referred to as Customer Id/
        name : str
            Name of the Organization
        environment : str
            location where the organization is hosted. **I.E.**
            North America, Central Europe or Asia Pacific
        contact : :class:`.Contact`
            Object containing details about Organization owner.
        address_set : :class:`.AddressSet`
            Object containing physical address of the Organization.
        language_preference : :class:`.LanguagePreference`
            Language preference when interacting with BSS through UI.
        state : :class:`.State`
            Current state of the Organization. **I.E.** Active
        time_zone : :class:`.TimeZone`
            Timezone the Organization is located in.
        payment_method_type : :class:`.PaymentMethodType`
           Payment method used by Organization
        currency_type : :class:`.CurrencyType`
            Currency the Organization pays in.
        created : Datetime
            Creation time for the organization given in the format of %Y/%m/%d %H:%M:%S
        modified : Datetime
            Modification time for the organization given in the format of %Y/%m/%d %H:%M:%S
        party_type : :class:`.PartyType`
            Party Type
        security_realm : :class:`.SecurityRealm`
            Security configuration of the Organization. I.E. Federated/Non-federated.
        subscriptions : {Subscription}
            A dictionary of Subscriber objects where the key is the Subscriber Id
        subscribers : {Subscriber}
            A dictionary of Subscription objects where the key is the Subscription Id
        admins: {Subscriber}
            A dictionary of Subscription objects where the key is the Subscription Id
        size : str
            A range of the number of users in an Organization. i.E 100<500
        industry : str
            The business or industry the Organization is in.
        vendor_id : int
            Vendor id of the Organization. I.E. 10.
        is_guest : bool
            Current state of the Organization. **I.E.** Active
        customer_type : :class:`.CustomerType`
            Current state of the Organization. **I.E.** Active
        is_partner : bool
            Whether or not the Organization is an IBM partner.
        is_sync_pending : bool
            Current state of the Organization. **I.E.** Active
        last_sync_date : bool
            Current state of the Organization. **I.E.** Active

       """
    def __init__(self, environment: str, id: int =0, name: str = "", address_set: AddressSet = "",
                 contact: Contact = "", language_preference: str = bss_enums.LanguagePreference.EN_US.value,
                 state: str = bss_enums.State.UNSET.value, time_zone: str = "America/Central",
                 payment_method_type: str = bss_enums.PaymentMethodType.PURCHASE_ORDER.value,
                 currency_type: str = bss_enums.CurrencyType.USD.value, owner: int = 0,
                 created: datetime = "01/01/1970 00:00:00", modified: datetime = "01/01/1970 00:00:00",
                 party_type: str = bss_enums.PartyType.ORGANISATION,
                 security_realm: str = bss_enums.SecurityRealm.NON_FEDERATED.value, industry=""
                 ) -> None:  # todo: split this. it's not intuitive.
        """
            Initialises an Organisation object by either retrieving an existing organisation or creating a new
            organisation depending on the parameters provided.

            :param environment: Environment in which the organisation resides. I.E. A3 for America, G3 for Europe, S3 for Asia.
            :param id: The organisation id of the organisation tof an existing organisation.
            :param name: name of organisation that will be created.
            :param given_name: First name of the owner for the organisation that will be created.
            :param family_name: Surname of the owner for the organisation that will be created.
            :param admin_email: Email address of the owner for the organisation that will be created.

            :ivar {Subscriber} : Dict of Subscribers with the Role User
            :ivar {Subscriber} admins : Dict of BSS Subscribers with the Role CustomerAdministrator

        """
        self.environment: str = environment
        self.id: int = id
        self.name: str = name
        self.address_set: AddressSet = address_set  # checl for empty. ssm has an empty one - 502491185
        self.contact: Contact = contact
        self.language_preference: str = bss_enums.LanguagePreference(language_preference).value
        self.state: str = bss_enums.State(state).value
        self.time_zone: str = time_zone  # todo: make time_zone and enum
        self.payment_method_type: str = bss_enums.PaymentMethodType(payment_method_type).value
        self.currency_type: str = bss_enums.CurrencyType(currency_type).value
        self.owner: int = owner
        self.created: datetime = created
        self.modified: datetime = modified
        self.party_type: str = bss_enums.PartyType(party_type).value
        self.security_realm: str = bss_enums.SecurityRealm(security_realm).value

        self.subscribers: Dict[str, Subscriber] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.admins: Dict[str, Subscriber] = {}

        self.size: int = 0
        self.industry: str = industry

        self.vendor_id: int = 10
        self.is_guest: bool = False
        self.customer_type: str = bss_enums.CustomerType.DIRECT.value
        self.is_partner: bool = False

        self.is_sync_pending: bool = False
        self.last_sync_date: datetime = "01/01/1970 00:00:00"

    @property
    def subscription_count(self) -> int:
        """
        The number of subscriptions the Organization has.

        :return: The number of Subscriptions
        :rtype: int
        """
        return len(self.subscriptions)

    # @property
    # def is_ssm(self) -> bool:
    #     """
    #     Checks if the Organization's Vendor Id is that of the IBM Marketplace.
    #     Some Write API calls may not be supported and instead the IBM API Connect API for IBM Marketplace should be
    #     used instead.
    #
    #     :return: if the Organiztion was created through the IBM Marketplace
    #     :rtype: bool
    #     """
    #     return self.vendor_id == [redacted]

    # @property
    # def is_bss(self) -> bool:
    #     """
    #     checks if the Organization's Vendor Id is that of IBM Social Cloud.
    #
    #     :return: if the Organiztion was created through IBM Social Cloud
    #     :rtype: bool
    #     """
    #     return self.vendor_id == [redacted]

    # @property
    # def is_resold(self) -> bool:  # if the org has been sold through a reseller todo: name
    #     """
    #     Checks if the Organization's Vendor Id matches IBM Marketplace and IBM Cloud - should determine if the Organization
    #     was created by a reseller.
    #
    #     :return: if the Organiztion was created through a third party.
    #     :rtype: bool
    #     """
    #     return self.vendor_id != [redacted] and self.vendor_id != [redacted]

    @property
    def country(self) -> str:
        """
        Country of which the Organization resides as per address_set.

        :return: Country the Organization is located in
        :rtype: str
        """
        return self.address_set.country

    @property
    def subscriber_count(self) -> int:
        return len(self.subscribers)

    @classmethod
    def create(cls, environment: str, organisation_name: str, given_name: str, family_name: str, admin_email: str,**kwargs)\
            -> 'Organization':
        """
            Creates a new organisation on BSS and returns organisation object.

            :param environment: Environment of the organisation , e.g. A3,G3,S3
            :param organisation_name: Name of the organisation.
            :param given_name: First name of the organisation owner.
            :param family_name: Surname of the organisation owner.
            :param admin_email: Email address for the organisation admin
            :returns: an organisation object
            :raises: PermissionError: User is not authorised to execute this request.
            :rtype: Organization
            :example:
            >>> resp = bss_api.create_org(environment, body)

        """
        body = register_customer_json(organisation_name, given_name, family_name, admin_email, **kwargs)
        resp = bss_api.create_org(environment, body)
        created_org = cls(environment)
        created_org.id = resp
        created_org.environment = environment
        created_org._get_details()
        return created_org

    @classmethod
    def get(cls, environment: str, organization_id: int) -> 'Organization':
        """
        Creates a new organisation on BSS and returns that organisation object.

        :param environment: Environment of the organisation , e.g. NA, CE, AP
        :param organization_id: Name of the organisation.
        :returns: Retrieved Organization
        :rtype: Organization
        :raises: PermissionError: User is not authorised to execute this request.

        :example:
         >>>resp = bss_api.create_org(environment, body)
        """
        retrieved_org = cls(environment)
        retrieved_org.id = organization_id
        retrieved_org.environment = environment
        retrieved_org._get_details()
        return retrieved_org

    @classmethod
    def get_basic(cls, environment: str, organization_id: int) -> 'Organization':
        """
        Gets an Organization object with basic Organization details. Does not retrieve subscription or subscriber
        information.
        :param environment: Datacenter where the Organization resides
        :param organization_id: Organization id
        :return: a Basic Organization
        :rtype: Organization
        """
        retrieved_org = cls(environment)
        retrieved_org.id = organization_id
        retrieved_org.environment = environment
        retrieved_org._get_details(component="organization")
        return retrieved_org

    def __repr__(self) -> str:
        """
        A Very high level summary of the Organization.
        :return: Org name, id, state, security modified and number of subsriptions
        :rtype: str
        """
        return f"{self.name} ({self.id}) {self.state}  {self.security_realm} {self.modified}. " \
               f"Subscriptions {self.subscription_count}"

    # def __eq__(self, other) -> bool:
    #     """
    #         Verifies that the objects contain the same data, not that the object is identical.
    #     :param other:
    #     :return: if objects contain the same data
    #     :rtype: bool
    #     """
    #     for x, y in self.__dict__.items():
    #         other_y = getattr(other, x)
    #         if y == other_y :
    #             pass
    #         else:
    #             print(f"{x} is not equal ({y},{other_y})")
    #     return self.__dict__ == other.__dict__

    # def update(self):  # not working
    #     """
    #        update ( DO NOT USE )
    #        Updates the organisation details server with current object attributes.
    #
    #        Example:
    #        my_org = Organisation("SP1")
    #        my_org.get_details(126126)
    #        my_org.name = "My New Org Name"
    #        my_org.update()
    #    """
    #
    #     body = register_customer_json(self.name, self.contact_given_name, self.contact_family_name,
    #                                   self.contact_email_address, self.phone, self.address_set.address_line_1,
    #                                   self.address_set.address_line_2,
    #                                   self.address_set.city, self.address_set.state, self.address_set.country,
    #                                   self.address_set.postal_code,  self.job_title, self.time_zone)
    #     print(self.contact_family_name)
    #     print(self.contact_given_name)
    #     print(self.contact_email_address)
    #     success, resp = update_org(self.environment, body)
    #     if success:
    #         self.id = resp
    #         print(f"org {resp}")
    #     else:
    #         print(resp.get("ResponseMessage"))
    #         print(resp.get("Useraction"))

    def _get_details(self, *, component: str ="all", json_body: {} =None) -> None:
        """
        Retrieves an organisation on BSS and returns that organisation object.

        :param component: Specify which part of the object to update optiona: all,organization,subscriptions,subscribers
        :param json_body: (Optional) When provided a JSON payload will be used to update Organization object instead of
        making a request.
        :returns: an organisation object
        :raises PermissionError: User is not authorised to execute this request.
        """
        if json_body:
            resp = json_body
        else:
            resp = bss_api.get_org_by_id(self.environment, self.id)
            resp = resp.get("Customer")
        customer = resp
        organization = resp.get("Organization")
        contact = resp.get("Organization").get("Contact")
        address_set = resp.get("Organization").get("AddressSet")
        customer_account_set = customer.get("CustomerAccountSet", [{}])[0]
        if component == "all" or component == "organization":
            self.id = customer.get("Id")  # when retrieving from json
            self.owner = organization.get("Owner")
            self.name = organization.get("OrgName")
            self.created = parse_time(organization.get("Created"))
            self.modified = parse_time(organization.get("Modified"))
            self.industry = organization.get("Industry")
            self.state = bss_enums.State(customer.get("CustomerState")).value
            self.party_type = bss_enums.PartyType(organization.get("PartyType")).value
            self.size = organization.get("CompanySize")  # todo : make use
            self.security_realm = bss_enums.SecurityRealm(organization.get("SecurityRealm")).value
            self.last_sync_date = parse_time(customer.get("LastSyncDate", "01/01/1970 00:00:00"))
            self.vendor_id: int = customer_account_set.get("VendorId")
            self.is_guest: bool = customer.get("IsGuest")
            self.customer_type: str = organization.get("CustomerType")
            self.is_partner: bool = organization.get("IsPartner")

            # IBM Cloud Specific
            self.is_sync_pending: bool = organization.get("IsSyncPending")
            self.last_sync_date: datetime = "01/01/1970 00:00:00"  # Customer.IsSyncPending  ssm only

        if component == "all" or component == "organization":
            self.contact = Contact(email_address=contact.get("EmailAddress"),
                                   family_name=contact.get("FamilyName", ""),
                                   given_name=contact.get("GivenName", ""),
                                   ldap_dn=contact.get("DN"),
                                   created=parse_time(contact.get("Created")),
                                   employee_number=contact.get("EmployeeNumber", ""),
                                   modified=parse_time(contact.get("Modified")),
                                   name_prefix=contact.get("NamePrefix", ""),
                                   name_suffix=contact.get("NameSuffix", ""),
                                   deleted=contact.get("Deleted"),
                                   security_realm=bss_enums.SecurityRealm(contact.get("SecurityRealm")).value,
                                   time_zone=contact.get("TimeZone"),
                                   job_title=contact.get("JobTitle", ""),
                                   mobile_phone=contact.get("MobilePhone", ""),
                                   work_phone=contact.get("WorkPhone", ""),
                                   home_phone=contact.get("HomePhone", ""),
                                   org_id=customer.get("Id"),
                                   org_name=organization.get("OrgName"),
                                   )
        if component == "all" or component == "organization":
            if not address_set:  # Address set may be empty - e.g. from SBS
                self.address_set = AddressSet.not_provided(modified=self.modified)
            else:
                self.address_set = AddressSet(state_code=address_set[0].get("StateCode"),
                                              postal_code=address_set[0].get("PostalCode"),
                                              city=address_set[0].get("City"),
                                              state=address_set[0].get("State"),
                                              country=address_set[0].get("Country"),
                                              country_code=address_set[0].get("CountryCode"),
                                              address_type=address_set[0].get("AddressType"),
                                              modified=address_set[0].get("Modified"),
                                              address_line_1=address_set[0].get("AddressLine1", ""),
                                              address_line_2=address_set[0].get("AddressLine2", ""))
        if component == "all" or component == "subscriptions":
            self._retrieve_subscriptions()
        if component == "all" or component == "subscribers":
            self._retrieve_subscribers()

    def check_for_updates(self) -> bool:
        """
          Compares current Organization object with live server data and updates if there are differences.

          :returns: **if** an update was made
          :rtype: bool

          :example:
          >>> my_organization.check_for_updates()

        """
        resp = bss_api.get_org_by_id(self.environment, self.id)
        was_updated = False
        organization = resp.get("Customer").get("Organization")
        contact = resp.get("Customer").get("Organization").get("Contact")
        address_set = resp.get("Customer").get("Organization").get("AddressSet")[0]

        logger.info(f' check_for_updates : Organization Object ({self.modified}) vs '
                    f'JSON ({parse_time(organization.get("Modified"))}) for org_id {self.id} '
                    f'on env {self.environment}')
        if self.modified != parse_time(organization.get("Modified")):  # if not equal we're getting the most recent
            self._get_details(component="organization")
            was_updated = True
            logger.info("Organisation was updated")
        logger.info(f' check_for_updates : Contact Object ({self.contact.modified}) vs '
                    f'JSON ({parse_time(contact.get("Modified"))}) for org_id {self.id} '
                    f'on env {self.environment}')
        if self.contact.modified != parse_time(contact.get("Modified")):
            self._get_details(component="contact")
            logger.info("Contact was updated")
            was_updated = True

        if self.address_set.modified != parse_time(address_set.get("Modified")):
            self._get_details(component="address_set")
            logger.info(f"""AddressSet was updated - {self.address_set.modified}  vs {parse_time(address_set.get("Modified"))}""")
            was_updated = True

        resp = bss_api.get_subscription_list_by_customer_id(self.environment, self.id)
        if len(self.subscriptions) == len(resp.get("List")):  # if subscription count doesnt changes - check each
            for subscription in resp.get("List"):
                if self.subscriptions[subscription.get("Id")].modified == parse_time(subscription.get("Modified")):
                    logger.info(f'check_for_updates Subscription object not modified '
                                f'({self.subscriptions[subscription.get("Id")].modified}) '
                                f'matches json response modified ({parse_time(subscription.get("Modified"))})')
                else:
                    logger.info("Subscription was updated")
                    self._get_details(self.id)  # get all details. no reason to just get subscriptions.
                    was_updated = True
                    break
        else:
            logger.info(f' check_for_updates : Subscription Object'
                        f' ({self.subscriptions[resp.get("Id")].modified}) vs '
                        f'JSON ({parse_time(resp.get("Modified"))}) for org_id {self.id} '
                        f'on env {self.environment}')
            self._get_details(self.id)  # get all details. no reason to just get subscriptions.
            was_updated = True
            logger.info("SubscriptionCount was updated")
        return was_updated

    def delete(self) -> None:
        """
        Deletes the Organization.

        :raises: PermissionError: User is not authorised to execute this request.

        :example:
         >>> my_organization.delete()
        """
        bss_api.delete_org(self.environment, self.id)
        self._cleanup()  # look into this - deregister pending could be useful but really it won't

    def suspend(self) -> None:
        """
            Suspends the Organization.

            :raises: PermissionError: User is not authorised to execute this request.

            :example:
                >>> my_organization.suspend()
        """
        bss_api.suspend_org(self.environment, self.id)
        self._get_details(component="organization")

    def unsuspend(self) -> None:
        """
             Unuspends the Organization.

             :raises: PermissionError: User is not authorised to execute this request.

             :example:
                >>> my_organization.unsuspend()
         """
        bss_api.unsuspend_org(self.environment, self.id)
        self._get_details(component="organization")

    def add_subscriber(self, *, email_address, given_name, family_name, **kawrgs) -> 'Subscriber':
        """
             Adds a new user to the Organization.

             For a full list of optional params see :func:`bssapi.models.subscriber.Subscriber.create`

             :param email_address: User's email address
             :param given_name: User's first name
             :param family_name: User's surname

             :raises: PermissionError: User is not authorised to execute this request.

             :return: Newly created Subscriber.
             :rtype: Subscriber

             :example:
             >>> Subscriber.create(given_name="Tim", family_name="Tom" ,email_address="tim.tom@tam.net")

         """
        subscriber = Subscriber.create(self.environment, self.id, self.name, email_address=email_address,
                                       given_name=given_name, family_name=family_name, **kawrgs)
        self.subscribers[subscriber.id] = subscriber
        return subscriber

    def remove_subscriber(self, subscriber: Subscriber) -> None:  # todo: make use of parameters
        """
        Removes the Subscriber

        :param subscriber:
        :return: None

        :example:
        >>> tom = Subscriber.get("A3", 2142424)
        >>> my_organization.remove_subscriber(tom)
        """
        subscriber.delete()
        self.subscribers.remove(subscriber.id)

    def filter_subscriptions(self, *, attribute, attribute_value, passed_operator=operator.eq) -> {Subscription}:
        """
        Returns a filtered subscriber list based instance attributes and queried attribute value.
        For greater than / less than queries it makes sense to think of it as :
        Is subscription.modified date greater ( newer ) than attribute_value?

        :param attribute: Subscription attribute that is being filtered.
        :param attribute_value: Value of attribute you want to filter against.
        :param passed_operator: Operator to be carried out agaisnt attribute and value. E.G. State is
        not equal to ACTIVE.
        :returns: A List of subscriptions that match the given query
        :rtype: {Subscription}
        :raises PermissionError: User is not authorised to execute this request.

        :example:
            >>> my_organisation.filter_subscriptions(attribute="state", attribute_value="ACTIVE",passed_operator=operator.ne)
        """
        filter_dict = {}
        filter_dict.update({(key if passed_operator(getattr(value, attribute), attribute_value) else "bin_this"):
                            value for key, value in self.subscriptions.items()})
        if "bin_this" in filter_dict:  # not really happy with this
            del filter_dict["bin_this"]
        return filter_dict

    def filter_subscribers(self, *, attribute, attribute_value, passed_operator=operator.eq) -> {Subscriber}:
        """
        Returns a filtered subscriber list based instance attributes and queried attribute value.
        For greater than / less than queries it makes sense to think of it as :
        Is subscriber.modified date greater ( newer ) than attribute_value?

        :param attribute: Subscriber attribute that is being filtered.
        :param attribute_value: Value of attribute you want to filter against.
        :param passed_operator: Operator to be carried out agaisnt attribute and value. E.G. State is not equal to ACTIVE.
        :returns: [Subscriber]
        :raises PermissionError: User is not authorised to execute this request.

        :example : my_organisation.filter_subscribers(attribute="state", attribute_value="ACTIVE", passed_operator=operator.ne)
        """
        filter_dict = {}
        filter_dict.update({(key if passed_operator(getattr(value, attribute), attribute_value) else "bin_this"):
                            value for key, value in self.subscribers.items()})
        if "bin_this" in filter_dict:  # not really happy with this
            del filter_dict["bin_this"]

        return filter_dict

    def _retrieve_subscriptions(self) -> None:
        page_number = 1
        page_size = 25
        logger.info(f'_retrieve_subscriptions'
                    f' Starting Subscription lookup for organization {self.name}.'
                    f' org_id {self.id} on env {self.environment}.')
        while True:
            resp = bss_api.get_subscription_list_by_customer_id(self.environment, self.id, page_number=page_number,
                                                                page_size=page_size)
            if not resp.get("List"):  # Empty list means we've hit the last page in our pagination journey.
                logger.info(f'_retrieve_subscriptions'
                            f' Subscription lookup completed. {len(self.subscriptions)} Subscriptions over {page_number} pages'
                            f' ({page_size} results per page) for org_id {self.id} on env {self.environment}.')
                logger.info("")
                break
            for subscriptionJson in resp.get("List"):
                my_sub = Subscription.from_json(self.environment, subscriptionJson)
                self.subscriptions[my_sub.id] = my_sub
            page_number += 1

    # todo: Consider using async requests or at least multiple ones.
    def _retrieve_subscribers(self) -> None:
        # todo: fix this - make this more useable.
        page_number = 1
        page_size = 25
        self.size = 0
        user_count = 0
        admin_count = 0
        total = 0
        logger.info(f'_retrieve_subscribers'
                    f' Starting Subscriber lookup for organization {self.name}.'
                    f' org_id {self.id} on env {self.environment}.')
        while True:
            resp = bss_api.get_subscribers_by_org(self.environment, self.id, page_number=page_number)
            if not resp.get("List"):  # Empty list means we've hit the last page in our pagination journey.
                logger.info(f'_retrieve_subscribers'
                            f' Subscriber lookup completed. {len(self.subscribers)} Subscribers and'
                            f' {len(self.admins)} over {page_number} pages'
                            f' ({page_size} results per page) for org_id {self.id} on env {self.environment}.')
                logger.info("")
                break
            for subscriberJson in resp.get("List"):
                my_sub = Subscriber.from_json(self.environment, subscriberJson)
                if "CustomerAdministrator" in my_sub.role_set:
                    self.admins.update({my_sub.id: my_sub})
                    self.subscribers.update({my_sub.id: my_sub})
                    admin_count += 1
                if "User" in my_sub.role_set:
                    self.subscribers.update({my_sub.id: my_sub})
                    user_count += 1
                total += 1
                self.size += 1  # let's bring that total org count up a bit.
            page_number += 1

    def add_subscription(self, *, part_number, part_quantity, duration_length, duration_units) -> 'Subscription':
        """
            Adds a new subscription to an Organization.

            For a full list of optional params see :func:`bssapi.models.subscriber.Subscription.create`

            :param part_number: Subscription part number. I.E. D0NPULL for Connections Cloud.
            :param part_quantity: Number of seats
            :param duration_length: length of Subscription duration units
            :param duration_units: options YEARS or MONTHS ( possibly DAYS )

            :returns: Created Subscription object
            :rtype: Subscription
            :raises PermissionError: User is not authorised to execute this request.

            :example :
                >>> my_organisation.add_subscription(part_number="D0NPULL", part_quantity=25, duration_length=1,
                duration_units="YEARS")
        """
        my_sub = Subscription.create(self.environment, self.id, part_number=part_number, part_quantity=part_quantity,
                                     duration_length=duration_length, duration_units=duration_units)
        self.subscriptions[my_sub.id] = my_sub
        return my_sub

    def remove_subscription(self, subscription: Subscription) -> None:  # remove by id not number.
        """
            Returns a filtered subscriber list based instance attributes and queried attribute value.
            For greater than / less than queries it makes sense to think of it as :
            Is subscriber.modified date greater ( newer ) than attribute_value?

            :param subscription: Subscription to delete
            :raises PermissionError: User is not authorised to execute this request.

            >>> connections_subscription = Subscription.get("A3",121242)
            >>> my_organization.remove_subscription(connections_subscription)
        """

        del self.subscriptions[subscription.id]
        subscription.delete()

    @classmethod
    def from_json(cls, environment, json_body) -> 'Organization':
        """
        Creates an Organization object from a JSON payload, for example when retrieving many orgs or organization searches
        :param environment: Datacenter
        :param json_body: JSON Payload
        :return: Organization
        :rtype: Organization
        """
        created_org = cls(environment)
        created_org.environment = environment
        created_org._get_details(json_body=json_body)
        return created_org

    def _cleanup(self) -> None:
        self.id: int = 0
        self.name: str = ""
        self.address_set: AddressSet = None
        self.contact: Contact = None
        self.language_preference: str = bss_enums.LanguagePreference.EN_US.value
        self.state: str = bss_enums.State.UNSET.value
        self.time_zone: str = "America/Central"  # todo: make time_zone and enum
        self.payment_method_type: str = bss_enums.PaymentMethodType.PURCHASE_ORDER.value
        self.currency_type: str = bss_enums.CurrencyType.USD.value
        self.owner: int = 0
        self.created: datetime = "01/01/1970 00:00:00"
        self.modified: datetime = "01/01/1970 00:00:00"
        self.party_type: str = bss_enums.PartyType.ORGANISATION.value
        self.security_realm: str = bss_enums.SecurityRealm.NON_FEDERATED.value

        self.subscribers: {Subscriber} = {}
        self.subscriptions: {Subscription} = {}
        self.admins: {Subscriber} = {}

        self.size: int = len(self.subscriptions) + len(self.admins)

    def _dump_details(self) -> None:
        intented_contact_string = textwrap.indent(self.contact._dump_details(),'\t')
        intented_address_set_string = ""
        print(f"""
        Environment : {self.environment}
        Id : {self.id}
        Name : {self.name}
        Address Set : {intented_address_set_string}
        Contact : {intented_contact_string}
        Language Preference : {self.language_preference}
        State : {self.state}
        Time Zone : {self.time_zone}
        Payment Method Type : {self.payment_method_type}
        Currency Type : {self.currency_type}
        Owner : {self.owner}
        Created : {self.created}
        Modified : {self.modified}
        Party Type : {self.party_type}
        Security Realm : {self.security_realm}
        """.ljust(15))
