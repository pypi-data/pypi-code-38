#!/usr/bin/env python

import os
import sys
import syslog
import datetime
import requests
import json
import urllib3
import urllib3.contrib.pyopenssl
from urllib3.exceptions import HTTPError as BaseHTTPError
import certifi
from multiprocessing import Process, Pipe
sys.path.append('/home/guestshell/.local/lib/python2.7/site-packages/csr_azure_guestshell/TokenMgr')
import token_api

event_dir = "/home/guestshell/azure/HA/events"
get_response_file = event_dir + '/routeTableGetRsp'
set_response_file = event_dir + '/routeTableSetRsp'
cert_file = "/etc/ssl/certs/ca-bundle.trust.crt"


def dbg_log(fp, msg):
    full_msg = '\n' + msg
    fp.write(full_msg)
    fp.flush()

def verify_node(node, event_type, debug_fh):

    if event_type == 'verify':
        node_verified = True
        if (not (node.has_key('cloud'))):
            dbg_log(debug_fh, "Missing required parameter -c cloud")
            node_verified = False
        if (not (node.has_key('subscriptionId'))):
            dbg_log(debug_fh, "Missing required parameter -s subscriptionId")
            node_verified = False
        if (not (node.has_key('resourceGroup'))):
            dbg_log(debug_fh, "Missing required parameter -g resourceGroup")
            node_verified = False
        if (not (node.has_key('routeTableName'))):
            dbg_log(debug_fh, "Missing required parameter -t routeTableName")
            node_verified = False
        if (not (node.has_key('nextHop'))):
            dbg_log(debug_fh, "Missing required parameter -n nextHopIpAddress")
            node_verified = False
        if node.has_key('appId'):
            if (not (node.has_key('tenantId'))):
                dbg_log(debug_fh, "Missing required parameter -d tenantId")
                node_verified = False
            if (not (node.has_key('appKey')) ) :
                dbg_log(debug_fh, "Missing required parameter -k applicationKey")
                node_verified = False

        if node_verified:
            dbg_log(debug_fh, "All required parameters have been provided")
            return 'OK'
        else:
            return 'ERR1'
             
    else:       
        if ((node.has_key('index')) and
            (node.has_key('cloud')) and
            (node.has_key('routeTableName')) and
            (node.has_key('subscriptionId')) and
            (node.has_key('resourceGroup')) and
            (node.has_key('nextHop'))) :

            if node.has_key('appId'):
                if (not (node.has_key('tenantId'))):
                    return "ERR1"
                elif (not (node.has_key('appKey')) ) :
                    return "ERR1"
                
            return 'OK'
        else:
            dbg_log(debug_fh, "verify_node: missing required parameter")
            return "ERR1"
            
    
def obtain_token(node, event_type, debug_fh):
    token = ''
    if 'appId' in node:
        appId = node['appId']
        # AppId has been specified. Use AAD to get a token
        token = token_api.get_token_by_aad(node['cloud'],
                                               node['tenantId'],
                                               node['appId'],
                                               node['appKey'])
        if event_type == 'verify':
            dbg_log(debug_fh, "Requesting token using Azure Active Directory")
            dbg_log(debug_fh, "Token=%s" % token)

    else:
        # No AppId specified.  Use MSI to get token.
        token = token_api.get_token_by_msi(node['cloud'])
        if event_type == 'verify':
            dbg_log(debug_fh, "Requesting token using Managed Service Identity")
            dbg_log(debug_fh, "Token=%s" % token)

    if token == '':
        dbg_log(debug_fh, "Failed to obtain token")
            
    return token


