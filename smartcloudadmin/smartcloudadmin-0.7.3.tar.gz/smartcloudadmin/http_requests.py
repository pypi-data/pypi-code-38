import requests
from smartcloudadmin.config import BssConfig
from smartcloudadmin.exceptions import BssServerError, BssResourceNotFound, BSSBadData

import logging

logging.basicConfig(level=BssConfig.log_level)
logger = logging.getLogger(__name__)

config = BssConfig()

"""
    This page mostly maps one to one with the BSS documentation found here:
    https://www-10.lotus.com/ldd/appdevwiki.nsf/xpAPIViewer.xsp?lookupName=API+Reference#action=openDocument&res_title=Overview_of_IBM_SmartCloud_SaaS_Business_Support_System_bss&content=apicontent
    
"""

bss_base_resource_url = "/api/bss/resource"
bss_base_service_url = "/api/bss/service"
ssm_base_resource_url = "/scx/test/sbs/subscriber/"


def make_req(environment, url, **kwargs):  # todo: network exception handler
    baseurl = config.get_url(environment)
    auth = config.get_credentials(environment)
    params = kwargs.get('params', {})
    json = kwargs.get('json', {})
    headers = kwargs.get('headers', {})
    method = kwargs.get('method', 'get')
    if method == "get":
        response = requests.get(f"{baseurl}{url}", auth=auth, params=params, verify=config.verify_ssl)
        return response
    elif method == "post":
        r = requests.post(f"{baseurl}{url}", auth=auth, json=json, params=params, headers=headers, verify=config.verify_ssl)
        return r
    elif method == "delete":
        r = requests.delete(f"{baseurl}{url}", auth=auth, json=json, params=params, verify=config.verify_ssl)
        return r
    elif method == "put":
        r = requests.put(f"{baseurl}{url}", auth=auth, json=json, params=params, verify=config.verify_ssl)
        return r


def create_org(env, post_body, base_url=bss_base_resource_url):
    bss_response = make_req(env, f"{base_url}/customer", json=post_body, method="post")
    if bss_response.json().get("Long", ""):  # Issue 17 - BSS returns 200 on successful create calls
        bss_response.status_code = 201
    return _http_status_handler(bss_response.status_code, bss_response)


def update_org(env, post_body, base_url=bss_base_resource_url):  # todo:  WIP
    bss_response = make_req(env, f"{base_url}/customer", json=post_body, method="put")
    if bss_response.json().get("Long", ""):
        return bss_response.json().get("Long")
    return _http_status_handler(bss_response.status_code, bss_response)


def delete_org(env, org_id):
    bss_response = make_req(env, f"/api/bss/resource/customer/{org_id}", method="delete")
    return _http_status_handler(bss_response.status_code, bss_response)


def suspend_org(environment, organization_id):
    bss_response = make_req(environment, f"/api/bss/resource/customer/{organization_id}",
                            method="post", headers={"x-operation": "suspendCustomer"})
    return _http_status_handler(bss_response.status_code, bss_response)


def unsuspend_org(environment, organization_id):
    bss_response = make_req(environment, f"/api/bss/resource/customer/{organization_id}",
                            method="post", headers={"x-operation": "unsuspendCustomer"})
    return _http_status_handler(bss_response.status_code, bss_response)


def get_org_by_id(environment, organization_id):
    bss_response = make_req(environment, f"/api/bss/resource/customer/{organization_id}")
    return _http_status_handler(bss_response.status_code, bss_response)


def get_orgs_by_name(environment, org_name, *, page_number=1, page_size=25):
    bss_response = make_req(environment, f"/api/bss/resource/customer?_namedQuery=getCustomerByOrgName&"
                                         f"orgName={org_name}&_pageNumber={page_number}&_pageSize={page_size}")
    if bss_response.status_code == 200:
        return bss_response.json().get("List")
    elif bss_response.status_code == 404:  # todo: special case. Expected for empty list
        return []
    return _http_status_handler(bss_response.status_code, bss_response)


def get_subscriber_by_email(env, email):  # todo: re-evaluate this - maybe we expect many results as we are returned a list.
    bss_response = make_req(env, f"/api/bss/resource/subscriber?"
                                 f"_namedQuery=getSubscriberByEmailAddress&emailAddress={email}")
    if bss_response.status_code == 200:
        return bss_response.json().get("List")[0]
    return _http_status_handler(bss_response.status_code, bss_response)


def get_subscribers_by_org(env, org_id, page_size=100, page_number=1):  # todo: support pagination
    bss_response = make_req(env, f"/api/bss/resource/subscriber?_namedQuery=getSubscriberByCustomer&"
                                 f"customer={org_id}&_pageNumber={page_number}&_pageSize={page_size}")
    return _http_status_handler(bss_response.status_code, bss_response)


