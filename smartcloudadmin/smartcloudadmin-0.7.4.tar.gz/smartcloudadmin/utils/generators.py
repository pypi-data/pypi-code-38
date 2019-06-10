import random
import pkg_resources

import os

# todo: lists could be changed to iterators or something that persists, or maybe both

def given_name(script="English"):
    resource_package = __name__  # Could be any module/package name
    resource_path = '/'.join((f'../datapool/{script}', 'given_name.csv'))  # Do not use os.path.join(), see below

    template = pkg_resources.resource_string(resource_package, resource_path).decode("utf-8")
    words = template.splitlines()
    my_pick = random.choice(words)
    return my_pick


def family_name(script="English"):
    resource_package = __name__  # Could be any module/package name
    resource_path = '/'.join((f'../datapool/{script}', 'family_name.csv'))  # Do not use os.path.join(), see below

    template = pkg_resources.resource_string(resource_package, resource_path).decode("utf-8")
    words = template.splitlines()
    my_pick = random.choice(words)

    return my_pick


def email_address(*, given_name, family_name, org_name):
   # print(f"{given_name}_{family_name}.{org_name}@isc4sb.com")
    return f"{given_name}_{family_name}.{org_name}@isc4sb.com"


def name_prefix():
    return "Mr."


def name_suffix():
    return ""


def employee_number():
    return "6A77777"


def phone_number():
    return "123-456-7899"


def address_line_1(script="English"):
    resource_package = __name__  # Could be any module/package name
    resource_path = '/'.join((f'../datapool/{script}', 'address_line_1.csv'))  # Do not use os.path.join(), see below

    template = pkg_resources.resource_string(resource_package, resource_path).decode("utf-8")
    words = template.splitlines()
    my_pick = random.choice(words)
    return f"{random.randint(0,9)} {my_pick} way"


def address_line_2(script="English"):
    resource_package = __name__  # Could be any module/package name
    resource_path = '/'.join((f'../datapool/{script}', 'address_line_2.csv'))  # Do not use os.path.join(), see below

    template = pkg_resources.resource_string(resource_package, resource_path).decode("utf-8")
    words = template.splitlines()
    my_pick = random.choice(words)
    return my_pick


def city(script="English"):
    resource_package = __name__  # Could be any module/package name
    resource_path = '/'.join((f'../datapool/{script}', 'town.csv'))  # Do not use os.path.join(), see below

    template = pkg_resources.resource_string(resource_package, resource_path).decode("utf-8")
    words = template.splitlines()
    my_pick = random.choice(words)
    #print(my_pick)
    return my_pick


def country():  # makes life easier for now
    return "United States"


def postal_code():
    return "01866"


def state():
    return "Massachusetts"


def job_title(script="English"):
    resource_package = __name__  # Could be any module/package name
    resource_path = '/'.join((f'../datapool/{script}', 'job_title.csv'))  # Do not use os.path.join(), see below

    template = pkg_resources.resource_string(resource_package, resource_path).decode("utf-8")
    words = template.splitlines()
    my_pick = random.choice(words)
    return my_pick


def time_zone():
    return "America/Central"


def language_pref():
    return "EN_US"


def address_type():
    return "MAILING"


def website_address():
    return "www.ibm.com"


def photo():
    return ""


def temp_password():
    return "wgAfaw224"