def get_route_table(node, event_type, token, debug_fh):
    
    # Specify the HTTP GET request to read the route table
    apiversion = "2017-10-01"
    auth_header = "Bearer " + token
    all_headers = {'Content-Type':'application/x-www-form-urlencoded',
                   'Accept':'application/json',
                   'Authorization':auth_header}
    
    if node['cloud'] == 'azure':
        url="https://management.azure.com/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/routeTables/%s?api-version=%s" % (node['subscriptionId'], node['resourceGroup'], node['routeTableName'], apiversion)
    elif node['cloud'] == 'azusgov':
        url="https://management.usgovcloudapi.net/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/routeTables/%s?api-version=%s" % (node['subscriptionId'], node['resourceGroup'], node['routeTableName'], apiversion)
    else:
        dbg_log(debug_fh, "Unknown cloud name %s" % node['cloud'])

    # Send the HTTP GET request for the route table
    try:
        response = requests.get(url, verify=cert_file, headers=all_headers)
    except requests.exceptions.RequestException as e:
        dbg_log(debug_fh, "get_route_table: request had error %s" % e)
        return None

    if 200 == response.status_code :
        # Write the HTTP GET response to a file for debugging purposes
        if event_type == 'verify':
            with open(get_response_file, 'w') as resp_fh:
                for chunk in response.iter_content(chunk_size=64):
                    resp_fh.write(chunk)
            dbg_log(debug_fh, "Read route table successfully")

    else:
        dbg_log(debug_fh, "Route GET request failed with code %d" % response.status_code)
        with open(get_response_file, 'w') as resp_fh:
            resp_fh.write(response.text)
        return None

    # Extract the routes section from the table
    route_table = response.json()
    routes = route_table['properties']['routes']

    if routes == '':
        dbg_log(debug_fh, "No routes found in table")
        with open(get_response_file, 'w') as resp_fh:
            resp_fh.write(response.json())
        return None

    return route_table


def set_one_route(node, event_type, route_table, token, debug_fh, event_file):
    if event_type == 'verify':
        dbg_log(debug_fh, "Evaluating single route in route table for event type %s" % event_type)

    if route_table == '':
        dbg_log(debug_fh, "No route table entries found")
        if event_type == 'verify':
            dbg_log(debug_fh, "It is likely permission to access the route table was not granted.")
        return 
        
    send_request = False
    found_route = False

    # Walk through all the routes in the current route table
    for i, route in enumerate(route_table["properties"]["routes"]):
        # Updating a single route in the table.  Need to find the right one.
        if node['route'] == route['properties']['addressPrefix']:
            # This is the one
            found_route = True
            if event_type == 'verify':
                # Don't change the route
                newNextHop = route['properties']['nextHopIpAddress']
                send_request = True
            elif event_type == 'peerFail':
                newNextHop = node['nextHop']
                send_request = True
            elif event_type == 'revert':
                newNextHop = node['nextHop']
                if route['properties']['nextHopIpAddress'] == node['nextHop']:
                    send_request = False
                else:
                    send_request = True
                    syslog.syslog("Azure HA: %s event for route table %s in resource group %s" %
                      (event_type, node['routeTableName'], node['resourceGroup']))
            else:
                dbg_log(debug_fh, "Invalid event type %s in set_route_table" % event_type)
                return
            break
        
    # Did we find the route?
    if found_route == False:
        dbg_log(debug_fh, "Did not find route %s event type %s" % (node['route'], event_type))
        return

    if send_request == False:
        if event_type == 'verify':
            dbg_log(debug_fh, "Verify event: No need to update single route in route table")
        if event_type == 'revert':
            # No action taken by this revert event. Delete the event log file
            debug_fh.close()
            os_command = "rm \"%s\"" % event_file
            os.system(os_command)
        return    

    # Specify the HTTP PUT request to write the route table
    # Set the URL
    apiversion = "2017-10-01"
    if node['cloud'] == 'azure':
        url="https://management.azure.com/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/routeTables/%s/routes/%s?api-version=%s" % (node['subscriptionId'], node['resourceGroup'], node['routeTableName'], route['name'], apiversion)
    elif node['cloud'] == 'azusgov':
        url="https://management.usgovcloudapi.net/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/routeTables/%s/routes/%s?api-version=%s" % (node['subscriptionId'], node['resourceGroup'], node['routeTableName'], route['name'], apiversion)
    else:
        dbg_log(debug_fh, "Unknown cloud name %s" % node['cloud']) 

    # Set the headers
    auth_header = "Bearer " + token
    all_headers = {'Content-Type':'application/json',
                   'Accept':'application/json',
                   'Authorization':auth_header}

    # Build the payload
    payload = "{\"properties\":{\"addressPrefix\":\"%s\", \"nextHopType\":\"%s\", \"nextHopIpAddress\":\"%s\"}}" % (route['properties']['addressPrefix'], route['properties']['nextHopType'], newNextHop)
    
    if event_type == 'verify':
        dbg_log(debug_fh, "Updating single route in route table")
        dbg_log(debug_fh, "URL=%s" % url)
        for key in all_headers:
            dbg_log(debug_fh, "%s:%s" % (key, all_headers[key]))
        dbg_log(debug_fh, "Payload=%s" % payload)
        
    # Send the PUT request
    try:
        response = requests.put(url, data=payload, verify=cert_file, headers=all_headers)
    except requests.exceptions.RequestException as e:
        dbg_log(debug_fh, "set_one_route: request had error %s" % e)
        return

    write_rsp_to_file = False
    if 200 == response.status_code :                                     
        dbg_log(debug_fh, "HTTP PUT of route table was successful")
        syslog.syslog("Azure HA: updated route %s to %s" % (route['name'], newNextHop))
        # Write the HTTP SET response to a file for debugging purposes
        if event_type == 'verify':
            write_rsp_to_file = True

        # Extract the routes section from the table
        put_response = response.json()
        provisionState = put_response['properties']['provisioningState']

        if event_type == 'verify':
            dbg_log(debug_fh, "Set route provision state is %s" % provisionState)

        if provisionState == 'Failed':
            dbg_log(debug_fh, "Set route provisioning state failed")
            write_rsp_to_file = True
    else:
        dbg_log(debug_fh, "Set route HTTP request failed rc=%d" % response.status_code)
        syslog.syslog("Azure HA: set route failed for route %s code=%d" %
                      (route['name'], response.status_code))
        write_rsp_to_file = True

    if write_rsp_to_file == True:
        with open(set_response_file, 'wb') as resp_fh:
            for chunk in response.iter_content(chunk_size=64):
                resp_fh.write(chunk)

    return


