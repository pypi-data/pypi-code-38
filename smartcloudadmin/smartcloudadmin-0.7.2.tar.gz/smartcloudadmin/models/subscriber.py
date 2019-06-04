import smartcloudadmin.http_requests as bss_api

from smartcloudadmin.models.seat import Seat
import smartcloudadmin.enums as bss_enums
from smartcloudadmin.utils.json_constructor import register_subscriber_json, set_one_time_password_json,\
    set_user_password_json, change_password_json
from smartcloudadmin.utils.qol import parse_time
from datetime import datetime
import logging
from smartcloudadmin.config import BssConfig

logging.basicConfig(level=BssConfig.log_level)
logger = logging.getLogger(__name__)


class Subscriber:
    """
     Represents an Subscriber used within IBM Social Cloud.
     Contains details about the physical location of the Organization headquarters.

     Attributes
     ----------
     environment : str
         Environment/Datacenter the Organization resides on.
     email : str
        Subscriber's email address.
     given_name : str
         First name of subscriber.
     family_name : str
         Surname of subscriber.
     id : int
         Subscriber id
     org_name : str
         Name of Organization to which subscriber belongs to.
     owner : int
         Owner id of Organization.
     created : Datetime
         Time of subscriber creation.
     modified : enumerate
         Time of subscriber was last modified.
     is_guest : bool
         Whether the subscriber is a guest of the Organization or not.
     state : str
         Current user activity state.
     party_role_type : str
         State where Organization resides.
     deleted : bool
         Is the subscriber deleted.
     customer_id : str
         Organization id
     role_set : str
        List of permissions the user has. E.G. User, Application Developer, Administrator.
     name_prefix : str
         Honorary Subscriber prefix. I.E. Dr.
     name_suffix : str
         Name Suffic, I.E. Jr.
     security_realm : enumerate
         Subscriber's federation type.
     employee_number : str
         Organization's number for subscriber
     seat_set : [Seat]
         List of Seat objects which subscriber occupies.
     entitlements : [int]
         List of subscription id's to which subscriber has a seat.
    """

    def __init__(self, environment: str, *, customer_id: int = 0, org_name: str = "", owner: str = 0,
                 modified: datetime = "01/01/1970 00:00:00", is_guest: bool = False,
                 created: datetime = "01/01/1970 00:00:00", subscriber_state: str = bss_enums.State.UNSET.value,
                 party_role_type=None, deleted: datetime = "01/01/1970 00:00:00", role_set=None, id: int = 0,
                 email: str = "", given_name: str = "", family_name: str = "", name_prefix: str = "",
                 name_suffix: str = "", security_realm: bss_enums.State = "", employee_number: str = ""):

        self.environment: str = environment
        self.email: str = email
        self.given_name: str = given_name
        self.family_name: str = family_name
        self.id: int = id
        self.org_name: str = org_name
        self.owner: int = owner
        self.modified: datetime = parse_time(modified)
        self.is_guest: bool = is_guest
        self.created: datetime = parse_time(created)
        self.state: str = bss_enums.State(subscriber_state).value
        self.party_role_type = party_role_type
        self.deleted: bool = deleted
        self.customer_id: int = customer_id
        self.role_set = role_set

        self.name_prefix: str = name_prefix
        self.name_suffix: str = name_suffix
        self.security_realm: str = security_realm
        self.employee_number: str = employee_number

        self.seat_set: {Seat} = {}
        self.entitlements: [int] = []

    @property
    def name(self) -> str:
        """
        :return: Subscriber's full formal name.
        """
        return f"{self.name_prefix} {self.given_name} {self.family_name} {self.name_suffix}"

    # @property
    # def basic(self) -> str:
    #     return "test"
    #
    # @property
    # def summary(self) -> str:
    #     return "subs, seats, etc"

    def __repr__(self) -> str:
        return f"{self.name} {self.email} ({self.id})  {self.state} {self.security_realm} {self.modified} {self.role_set}"

    @classmethod
    def from_json(cls, environment, json_body) -> 'Subscriber':
        subscriber = cls(environment)
        subscriber._get_details_by_id(json_body=json_body)
        return subscriber

    @classmethod
    def get(cls, environment, *, subscriber_id=None, email_address=None) -> 'Subscriber':
        if subscriber_id:  # if both are set use sub id.
            resp = bss_api.get_subscriber_by_id(environment, subscriber_id)
            return Subscriber.from_json(environment, resp)
        elif email_address:
            resp = bss_api.get_subscriber_by_email(environment, email_address)
            return Subscriber.from_json(environment, resp)
        else:
            raise ValueError("Either subscriber id or email address needs to be given as a parameter")

    @classmethod
    def create(cls, environment, organization_id, org_name, *, email_address, given_name, family_name, **kwargs)\
            -> 'Subscriber':
        """
        Creates a subscriber object.

        See also Organzation.add_subscriber()
        Required
        --------
        :param environment: Datacenter to create the Organization on.
        :param organization_id: ID of subscribers organiation
        :param org_name: Name of subscribers organisation.
        :param email_address: Subscriber's Email address
        Optional
        --------
        :param given_name: Subscriber's first name, default : ""
        :param family_name: Subscriber's surname,default : ""
        :param role_set: Role Subscriber should be granted on creation, defaults to User.
        :param name_prefix: default : ""
        :param name_suffix: default : ""
        :param employee_number: default : ""
        :param language_preference: Defaults to English
        :param work_phone: default : ""
        :param mobile_phone: default : ""
        :param home_phone: default : ""
        :param fax: default : ""
        :param job_title: default : ""
        :param website_address: default : ""
        :param time_zone: Defaults to GMT
        :param photo: default : ""


        :return: Subscriber
        """
        body = register_subscriber_json(customer_id=organization_id, org_name=org_name,email_address=email_address,
                                        given_name=given_name, family_name=family_name,**kwargs)
        resp = bss_api.create_subscriber(environment, body)

        subscriber = cls(environment)
        subscriber.id = resp
        subscriber._get_details_by_id()
        return subscriber

    def get_roles(self) -> [str]:
        """
            The Roles currently held by subscriber.
            :return: he current roles groups a subscriber is a member of.
        """
        roles = []
        for role_set in self.role_set:
            roles.append(role_set)
        return roles

    def __eq__(self, other) -> bool:  # mostly for verifying different initialisation classmethods return the same obj
        return self.__dict__ == other.__dict__

    def activate(self) -> None:
        """
            Activates the user on smartcloud.
            :return: None
        """
        bss_api.activate_subscriber(self.environment, self.id)
        self._get_details_by_id()

    def set_one_time_password(self, password) -> None:
        """
            Sets a one time password for the subscriber which they will then be prompted to change on login.
            :param password:
        """
        body = set_one_time_password_json(email=self.email, temp_password=password)
        bss_api.set_one_time_password(self.environment, body)

    def change_password(self, current_password, password) -> None:
        """
            Changes the subscriber's password. Need to know current password in order to change.
            Could be used in conjunction with set_one_time_password to initially set and then change a password.
            :param current_password: Subscriber's current password
            :param password: New password for the subscriber.
        """
        body = change_password_json(email=self.email, old_password=current_password, new_password=password)
        bss_api.change_password(self.environment, body)

    def reset_password(self) -> None:
        bss_api.reset_password(self.environment, self.email)
        """
            Resets the subscribers password and sends them an email in order to set a new one.
            :param environment: Datacenter the subscriber belongs to.
            :param email: Subscriber's email address
        """

    def set_password(self, password) -> None:
        """
            Sets subscribers password.
            :param password: Password to set.
        """
        body = set_user_password_json(email=self.email, new_password=password)
        bss_api.set_password(self.environment, body)

    def delete(self, *, soft_delete=True) -> None:
        """
            Delete subscriber.
            :param soft_delete: Should the subscriber be soft deleted or hard deleted. By default the user is soft deleted.
            :type bool:
        """
        if soft_delete:
            soft_delete_string="true"
        else:
            soft_delete_string="false"
        bss_api.delete_subscriber(self.environment, self.id, soft_delete=soft_delete_string)
        if soft_delete == "false":
            self._cleanup()
        else:  # soft delete
            self._get_details_by_id()

    def restore(self) -> None:
        """
            Restore a user from a soft deleted state.
        """
        bss_api.restore_subscriber(self.environment, self.id)
        self._get_details_by_id()

    def show_as_row(self) -> str:
        """

            :return: Basic details relevent about a user.
        """
        return f"{self.given_name} {self.family_name} {self.email}  {self.state} {self.customer_id}"

    def show_as_summary(self) -> str:
        return f"First Name: {self.given_name}\n" \
               f"Surname: {self.id}\n" \
               f"Email Address: {self.state}\n" \
               f"User Seats: {self.seats}\n" \
               f"Customer Id: {self.available_Seats}\n"

    def suspend(self) -> None:
        """
            Suspends a subscriber.
        """
        bss_api.suspend_subscriber(self.environment, self.id)
        self._get_details_by_id()

    def unsuspend(self) -> None:
        """
            Unsuspends a subscriber.
        """
        bss_api.unsuspend_subscriber(self.environment, self.id)
        self._get_details_by_id()

    def entitle(self, subscription_id) -> None:
        """
            Entitles a subscriber with a subscription from the organization.
            :param subscription_id: subscription id to entitle user with.
        """
        resp = bss_api.entitle_subscriber(self.environment, self.id, subscription_id=subscription_id)
        # self.entitlements[resp.get("Key", {})[0]] = resp.get("Value", {})[0]  # todo: Look into this
        self._get_details_by_id()

    def revoke(self, subscription_id) -> None:
        """
            Revokes a subcribers enttilement to a subscription.
            :param subscription_id:w
        """
        # seat_id = self.entitlements[subscription_id]
        seat = self.seat_set[subscription_id]
        bss_api.revoke_subscriber(self.environment, self.id, seat.id)
        # del self.entitlements[subscription_id]
        self._get_details_by_id()

    # Used for automation and testing - not for production use, unless you want randomly generated users.
    # In that case work away.
    @classmethod
    def _generate_random_user(cls) -> 'Subscriber':
        pass

    def _get_details_by_id(self, json_body=None) -> None:  # todo: handle paging
        if json_body:
            json_body = json_body
        else:
            json_body = bss_api.get_subscriber_by_id(self.environment, self.id)

        person_json = json_body.get("Person")
        self.email: str = person_json.get("EmailAddress")
        self.given_name: str = person_json.get("GivenName")
        self.family_name: str = person_json.get("FamilyName")
        self.id: int = json_body.get("Id")
        self.org_name: str = person_json.get("OrgName")
        self.owner: int = person_json.get("Owner")
        self.modified: datetime = parse_time(person_json.get("Modified"))
        self.is_guest: bool = json_body.get("IsGuest")
        self.created: datetime = parse_time(person_json.get("Created"))
        self.state: str = bss_enums.State(json_body.get("SubscriberState")).value
        self.party_role_type: str = bss_enums.PartyRollType(json_body.get("PartyRoleType")).value
        self.deleted: bool = person_json.get("Deleted")
        self.customer_id: int = json_body.get("CustomerId")

        for seat in json_body.get("SeatSet"):
            self.seat_set[seat.get("SubscriptionId")] = Seat.from_json(seat)
            self.entitlements.append(seat.get("SubscriptionId"))
        self.role_set = person_json.get("RoleSet")

        self.name_prefix: str = person_json.get("NamePrefix")
        self.name_suffix: str = person_json.get("NameSuffix")
        self.security_realm: str = bss_enums.SecurityRealm(person_json.get("SecurityRealm")).value
        self.employee_number: str = person_json.get("EmployeeNumber")
        self.invited_by: str = json_body.get("InvitedBy")
        self.is_sync_pending: str = json_body.get("IsSyncPending")
        self.is_restricted_use: str = person_json.get("IsRestrictedUse")
        self.language_preference: str = person_json.get("LanguagePreference")
        self.security_realm: str = person_json.get("SecurityRealm")

    def _dump_details(self) -> None:
        print(f"""
        Environment : {self.environment}
        Email : {self.email}
        Given Name : {self.given_name}
        Family Name : {self.family_name}
        Id : {self.id}
        Org Name : {self.org_name}
        Owner : {self.owner}
        Modified : {self.modified}
        Is Guest : {self.is_guest}
        Created : {self.created}
        State : {self.state}
        Party Role Type : {self.party_role_type}
        Deleted : {self.deleted}
        Customer Id : {self.customer_id}
        Role Set : {self.role_set}
        Subscriber Attribute Set : {self.subscriber_attribute_set}
        Person : {self.person}                           
        """.ljust(15))

    def _cleanup(self) -> None:
        self.environment: str = None
        self.customer_id: int = 0
        self.org_name: str = ""
        self.owner: str = 0
        self.state: str = bss_enums.State.UNSET.value
        self.modified: datetime = "01/01/1970 00:00:00"
        self.is_guest: bool = False
        self.created: datetime = "01/01/1970 00:00:00"
        self.subscriber_state: str = bss_enums.State.UNSET.value
        self.party_role_type = None
        self.deleted: datetime = "01/01/1970 00:00:00"
        self.role_set = None
        self.id: int = 0
        self.email: str = ""
        self.given_name: str = ""
        self.family_name: str = ""
        self.name_prefix: str = ""
        self.name_suffix: str = ""
        self.security_realm: str = ""
        self.employee_number: str = ""

    def get_role_list(self):
        return bss_api.get_role_list(self.environment, self.email)

    def assign_role(self, valid_role) -> None:  # todo: use enums
        """
            Assigns a role to a subscriber.
            :param valid_role:
        """
        bss_api.assign_role(self.environment, self.email, valid_role)

    def unassign_role(self, valid_role) -> None: # todo: use enums
        """
            Removes a role from a subscriber.
            :param valid_role:
        """
        bss_api.unassign_role(self.environment, self.email, valid_role)
