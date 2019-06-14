import requests
import json
import hashlib
import base64
import time
import hmac

# Account Info
access_id = "pQq3HjKQV2v4L2e9zXHA"
access_key = "Ggc_n}WTb2=K(q!2%56HZZH5GAtPEBBaW762+_dQ"
company = "itculate"

##Request Info
http_verb = "GET"
resource_path = "/device/devices/33"
# query_parameters = ""
query_parameters = "?fields=systemProperties"
data = ""

# Construct URL
url = "https://" + company + ".logicmonitor.com/santaba/rest" + resource_path + query_parameters

# Get current time in milliseconds
epoch = str(int(time.time() * 1000))

# Concatenate Request details
requestVars = http_verb + epoch + data + resource_path

# Construct signature
signature = base64.b64encode(hmac.new(access_key, msg=requestVars, digestmod=hashlib.sha256).hexdigest())

# Construct headers
auth = "LMv1 " + access_id + ":" + signature + ":" + epoch
headers = {"Content-Type": "application/json", "Authorization": auth}

# Make request
response = requests.get(url, data=data, headers=headers)

# Print status and body of response
print("URL:{}".format(url))
print("Response Status:{}".format(response.status_code))
print("Response Body:{}".format(response.content))

#
# #Request Info
# httpVerb ='GET'
# resource_path = '/device/devices'
# query_parameters = '?fields=id,category,displayName,systemProperties'
#
# data = ''
#
# #Construct URL
# url = 'https://' + Company +'.logicmonitor.com/santaba/rest' + resource_path +query_parameters
#
# #Get current time in milliseconds
# epoch = str(int(time.time() * 1000))
#
# #Concatenate Request details
# requestVars = httpVerb + epoch + data + resource_path
#
# #Construct signature
# signature = base64.b64encode(hmac.new(access_key,msg=requestVars,digestmod=hashlib.sha256).hexdigest())
#
# #Construct headers
# auth = 'LMv1 ' + access_id + ':' + signature + ':' + epoch
# headers = {'Content-Type':'application/json','Authorization':auth}
#
# #Make request
# response = requests.get(url, data=data, headers=headers)
#
# #Print status and body of response
# print 'Response Status:',response.status_code
# print 'Response Body:',response.content