def set_all_routes(node, event_type, route_table, token, debug_fh):
    if event_type == 'verify':
        dbg_log(debug_fh, "Evaluating all routes in route table for event type %s" % event_type)

    send_request = False

    # The etag can contain quotation marks which must be escaped
    current_etag = route_table['etag']
    new_etag = ''
    tag_len = len(current_etag)
    for i in range(tag_len):
        if current_etag[i] == '\"':
            new_etag = new_etag + '\\'
        new_etag = new_etag + current_etag[i]
                                                        
    payload = "{\"location\":\"%s\", \"etag\":\"%s\", \"properties\":{\"routes\":[" % (route_table['location'], new_etag)

    # Walk through all the routes in the current route table
    routes = route_table['properties']['routes']
    for i, route in enumerate(routes):
        if route['properties']['nextHopType'] == 'VirtualAppliance':
            if event_type == 'verify':
                # Don't change the route
                newNextHop = route['properties']['nextHopIpAddress']
                send_request = True
            elif event_type == 'peerFail':
                newNextHop = node['nextHop']
                send_request = True   
            elif event_type == 'revert':
                newNextHop = node['nextHop']
                if route['properties']['nextHopIpAddress'] != node['nextHop']:
                    send_request = True
            else:
                 dbg_log(debug_fh, " Invalid event type %s in set_route_table" % event_type)
                 return

            payload = payload + "{\"name\":\"%s\", \"id\":\"%s\", \"properties\":{\"addressPrefix\":\"%s\", \"nextHopType\":\"%s\", \"nextHopIpAddress\":\"%s\"}}," % (route['name'], route['id'], route['properties']['addressPrefix'], route['properties']['nextHopType'], newNextHop)

        else:
            # These route types have no explicit next hop IP address
            payload = payload + "{\"name\":\"%s\", \"id\":\"%s\", \"properties\":{\"addressPrefix\":\"%s\", \"nextHopType\":\"%s\"}}," % (route['name'], route['id'], route['properties']['addressPrefix'], route['properties']['nextHopType'])

    payload = payload + ']}}'

    if send_request == False:
        if event_type == 'verify':
            dbg_log(debug_fh, "No need to update any routes in route table")
        else:
            debug_fh.close()
            os_command = "rm \"%s\"" % event_file
            os.system(os_command)
        return    

    # Specify the HTTP PUT request to write the route table
    # Set the URL
    apiversion = "2017-10-01"
    if node['cloud'] == 'azure':
        url="https://management.azure.com/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/routeTables/%s?api-version=%s" % (node['subscriptionId'], node['resourceGroup'], route_table['name'], apiversion)
    elif node['cloud'] == 'azusgov':
        url="https://management.usgovcloudapi.net/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/routeTables/%s?api-version=%s" % (node['subscriptionId'], node['resourceGroup'], route_table['name'], apiversion)
    else:
        dbg_log(debug_fh, "Unknown cloud name %s" % node['cloud'])  

    # Set the headers
    auth_header = "Bearer " + token
    all_headers = {'Content-Type':'application/json',
                   'Accept':'application/json',
                   'Authorization':auth_header}

    dbg_log(debug_fh, "URL=%s" % url)
    dbg_log(debug_fh, "Headers=%s" % all_headers)
    dbg_log(debug_fh, "Payload=%s" % payload)
        
    
    # Send the PUT request
    dbg_log(debug_fh, "Updating all routes in route table")
    try:
        response = requests.put(url, headers=all_headers, data=payload, verify=cert_file)
    except requests.exceptions.RequestException as e:
        dbg_log(debug_fh, "set_all_routes: request had error %s" % e)
        return

    write_rsp_to_file = False
    if 200 == response.status_code :                                     
        # Write the HTTP SET response to a file for debugging purposes
        syslog.syslog("Azure HA: updated all routes in table %s to %s" %
                      (node['routeTableName'], newNextHop))
        if event_type == 'verify':
            write_rsp_to_file = True 
    else:
        dbg_log(debug_fh, "Set route request failed rc=%d" % response.status_code)
        syslog.syslog("Azure HA: failed to set all routes in table %s code=%d" %
                      (node['routeTableName'], response.status_code))
        write_rsp_to_file = True

    if write_rsp_to_file == True:
        with open(set_response_file, 'wb') as resp_fh:
            for chunk in response.iter_content(chunk_size=64):
                resp_fh.write(chunk)

    return