def get_subscriber_by_id(environment, subscriber_id):
    bss_response = make_req(environment, f"/api/bss/resource/subscriber/{subscriber_id}")
    if bss_response.status_code == 200:
        return bss_response.json().get("Subscriber")
    return _http_status_handler(bss_response.status_code, bss_response)


def activate_subscriber(env, subscriber_id):
    bss_response = make_req(env, f"/api/bss/resource/subscriber/{subscriber_id}", method="post",
                            headers={"x-operation": "activateSubscriber"})
    return _http_status_handler(bss_response.status_code, bss_response)


def set_one_time_password(env, post_body):
    bss_response = make_req(env, f"/api/bss/service/authentication/setOneTimePassword", method="post", json=post_body)
    if bss_response.status_code == 204:
        return {}
    return _http_status_handler(bss_response.status_code, bss_response)


def change_password(env, post_body):
    bss_response = make_req(env, f"/api/bss/service/authentication/changePassword", method="post",
                            json=post_body)
    if bss_response.status_code == 204:
        return {}
    return _http_status_handler(bss_response.status_code, bss_response)


def reset_password(env, email_address):
    bss_response = make_req(env, f"/api/bss/service/authentication/resetPassword?loginName={email_address} ",
                            method="post")
    if bss_response.status_code == 204:
        return {}
    return _http_status_handler(bss_response.status_code, bss_response)


def set_password(env, post_body, by_pass_policy=False):
    if by_pass_policy == False:
        by_pass_policy = "false"
    else:
        by_pass_policy = "true"
    bss_response = make_req(env, f"/api/bss/service/authentication/setUserPassword?bypassPolicy={by_pass_policy}",
                            method="post", json=post_body)
    if bss_response.status_code == 204:
        return {}
    return _http_status_handler(bss_response.status_code, bss_response)


def create_subscriber(environment, post_body, supress_email="true"):
    bss_response = make_req(environment, f"/api/bss/resource/subscriber?suppressEmail={supress_email}", json=post_body,
                            method="post", params={"suppressEmail": f"{supress_email}"})

    if bss_response.json().get("Long", ""):  # Issue 17 - BSS returs 200 on successful create calls
        bss_response.status_code = 201
    return _http_status_handler(bss_response.status_code, bss_response)


def get_subscribers(env):
    bss_response = make_req(env, f"/api/bss/resource/subscriber/")
    return _http_status_handler(bss_response.status_code, bss_response)


def delete_subscriber(env, subscriber_id, soft_delete="true"):
    bss_response = make_req(env, f"/api/bss/resource/subscriber/{subscriber_id}?moveToSoftDelete={soft_delete}",
                            method="delete")
    return _http_status_handler(bss_response.status_code, bss_response)


def restore_subscriber(env, subscriber_id):
    bss_response = make_req(env, f"/api/bss/resource/subscriber/{subscriber_id}",
                            method="post", headers={"x-operation": "restoreSubscriber"})
    return _http_status_handler(bss_response.status_code, bss_response)


def suspend_subscriber(env, subscriber_id):
    bss_response = make_req(env, f"/api/bss/resource/subscriber/{subscriber_id}",
                            method="post", headers={"x-operation": "suspendSubscriber"})
    return _http_status_handler(bss_response.status_code, bss_response)


def unsuspend_subscriber(env, subscriber_id):
    bss_response = make_req(env, f"/api/bss/resource/subscriber/{subscriber_id}",
                            method="post", headers={"x-operation": "unSuspendSubscriber"})
    return _http_status_handler(bss_response.status_code, bss_response)


def entitle_subscriber(env, subscriber_id, subscription_id):
    bss_response = make_req(env, f"/api/bss/resource/subscriber/{subscriber_id}/subscription/{subscription_id}",
                            method="post", headers={"x-operation": "entitleSubscriber"})
    if bss_response.status_code == 200:
        return bss_response.json().get("HashMap")
    elif bss_response.status_code == 404:
        # Playing fast and loose with response codes. todo: should info be returned explaining user is already entitled?
        # {'ResponseCode': '404', 'MessageCode': 'BZSUS1926E', 'Severity': 'Error',
        #  'ResponseMessage': 'The subscriber already has a seat for the subscription.',
        # 'Useraction': 'Check that the subscriber already has the same subscription.'}
        return ""

    return _http_status_handler(bss_response.status_code, bss_response)


def revoke_subscriber(env, subscriber_id, seat_id):
    bss_response = make_req(env, f"/api/bss/resource/subscriber/{subscriber_id}/seat/{seat_id}?_force=false",
                            method="post", headers={"x-operation": "revokeSubscriber"})
    return _http_status_handler(bss_response.status_code, bss_response)


def create_subscription(env, body, suppress_email="true"):
    bss_response = make_req(env, f"/api/bss/resource/subscription?suppressEmail={suppress_email}",
                            method="post", json=body)
    if bss_response.status_code == 200:
        return bss_response.json().get("List")[0]
    return _http_status_handler(bss_response.status_code, bss_response)


