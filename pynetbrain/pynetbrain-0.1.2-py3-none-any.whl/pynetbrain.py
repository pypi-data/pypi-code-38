import requests
import json


__version__ = "0.1.2"


# Login NetBrain and get system token.
def loginSession(nb_url, username, password):
    full_url = nb_url + "/ServicesAPI/API/V1/Session"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    try:
        response = requests.post(full_url, headers=headers, auth=(username, password))
        if response.status_code == 200:
            token = response.json()["token"]
            return token
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Logout NetBrain and release system token.
def logoutSession(nb_url, token):
    full_url = nb_url + "/ServicesAPI/API/V1/Session"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    data = {"token": token}
    try:
        response = requests.delete(full_url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return "NetBrain Logout Successful!"
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Get all tenants info
def getTenants(nb_url, token):
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Tenants"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    try:
        response = requests.get(full_url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["tenants"]
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Get all domains info. If tenantId is None, will present all domains.
def getDomains(nb_url, token, tenantId=None):
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Domains"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    data = {"tenantId": tenantId}
    try:
        response = requests.get(full_url, params=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["domains"]
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Login specified domain
def loginDomain(nb_url, token, tenantId, domainId):
    full_url = nb_url + "/ServicesAPI/API/V1/Session/CurrentDomain"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    body = {"tenantId": tenantId, "domainId": domainId}
    try:
        response = requests.put(full_url, data=json.dumps(body), headers=headers)
        if response.status_code == 200:
            return "NetBrain Login Successful!"
        elif response.status_code != 200:
            return response.json()
    except Exception as e:
        return str(e)


# Create sites with full site path.
def createSites(nb_url, token, sites):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites"
    try:
        response = requests.post(
            full_url, data=json.dumps({"sites": sites}), headers=headers
        )
        if response.status_code == 200:
            return "CreateSites: Site Created successfully!"
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Create parent site with the site path.
def createParentSite(nb_url, token, sitePath):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites/Parent"
    try:
        response = requests.post(
            full_url, data=json.dumps({"sitePath": sitePath}), headers=headers
        )
        if response.status_code == 200:
            return "Site Created successfully!"
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Create child site with the site path.
def createChildSite(nb_url, token, sitePath):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites/Leaf"
    try:
        response = requests.post(
            full_url, data=json.dumps({"sitePath": sitePath}), headers=headers
        )
        if response.status_code == 200:
            return "Site Created successfully!"
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Create child site with the site path.
def deleteSite(nb_url, token, sitePath):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites/"
    try:
        response = requests.delete(
            full_url, params={"sitePath": sitePath}, headers=headers
        )
        if response.status_code == 200:
            return "Site Deleted successfully! - " + str(sitePath)
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Add devices into sites
def addSiteDevice(nb_url, token, siteId, sitePath, devices):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites/Devices"
    site = {"siteId": siteId, "sitePath": sitePath, "devices": devices}
    try:
        response = requests.post(full_url, data=json.dumps(site), headers=headers)
        if response.status_code == 200:
            return "AddSiteDevice: Devices added successfully!"
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Remove all devices from site transaction, and add new devices to it
def replaceSiteDevice(nb_url, token, siteId, sitePath, devices):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites/Devices"
    site = {"siteId": siteId, "sitePath": sitePath, "devices": devices}
    try:
        response = requests.put(full_url, data=json.dumps(site), headers=headers)
        if response.status_code == 200:
            return "Device moved successfully!"
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Delete devices into sites
def deleteSiteDevice(nb_url, token, siteId, sitePath, devices):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites/Devices"
    site = {"siteId": siteId, "sitePath": sitePath, "devices": devices}
    try:
        response = requests.delete(full_url, data=json.dumps(site), headers=headers)
        if response.status_code == 200:
            return "Devices removed successfully!"
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Get all leaf sites of a container site, either siteID or sitePath need to be provided; siteID if both provided.
def getChildSites(nb_url, token, sitePath):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites/ChildSites"
    data = {"sitePath": sitePath}
    try:
        response = requests.get(full_url, params=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["sites"]
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Get basic information of a site, either siteID or sitePath need to be provided; siteID if both provided.
def getSiteInfo(nb_url, token, sitePath):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites/SiteInfo"
    data = {"sitePath": sitePath}
    try:
        response = requests.get(full_url, params=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["siteInfo"]
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Get all devices that belong to the site specified by site name, either siteID or sitePath need to be provided; siteID if both provided.
def getSiteDevice(nb_url, token, sitePath):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Sites/Devices"
    data = {"sitePath": sitePath}
    try:
        response = requests.get(full_url, params=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["devices"]
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Get Devices
def getDevice(nb_url, token, hostname):
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Devices"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    query = {"hostname": hostname}
    try:
        response = requests.get(full_url, headers=headers, params=query)
        if response.status_code == 200:
            result = response.json()
            return result["devices"]
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Get device attribute
def getDeviceAttributes(nb_url, token, hostname, attributeName):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Devices/Attributes"
    body = {"hostname": hostname, "attributeName": attributeName}
    try:
        response = requests.get(full_url, params=body, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["attributes"]
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Get interfaces
def getInterfaces(nb_url, token, hostname):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Interfaces"
    body = {"hostname": hostname}
    try:
        response = requests.get(full_url, params=body, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["interfaces"]
        else:
            return response.json()
    except Exception as e:
        return str(e)


# Get interface attribute
def getInterfaceAttributes(nb_url, token, hostname, interfaceName, attributeName):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    headers["Token"] = token
    full_url = nb_url + "/ServicesAPI/API/V1/CMDB/Interfaces/Attributes"
    body = {
        "hostname": hostname,
        "interfaceName": interfaceName,
        "attributeName": attributeName,
    }
    try:
        response = requests.get(full_url, params=body, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return response.json()
    except Exception as e:
        return str(e)
