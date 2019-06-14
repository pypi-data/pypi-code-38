"""Used to import assets from CSV files"""
import csv, json, copy, re

from datetime import datetime
from argus_cli.plugin import register_command

# Authenticate
from api_generator.helpers.authentication import with_authentication

# API calls
from argus_api.api.assets.v1.host import add_host_asset, update_host_asset, search_host_assets, delete_host_asset
from argus_api.api.assets.v1.service import search_service_assets, attach_hosts_to_service
from argus_api.api.customers.v1.customer import get_customer_by_shortname
from api_generator.exceptions.http import ArgusException, ObjectNotFoundException

# CLI
from argus_cli.helpers.formatting import ask, success, failure
from argus_cli.helpers.log import logging
from argus_cli.helpers.collections import set_dotnotation
from argus_plugins import argus_cli_module

log = logging.getLogger("plugin").getChild("assets")

def diff(a: list, b: list):
    """Returns values from 'a' not found in 'b'"""
    return list(set(a) - set(b))

@register_command(extending=('assets', 'import'), module=argus_cli_module)
def hosts(
        customer: str,
        file_path: str,
        map_headers: list = tuple(),
        extra_json: str = None,
        field_separator: str = " ",
        headers_on_first_line: bool = False,
        always_yes: bool = False,
        api_key: str = None,
        splunk: bool = False,
        replace_hosts: bool = False,
        output: str = None,
        dry: bool = False
    ):
    """Imports assets from a CSV file

    Host assets *must* provide fields 'name' and 'ipAddresses'. If the file does not provide these fields, but have
    other names for these fields such as 'ip' and 'description', pass --map-headers ip:ipAddresses,description:name to
    map the headers to these names.

    A host may have multiple ipAddresses, these should be separated by a semicolon, like: 10.0.15.12;88.283.39.12

    Optional fields are:
        - operatingSystemCPE
        - type (SERVER or CLIENT, default: SERVER)
        - source (CVM or USER, default: USER)
        - aliases (list of aliases, separated by given field separator)
        - properties (additional properties to add to the host, formatted as JSON)

    You can add these fields using --extra-json type:CLIENT (to apply to all hosts), or as its
    own field in the CSV file.

    :param customer: Name of the customer to import assets for
    :param file_path: Path to the CSV file
    :param map_headers: Optional map of header names, e.g ipAddressv4:address,long_description:description
    :param field_separator: Separator used inside fields, e.g when providing multiple IP addresses or aliases. Defaults to whitespace.
    :param extra_json: Adds extra field: values to each JSON object read from CSV. Can be used to add missing fields
    :param headers_on_first_line: Whether headers should be taken from the first line in the CSV
    :param api_key: API key to authenticate with (otherwise password will be requested)
    :param splunk: If this flag is set, JSON data will be written and the log will be suppressed
    :param replace_hosts: If this flag is set, if an IP belongs to another host, that host will be deleted before creating a new host
    :param output: File to write results to (used in conjunction with the splunk flag)
    :param dry: If this is enabled, no modifying API calls will be made
    """

    headers = None

    # If headers are not on the first line of the CSV file
    # and we have a map of headers, create the header names
    # either by getting the last value of every old:new pair,
    # or just each value if there's no mapping
    if map_headers:
        headers = {
            (
             header.split(":")[0] if ":" in header else header
            ): (header.split(":")[1] if ":" in header else header)
            for header in map_headers
        }

    with open(file_path) as assets_file:
        try:
            assets = [
                asset
                for asset in csv.DictReader(
                    assets_file,
                    delimiter=",",
                    fieldnames=headers if not headers_on_first_line else None
                )
            ]
        except UnicodeDecodeError:
            raise ValueError(
                "This file seems to be corrupt, it contains strange bytes."
                "Please check the file encoding, and try to re-save the file"
            )

    if not assets and headers_on_first_line and not map_headers:
        raise ValueError(
            "CSV file was empty, or contained only one row "
            "but you did not define any headers so these were "
            "thought to be headers"
        )

    messages = []

    # Authorize our API calls
    authorize = with_authentication(api_key=api_key)
    get_customer = authorize(get_customer_by_shortname)
    add_asset = authorize(add_host_asset)
    update_asset = authorize(update_host_asset)
    delete_asset = authorize(delete_host_asset)

    # Get the customer, and fail if none was found
    try:
        customer = get_customer(customer)
    except ObjectNotFoundException:
        raise LookupError("No customer found for %s" % customer)

    # Search for all existing assets with the names we found
    existing_assets = authorize(search_host_assets)(
        keywords=[
            host["name"]
            for host in assets if "name" in host
        ],
        customerID=[customer["data"]["id"]],
        limit=10000
    )

    # ... and create a lookup table
    existing_assets = {
        asset["name"]: asset
        for asset in existing_assets["data"]
    }

    # ... also create a lookup table for IPs to allow removing old hosts
    existing_ip_assets = {}

    for host in existing_assets.values():
        for ipAddress in host["ipAddresses"]:
            existing_ip_assets[ipAddress["address"]] = host

    # Update asset dicts with names from map_headers
    if map_headers:
        for host in assets:
            for key, new_key in headers.items():
                host[new_key] = host.pop(key)

    # Merge IP addresses of assets with the same name
    uniqueHosts = {
        host["name"]: host for host in assets if "name" in host
    }

    for host in assets:
        uniqueHosts[host["name"]]["ipAddresses"] = (
            uniqueHosts[host["name"]]["ipAddresses"].split(field_separator) +
            host["ipAddresses"].split(field_separator)
        )
        uniqueHosts[host["name"]]["ipAddresses"] = field_separator.join(
            list(set(uniqueHosts[host["name"]]["ipAddresses"]))
        )

    services_to_attach_hosts = {
        # serviceName: [host1, host2]
    }

    for host in uniqueHosts.values():

        # These fields are required
        if "name" not in host or "ipAddresses" not in host:
            log.plugin(
                failure(
                    "Skipping. Required fields 'name' "
                    "and 'ipAddresses' not in %s" % str(host)
                )
            )
            continue

        host.update({
            'customerID': int(customer['data']['id']),
            'ipAddresses': host['ipAddresses'].split(field_separator),
            'properties': json.loads(host['properties']) if "properties" in host else {}
        })

        if extra_json:
            host.update(json.loads(extra_json))

        # Replace keys with dot notation (e.g criticality.availability) with
        # a nested dict instead:
        for key in [key for key in host.keys() if "." in key]:
            host = set_dotnotation(dict(**host), key, host[key])
            del host[key]

        host["name"] = re.sub(r"[^\s\w\{\}\$-().\[\]\"\'_\/\\,\*\+#:@!\?;-]", "", host["name"]).strip()

        # Check if any host already has any of these IPs, and ask the user if they want to remove
        # those hosts first
        for ip in host["ipAddresses"]:
            if ip in existing_ip_assets:
                existing_host = existing_ip_assets[ip]

                # Skip if the IPs are identical and the host name is identical
                if host["name"] == existing_host["name"] and \
                   sorted(host["ipAddresses"]) == sorted([ip["address"] for ip in existing_host["ipAddresses"]]):
                    continue

                # Keep track of host iD to associate services later on
                host.update({ "id": existing_host["id"] })

                if (replace_hosts and always_yes) or ask("A host already exists with IP %s" % ip):
                    # If the host has multiple IPs, update the host to remove this IP
                    if len(existing_host["ipAddresses"]) > 1:
                        try:
                            if not dry:
                                update_asset(
                                    existing_host["id"],
                                    deleteIpAddresses=[ip]
                                )
                            if splunk:
                                messages.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "message": "Updated %s and removed IP %s" % (existing_host["name"], ip),
                                    "name": existing_host["name"],
                                    "ip": existing_host["ipAddresses"],
                                    "body": {
                                        "id": existing_host["id"],
                                        "deleteIpAddresses": [ip]
                                    },
                                    "updated": True,
                                    "deleted": False,
                                    "created": False,
                                    "failure": False,
                                })
                            else:
                                log.plugin(
                                    success("Updated %s and removed IP %s" % (existing_host["name"], ip))
                                )
                        except ArgusException as error:
                            if splunk:
                                messages.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "message": "Failed to remove ip %s from %s: %s" % (ip, existing_host["name"], error),
                                    "name": existing_host["name"],
                                    "ip": existing_host["ipAddresses"],
                                    "body": {
                                        "id": existing_host["id"],
                                        "deleteIpAddresses": [ip]
                                    },
                                    "updated": False,
                                    "created": False,
                                    "deleted": False,
                                    "failure": True,
                                })
                            else:
                                log.plugin(
                                    failure("Failed to remove ip %s from %s: %s" % (ip, existing_host["name"], error))
                                )

                    # If the host only has one IP, delete the host altogether
                    else:
                        try:
                            if not dry:
                                delete_asset(
                                    existing_host["id"]
                                )
                            if splunk:
                                messages.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "message": "Removed host %s" % (existing_host["name"]),
                                    "name": existing_host["name"],
                                    "ip": existing_host["ipAddresses"],
                                    "body": {
                                        "id": existing_host["id"],
                                    },
                                    "updated": False,
                                    "deleted": True,
                                    "created": False,
                                    "failure": False,
                                })
                            else:
                                log.plugin(
                                    success("Removed host %s" % (existing_host["name"]))
                                )
                        except ArgusException as error:
                            if splunk:
                                messages.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "message": "Failed to remove host %s: %s" % (existing_host["name"], error),
                                    "name": existing_host["name"],
                                    "ip": existing_host["ipAddresses"],
                                    "body": {
                                        "id": existing_host["id"],
                                    },
                                    "updated": False,
                                    "created": False,
                                    "deleted": False,
                                    "failure": True,
                                })
                            else:
                                log.plugin(
                                    failure("Failed to remove ip %s from %s: %s" % (ip, existing_host["name"], error))
                                )


        # Add services to host if host has any services
        if "services" in host:
            for service in host['services'].split(';'):
                if service.strip() in services_to_attach_hosts:
                    services_to_attach_hosts[service.strip()].append(host)
                else:
                    services_to_attach_hosts[service.strip()] = [host]

        if host["name"] in existing_assets:
            host.update({ "id": existing_assets[host["name"]]["id"] })

            if always_yes or ask("%s already exists, do you want to update it?" % host["name"]):
                current_asset = existing_assets[host["name"]]
                try:
                    current_ips_with_range = [ "%s/%d" % (ip["address"], ip["maskBits"]) for ip in current_asset["ipAddresses"]]
                    given_ips_with_range = [ "%s/32" % ip if "/" not in ip else ip for ip in host["ipAddresses"] ]

                    host.update({
                        "addIpAddresses": diff(given_ips_with_range, current_ips_with_range),
                        "deleteIpAddresses": diff(current_ips_with_range, given_ips_with_range)
                    })

                    if "aliases" in host:
                        host.update({
                            "addAliases": diff(host["aliases"].split(field_separator), [ alias["fqdn"] for alias in current_asset["aliases"] ]),
                            "deleteAliases": diff([ alias["fqdn"] for alias in current_asset["aliases"] ], host["aliases"].split(field_separator)),
                        })

                    if "properties" in host:
                        host.update({
                            "addProperties": {
                                property: value
                                for property, value in host["properties"].items()
                                if property in diff(host["properties"].keys(), current_asset["properties"].keys())
                            },
                            "deleteProperties": diff(current_asset["properties"].keys(), host["properties"].keys())
                        })

                    # Skip updating if nothing has changed
                    criticality_unchanged = (
                        "criticality" not in host
                        or host["criticality"] == {
                            key: value
                            for key, value in existing_host["criticality"].items()
                            if key in host["criticality"]
                        }
                    )

                    # Skip updating if nothing has changed
                    if not host["addIpAddresses"] and not host["deleteIpAddresses"] \
                            and not host.get("addAliases") and not host.get("deleteAliases") \
                            and not host.get("addProperties") and not host.get("deleteProperties") \
                            and host["description"] == current_asset["description"] \
                            and criticality_unchanged:
                        continue

                    if not dry:
                        update_asset(
                            existing_assets[host["name"]]["id"],
                            **{
                                field: value
                                for field, value in host.items()
                                if field not in ('ipAddresses', 'customerID', 'properties', 'aliases', 'services', 'id')
                            }
                        )
                    if splunk:
                        messages.append({
                            "timestamp": datetime.now().isoformat(),
                            "message": "Updated %s" % host["name"],
                            "name": host["name"],
                            "ip": host["ipAddresses"],
                            "body": {
                                field: value
                                for field, value in host.items()
                                if field not in ('ipAddresses', 'customerID', 'properties', 'aliases', 'services', 'id')
                            },
                            "updated": True,
                            "created": False,
                            "deleted": False,
                            "failure": False,
                        })
                    else:
                        log.plugin(
                            success("Updated %s" % host["name"])
                        )
                except ArgusException as error:
                    if splunk:
                        messages.append({
                            "timestamp": datetime.now().isoformat(),
                            "message": "Failed to update %s: %s" % (host["name"], error),
                            "name": host["name"],
                            "ip": host["ipAddresses"],
                            "body": {
                                field: value
                                for field, value in host.items()
                                if field not in ('ipAddresses', 'customerID', 'properties', 'aliases', 'services', 'id')
                            },
                            "updated": False,
                            "created": False,
                            "deleted": False,
                            "failure": True,
                        })
                    else:
                        log.plugin(
                            failure("Failed to update %s: %s" % (host["name"], error))
                        )
        else:
            try:
                if not dry:
                    created_asset = add_asset(**{
                        key: value
                        for key, value in host.items()
                        if key not in ('services', 'id')
                    })

                    if "data" in created_asset and created_asset["data"]:
                        host["id"] = created_asset["data"]["id"]
                if splunk:
                    messages.append({
                        "timestamp": datetime.now().isoformat(),
                        "message": "Created %s (%s)" % (host["name"], ", ".join(host["ipAddresses"])),
                        "name": host["name"],
                        "ip": host["ipAddresses"],
                        "body": host,
                        "updated": False,
                        "created": True,
                        "failure": False,
                        "deleted": False,
                    })
                else:
                    log.plugin(
                        success("Created %s (%s)" % (host["name"], ", ".join(host["ipAddresses"])))
                    )
            except ArgusException as error:
                if splunk:
                        messages.append({
                            "timestamp": datetime.now().isoformat(),
                            "message": "Failed to create %s: %s" % (host["name"], error),
                            "name": host["name"],
                            "ip": host["ipAddresses"],
                            "body": host,
                            "updated": False,
                            "created": False,
                            "failure": True,
                            "deleted": False,
                        })
                else:
                    log.plugin(
                        failure("Failed to create %s: %s" % (host["name"], error))
                    )


        if splunk and messages:
            if output:
                with open(output, "w") as json_file:
                    json_file.write(json.dumps(messages, indent=4, sort_keys=True))
            else:
                print(json.dumps(messages))

    for service_name, host_list in services_to_attach_hosts.items():
        try:
            for service in authorize(search_service_assets)(name=[service_name], customerID=[int(customer['data']['id'])])["data"]:
                if service["name"] == service_name:
                    try:
                        if not dry:
                            authorize(attach_hosts_to_service)(
                                id=service["id"],
                                hostAssetIDs=[host["id"] for host in host_list if "id" in host]
                            )
                            if splunk:
                                print(
                                    json.dumps({
                                        "timestamp": datetime.now().isoformat(),
                                        "message": "Attached %d hosts to service %s" % (len(host_list), service_name),
                                        "name": service_name,
                                        "hosts": host_list,
                                        "updated": True,
                                        "created": False,
                                        "deleted": False,
                                        "failure": False,
                                    })
                                )
                            else:
                                log.plugin(
                                    failure("Attached %d hosts to service %s" % (len(host_list), service_name))
                                )
                    except ArgusException as error:
                        if splunk:
                            print(
                                json.dumps({
                                    "timestamp": datetime.now().isoformat(),
                                    "message": "Failed to attach hosts to service %s: %s" % (service_name, error),
                                    "name": service_name,
                                    "hosts": host_list,
                                    "updated": False,
                                    "created": False,
                                    "deleted": False,
                                    "failure": True,
                                })
                            )
                        else:
                            log.plugin(
                                failure("Failed to attach hosts to service %s: %s" % (service_name, error))
                            )

        except ArgusException as error:
            if splunk:
                print(
                    json.dumps({
                        "timestamp": datetime.now().isoformat(),
                        "message": "Failed to look up service %s: %s" % (service_name, error),
                        "name": service_name,
                        "updated": False,
                        "created": False,
                        "deleted": False,
                        "failure": True,
                    })
                )
            else:
                log.plugin(
                    failure("Failed to look up service %s" % (service_name, error))
                )