def suspend_subscription(env, subscription_id):
    bss_response = make_req(env, f"/api/bss/resource/subscription/{subscription_id}",
                            method="post", headers={"x-operation": "suspendSubscription"})
    return _http_status_handler(bss_response.status_code, bss_response)


def unsuspend_subscription(env, subscription_id):
    bss_response = make_req(env, f"/api/bss/resource/subscription/{subscription_id}",
                            method="post", headers={"x-operation": "unsuspendSubscription"})
    return _http_status_handler(bss_response.status_code, bss_response)


def delete_subscription(environment, subscription_id):
    bss_response = make_req(environment, f"/api/bss/resource/subscription/{subscription_id}",
                            method="delete")
    return _http_status_handler(bss_response.status_code, bss_response)


def transfer_subscription_seat(environment, current_subscription_id, seat_id, target_subscription_id):
    bss_response = make_req(environment, f"/api/bss/resource/subscription/{current_subscription_id}/seat/{seat_id}?"
                                         f"targetSubscription={target_subscription_id}",
                            method="post", headers={"x-operation": "transferSeat"})
    return _http_status_handler(bss_response.status_code, bss_response)


def change_subscription_quota(env, subscription_id, seat_id):
    bss_response = make_req(env, f"/api/bss/resource/subscription/{subscription_id}/seat/{seat_id}",
                            method="post", headers={"x-operation": "changeQuota"})
    return _http_status_handler(bss_response.status_code, bss_response)


def get_subscription_list_by_customer_id(env, customer_id, page_number=1, page_size=100):
    bss_response = make_req(env, f"/api/bss/resource/subscription?_namedQuery=getSubscriptionByCustomer&"
                                 f"customerId={customer_id}",
                            method="get", params={"_pageNumber": f"{page_number}", "_pageSize": f"{page_size}"})
    return _http_status_handler(bss_response.status_code, bss_response)


def get_subscription_by_subscription_id(env, subscription_id):
    bss_response = make_req(env, f"/api/bss/resource/subscription/{subscription_id}",
                            method="get")
    if bss_response.status_code == 200:  # bit of a custom handler
        return bss_response.json().get("Subscription")  # todo: check all return json and standardise
    return _http_status_handler(bss_response.status_code, bss_response)


def get_seat_details_by_subscription_id(env, subscription_id, seat_id):
    bss_response = make_req(env, f"/api/bss/resource/subscription/{subscription_id}/seat/{seat_id}",
                            method="get")
    return _http_status_handler(bss_response.status_code, bss_response)


def vendor_get_subscription_list(env, subscription_id, seat_id):
    bss_response = make_req(env, f"/api/bss/resource/subscription/{subscription_id}/seat/{seat_id}",
                            method="get")
    return _http_status_handler(bss_response.status_code, bss_response)


def get_role_list(env, login_name):
    bss_response = make_req(env, f"/api/bss/service/authorization/getRoleList?loginName={login_name}",
                            method="post")

    if bss_response.status_code == 200:
        return bss_response.json().get("List")
    return _http_status_handler(bss_response.status_code, bss_response)


def assign_role(env, login_name, valid_role):
    bss_response = make_req(env, f"/api/bss/service/authorization/assignRole?loginName={login_name}&role={valid_role}",
                            method="post")
    return _http_status_handler(bss_response.status_code, bss_response)


def unassign_role(env, login_name, valid_role):
    bss_response = make_req(env, f"/api/bss/service/authorization/unassignRole?"
                                 f"loginName={login_name}&role={valid_role}",
                            method="post")
    return _http_status_handler(bss_response.status_code, bss_response)


def _http_status_handler(given_status_code, bss_response_body):
    """

    :param status_code:
    :param success_message:
    :return:
    """
    # todo: flesh this out and add in better exception
    if given_status_code == 200:
        return bss_response_body.json()
    elif given_status_code == 201:
        return bss_response_body.json().get("Long", "")
    elif given_status_code == 204:
        return None
    elif given_status_code == 400:
        _throw_http_400(bss_response_body.json().get('BSSResponse'))
    elif given_status_code == 404:
        _throw_http_404(bss_response_body.json().get('BSSResponse'))
    elif given_status_code == 500:
        _throw_http_500(bss_response_body.json().get('BSSResponse'))
    elif given_status_code == 502:
        _throw_http_500(bss_response_body.json().get('BSSResponse'))
    else:
        raise Exception(f"Unexpected exception. Received status {given_status_code}")


def _throw_http_400(bss_message_string: str):
    raise BSSBadData(bss_message_string)


def _throw_http_404(bss_message_string: str):
    raise BssResourceNotFound(bss_message_string)


def _throw_http_500(bss_message_string: str):
    raise BssServerError(bss_message_string)