def set_route_table(node, event_type, route_table, token, debug_fh, event_file):
    # Are we changing all route entries, or just a specific one?
    if 'route' in node:
        # Updating a specific route in the table
        set_one_route(node, event_type, route_table, token, debug_fh, event_file)
    else:
        # Updating all routes in the table
        set_all_routes(node, event_type, route_table, token, debug_fh)



def handler(node, event_type):
    try:
        timestamp = str(datetime.datetime.now())
        event_file = "%s/event.%s" % (event_dir, timestamp)
        debug_fh = open(event_file, "w+")

        dbg_log(debug_fh, "Event type is %s" % event_type)

        for key in node:
            param_str = "%s \t%s " % (key, node[key])
            dbg_log(debug_fh, param_str)

        # Verify the node has been sufficiently configured
        rc = verify_node(node, event_type, debug_fh)
        if 'OK' != rc:
            dbg_log(debug_fh, "Event processing aborted")
            debug_fh.close()
            return
    
        token = obtain_token(node, event_type, debug_fh)
         
        if event_type == 'verify':
            dbg_log(debug_fh, "Reading route table")
        elif event_type == 'peerFail':
            syslog.syslog("Azure HA: %s event for route table %s in resource group %s" %
                          (event_type, node['routeTableName'], node['resourceGroup']))
                          
        route_table = get_route_table(node, event_type, token, debug_fh)
        if route_table == None:
            return
    
        if event_type == 'verify':
            dbg_log(debug_fh, "Writing route table")
        set_route_table(node, event_type, route_table, token, debug_fh, event_file)
    
        if event_type == 'verify':
            dbg_log(debug_fh, "Event handling completed")
        debug_fh.close()

    except Exception as e:
        dbg.log(debug_fh, 'ERR', "Event handler caught exception %s" % e)
        tb = traceback.format_exc()
        dbg.log(debug_fh, 'ERR', "%s" % tb)
        debug_fh.close


def handle_event(node, event_type):
    try:
        p = Process(target=handler, args=(node, event_type))
        p.start()
        p.join()

    except Exception as e:
        dbg.log(debug_fh, 'ERR', "HA server caught exception %s" % e)
        tb = traceback.format_exc()
        dbg.log(debug_fh, 'ERR', "%s" % tb)