a = {
    "status": 200,
    "errmsg": "OK",
    "data": {
        "id": 72,
        "name": "us-east-1:ec2:i-0e0cbbd186f4d0a20-19",
        "displayName": "US-E1:analytics.prod-us-east-1d.1_i-0e0cbbd186f4d0a20",
        "deviceType": 2,
        "relatedDeviceId": -1,
        "currentCollectorId": 2,
        "preferredCollectorId": 2,
        "preferredCollectorGroupId": 1,
        "preferredCollectorGroupName": "@default",
        "description": "Automatically discovered",
        "createdOn": 1524682846,
        "updatedOn": 1524682846,
        "disableAlerting": False,
        "autoPropsAssignedOn": 1526534872,
        "autoPropsUpdatedOn": 1526534872,
        "scanConfigId": 0,
        "link": "",
        "enableNetflow": False,
        "netflowCollectorId": 0,
        "netflowCollectorGroupId": 0,
        "netflowCollectorGroupName": None,
        "lastDataTime": 0,
        "lastRawdataTime": 0,
        "hostGroupIds": "19,50,4",
        "sdtStatus": "none-none-none",
        "userPermission": "write",
        "hostStatus": "normal",
        "alertStatus": "none",
        "alertStatusPriority": 100000,
        "awsState": 1,
        "azureState": 1,
        "alertDisableStatus": "none-none-none",
        "alertingDisabledOn": None,
        "collectorDescription": "ip-172-33-17-217.ec2.internal",
        "netflowCollectorDescription": None,
        "customProperties": [{
            "name": "snmp.version",
            "value": "v2c"
        }, {
            "name": "snmp.community",
            "value": "********"
        }, {
            "name": "system.categories",
            "value": "AWS/EC2,snmpTCPUDP,Netsnmp,snmpHR,collectorDataSources,snmpUptime,snmp"
        }],
        "upTimeInSeconds": 0,
        "deletedTimeInMs": 0,
        "toDeleteTimeInMs": 0,
        "hasDisabledSubResource": True,
        "ancestorHasDisabledLogicModule": True,
        "systemProperties": [{
            "name": "system.enablenetflow",
            "value": "False"
        }, {
            "name": "system.aws.tag.itculate-cluster-name",
            "value": "analytics-cluster"
        }, {
            "name": "system.aws.keyName",
            "value": "web"
        }, {
            "name": "system.aws.privateDnsName",
            "value": "ip-172-33-40-216.ec2.internal"
        }, {
            "name": "system.aws.region",
            "value": "us-east-1"
        }, {
            "name": "system.description",
            "value": "Automatically discovered"
        }, {
            "name": "system.aws.availabilityZone",
            "value": "us-east-1d"
        }, {
            "name": "system.aws.tag.Role",
            "value": "analytics"
        }, {
            "name": "system.aws.amiLaunchIndex",
            "value": "0"
        }, {
            "name": "system.prefcollectordesc",
            "value": "ip-172-33-17-217.ec2.internal"
        }, {
            "name": "system.aws.launchTime",
            "value": "1524681847000"
        }, {
            "name": "system.aws.rootDeviceType",
            "value": "ebs"
        }, {
            "name": "system.aws.sourceDestCheck",
            "value": "True"
        }, {
            "name": "system.groups",
            "value": "ITculate account/EC2,production analytics,Devices by Type/Linux Servers"
        }, {
            "name": "system.aws.tag.Name",
            "value": "analytics.prod-us-east-1d.1"
        }, {
            "name": "system.deviceGroupId",
            "value": "19,50,4"
        }, {
            "name": "system.collector",
            "value": "False"
        }, {
            "name": "system.aws.vpcId",
            "value": "vpc-05fda361"
        }, {
            "name": "system.ips",
            "value": "fe80:0:0:0:c91:c3ff:fe09:8878,172.33.40.216"
        }, {
            "name": "system.aws.stateCode",
            "value": "16"
        }, {
            "name": "system.aws.tag.ITculate-owner_email",
            "value": "ran@itculate.io"
        }, {
            "name": "system.aws.subnetId",
            "value": "subnet-b1cd17e9"
        }, {
            "name": "system.aws.hypervisor",
            "value": "xen"
        }, {
            "name": "system.prefcollectorid",
            "value": "2"
        }, {
            "name": "system.aws.publicDnsName",
            "value": "ec2-54-221-13-4.compute-1.amazonaws.com"
        }, {
            "name": "system.displayname",
            "value": "US-E1:analytics.prod-us-east-1d.1_i-0e0cbbd186f4d0a20"
        }, {
            "name": "system.awsrootgroupid",
            "value": "16"
        }, {
            "name": "system.categories",
            "value": "AWS/EC2,snmpTCPUDP,Netsnmp,snmpHR,collectorDataSources,snmpUptime,snmp"
        }, {
            "name": "system.hostname",
            "value": "us-east-1:ec2:i-0e0cbbd186f4d0a20-19"
        }, {
            "name": "system.sysinfo",
            "value": "Linux ip-172-33-40-216 3.13.0-125-generic #174-Ubuntu SMP Mon Jul 10 18:51:24 UTC 2017 x86_64"
        }, {
            "name": "system.aws.instanceType",
            "value": "m5.large"
        }, {
            "name": "system.aws.securityGroups",
            "value": "[{\"groupName\":\"prod-analytics-server\",\"groupId\":\"sg-3f134e44\"}]"
        }, {
            "name": "system.aws.ebsOptimized",
            "value": "False"
        }, {
            "name": "system.collectorplatform",
            "value": "linux"
        }, {
            "name": "system.aws.publicIpAddress",
            "value": "54.221.13.4"
        }, {
            "name": "system.aws.rootDeviceName",
            "value": "/dev/sda1"
        }, {
            "name": "system.cloud.category",
            "value": "AWS/EC2"
        }, {
            "name": "system.sysoid",
            "value": "1.3.6.1.4.1.8072.3.2.10"
        }, {
            "name": "system.aws.tag.ITculate-cluster",
            "value": "analytics"
        }, {
            "name": "system.aws.tag.VPC",
            "value": "prod"
        }, {
            "name": "system.cloud.monitoriptype",
            "value": "private"
        }, {
            "name": "system.aws.imageId",
            "value": "ami-841f46ff"
        }, {
            "name": "system.collectorid",
            "value": "2"
        }, {
            "name": "system.deviceId",
            "value": "72"
        }, {
            "name": "system.aws.monitoring",
            "value": "disabled"
        }, {
            "name": "system.aws.endpoint",
            "value": "ec2.us-east-1.amazonaws.com"
        }, {
            "name": "system.aws.virtualizationType",
            "value": "hvm"
        }, {
            "name": "system.aws.resourceid",
            "value": "i-0e0cbbd186f4d0a20"
        }, {
            "name": "system.aws.monitoringstate",
            "value": "1"
        }, {
            "name": "system.aws.blockDeviceMappings",
            "value": "[{\"volumeId\":\"vol-0549c3b025aa79611\",\"deleteOnTermination\":True,\"deviceName\":\"/dev/sda1\",\"attachTime\":1524681848000,\"status\":\"attached\"}]"
        }, {
            "name": "system.collectordesc",
            "value": "ip-172-33-17-217.ec2.internal"
        }, {
            "name": "system.aws.architecture",
            "value": "x86_64"
        }, {
            "name": "system.aws.arn",
            "value": "arn:aws:ec2:us-east-1:560754049107:instance/i-0e0cbbd186f4d0a20"
        }, {
            "name": "system.sysname",
            "value": "ip-172-33-40-216"
        }, {
            "name": "system.aws.stateName",
            "value": "running"
        }, {
            "name": "system.devicetype",
            "value": "2"
        }, {
            "name": "system.collectorversion",
            "value": "26001"
        }, {
            "name": "system.staticgroups",
            "value": "ITculate account/EC2"
        }, {
            "name": "system.aws.tag.itculate-cluster-topology",
            "value": "member"
        }, {
            "name": "system.aws.privateIpAddress",
            "value": "172.33.40.216"
        }],
        "autoProperties": [],
        "inheritedProperties": [{
            "name": "aws.accountid",
            "value": "560754049107"
        }, {
            "name": "netapp.ssl",
            "value": "True"
        }, {
            "name": "aws.externalid",
            "value": "14dda392-fbdb-42a1-ab46-30012e4a0302"
        }, {
            "name": "aws.assumedrolearn",
            "value": "arn:aws:iam::560754049107:role/LogicMonitorCrossCloud"
        }]
    }
}
