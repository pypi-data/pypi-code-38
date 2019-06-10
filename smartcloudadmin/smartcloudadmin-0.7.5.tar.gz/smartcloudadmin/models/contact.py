from datetime import datetime
from smartcloudadmin.enums import SecurityRealm
import logging
from smartcloudadmin.config import BssConfig

logging.basicConfig(level=BssConfig.log_level)
logger = logging.getLogger(__name__)


class Contact:
    """
    Represents an Organization within IBM Social CLoud.

    Supported Operations:

    +-----------+-------------------------------------------------------------+
    | Operation |              Description                                    |
    +===========+=============================================================+
    | str(x)    | Returns basic details about the Contact                     |
    +-----------+-------------------------------------------------------------+
    Attributes
    ----------
    given_name : str
        First name of the contact.
    family_name : str
         Surname of the contact.
    email_address : str
        Login email address of the user.
    ldap_dn : str
        Users fully quantified domain name as it is in IBM SmartCloud's LDAP server.
    created : :class:`.Datetime`
        Creation date for the Contact record.
    modified : :class:`Datetime`
        Modification date for the Contact record.
    employee_number : str
        Organization supplied employee number.
    name_prefix : str
        Honorary title I.E. Mr. Ms. Dr.
    name_suffix : str
        Name Suffix I.E. Jr.
    deleted : bool
        Whether the Contact user still exists.
    security_realm : :class:`.SecurityRealm`
        Security configuration for the Contact.
    time_zone : :class:`.TimeZone`
        Timezone of the Contact.
    job_title : str
        Job title of the Contact.
    mobile_phone : str
        Mobile phone number to reach Contact.
    work_phone : str
        Work phone number to reach Contact.
    home_phone : str
        Home phone number to reach Contact.
   """

    def __init__(self, *, given_name, family_name, email_address,
                 ldap_dn: str = "", employee_number: str = "", created: datetime="01/01/1970 00:00:00",
                 modified: datetime="01/01/1970 00:00:00", name_prefix: str = "", name_suffix: str = "", deleted: bool,
                 org_name: str = "", org_id: int = 0, security_realm: SecurityRealm= SecurityRealm.NON_FEDERATED,
                 time_zone:str = "America/Central", job_title: str = "Employee", mobile_phone: str = "0000000",
                 work_phone: str = "0000000", home_phone: str = "0000000"):
        self.family_name: str = family_name
        self.given_name: str = given_name
        self.email_address: str = email_address
        self.ldap_dn: str = ldap_dn
        self.created: datetime = created
        self.employee_number: str = employee_number
        self.modified: datetime = modified
        self.name_prefix: str = name_prefix
        self.name_suffix: str = name_suffix
        self.deleted: bool = deleted
        self.security_realm: SecurityRealm = security_realm
        self.time_zone: str = time_zone
        self.job_title: str = job_title
        self.mobile_phone: str = mobile_phone
        self.work_phone: str = work_phone
        self.home_phone: str = home_phone

        # These are mainly additional verification
        self.org_name: str = org_name
        self.org_id: int = org_id

    def __repr__(self) -> str:
        return f"""{self.name_prefix} {self.given_name} {self.family_name} {self.name_suffix} ({self.email_address})""".strip(" ")

    @classmethod
    def from_json(cls):
        pass  # todo: implement this

    def _dump_details(self):
        return f"""
        Family Name : {self.family_name}
        Given Name : {self.given_name}
        Email Address : {self.email_address}
        LDAP DN : {self.ldap_dn}
        Created : {self.created}
        Modified : {self.modified}
        Name Prefix : {self.name_prefix}
        Name Suffix : {self.name_suffix}
        Deleted : {self.deleted}
        Security Realm : {self.security_realm}
        Time Zone : {self.time_zone}
        Job Title : {self.job_title}
        Mobile Phone : {self.mobile_phone}
        Work Phone : {self.work_phone}
        Home Phone : {self.home_phone}"""
