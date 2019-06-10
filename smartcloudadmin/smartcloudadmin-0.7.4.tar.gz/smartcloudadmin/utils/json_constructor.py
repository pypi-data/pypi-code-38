import json
from pkg_resources import resource_filename

"""
File contains functions to return JSON templates with 
"""


"""
    Returns the JSON template with param sustituted
"""


def register_customer_json(organization_name, contact_given_name, contact_family_name, contact_email_address,
                           phone="", address_line_1="",
                           address_line_2="", city="", state="",
                           country="", postcode="",
                           job_title="", time_zone="",
                           address_type="", language_preference=""):
    filepath = resource_filename(__name__, '../json/register_customer.json')
    data = open(filepath)
    string_data = data.read().format(
        org_name=organization_name, contact_family_name=contact_family_name,
        contact_given_name=contact_given_name, contact_email_address=contact_email_address,
        phone="123-456-7899", address_line_1=address_line_1, address_line_2=address_line_2, city=city,
        country=country, postal_code=postcode, state=state, job_title="Director", time_zone="America/Central",
        address_type=address_type, name_prefix="Mr", employee_number="6A77777",
        language_preference=language_preference, work_phone="123-456-7899",
        mobile_phone="123-456-7899", home_phone="123-456-7899", fax="123-456-7899",
        website_address="www.ibm.com")
    data.close()
    return json.loads(string_data)


def register_subscriber_json(*, customer_id, email_address, given_name, family_name, **kwargs):
    given_name = given_name
    family_name = family_name
    org_name = kwargs.get('org_name', "")
    role_set = kwargs.get('role_set', "User")
    email_address = email_address
    name_prefix = kwargs.get('name_prefix',  "")
    name_suffix = kwargs.get('name_suffix',  "")
    employee_number = kwargs.get('employee_number',  " ")
    language_preference = kwargs.get('language_preference', "en_US")
    work_phone = kwargs.get('work_phone',  "")
    mobile_phone = kwargs.get('mobile_phone',  "")
    home_phone = kwargs.get('home_phone',  "")
    fax = kwargs.get('fax',  "")
    job_title = kwargs.get('job_title',  "")
    website_address = kwargs.get('website_address',  "")
    time_zone = kwargs.get('time_zone', "CST")
    photo = kwargs.get('time_zone',  "")

    filepath = resource_filename(__name__, '../json/register_subscriber.json')
    data = open(filepath)
    # data = open('smartcloudadmin/json/register_subscriber.json')
    string_data = data.read().format(customer_id=customer_id, family_name=family_name,
                                     given_name=given_name, email_address=email_address,role_set=role_set,
                                     name_prefix=name_prefix,  name_suffix=name_suffix, employee_number=employee_number,
                                     language_preference=language_preference, work_phone=work_phone,
                                     mobile_phone=mobile_phone, home_phone=home_phone, fax=fax,
                                     job_title=job_title, website_address=website_address, time_zone=time_zone,
                                     photo=photo)
    data.close()
    return json.loads(string_data)


def set_one_time_password_json(*, email, temp_password):
    filepath = resource_filename(__name__, '../json/set_one_time_password.json')
    data = open(filepath)
    # data = open('smartcloudadmin/json/set_one_time_password.json')
    string_data = data.read().format(email_address=email, temp_password=temp_password)
    data.close()
    return json.loads(string_data)


def reset_password(*, email, old_password, new_password):
    filepath = resource_filename(__name__, '../json/change_password.json')
    # data = open('smartcloudadmin/json/change_password.json')
    data = open(filepath)
    string_data = data.read().format(email_address=email, old_password=old_password, new_password=new_password)
    data.close()
    return json.loads(string_data)


def change_password_json(*, email, old_password, new_password):
    filepath = resource_filename(__name__, '../json/change_password.json')
    data = open(filepath)
    # data = open('smartcloudadmin/json/change_password.json')
    string_data = data.read().format(email_address=email, old_password=old_password, new_password=new_password)
    data.close()
    return json.loads(string_data)


def set_user_password_json(*, email, new_password):
    filepath = resource_filename(__name__, '../json/set_user_password.json')
    data = open(filepath)
    # data = open('smartcloudadmin/json/set_user_password.json')
    string_data = data.read().format(email_address=email, new_password=new_password)
    data.close()
    return json.loads(string_data)


def register_subscription_json(*, duration_units="YEARS", duration_length=1, part_number, part_quantity, customer_id):
    filepath = resource_filename(__name__, '../json/register_subscription.json')
    data = open(filepath)
    # data = open('smartcloudadmin/json/register_subscription.json')
    string_data = data.read().format(duration_units=duration_units, duration_length=duration_length,
                                     part_number=part_number, part_quantity=part_quantity, customer_id=customer_id)
    data.close()
    return json.loads(string_data)
