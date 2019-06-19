#!/usr/bin/env python

#
# Generated Tue Jun 18 18:37:22 2019 by generateDS.py version 2.32.0.
# Python 2.7.5 (default, Jul 13 2018, 13:06:57)  [GCC 4.8.5 20150623 (Red Hat 4.8.5-28)]
#
# Command line options:
#   ('-q', '')
#   ('-f', '')
#   ('-o', 'pyone/bindings/supbind.py')
#   ('-s', 'pyone/bindings/__init__.py')
#   ('--super', 'supbind')
#   ('--external-encoding', 'utf-8')
#   ('--silence', '')
#
# Command line arguments:
#   ../../../share/doc/xsd/index.xsd
#
# Command line:
#   /var/lib/jenkins/jobs/new-init/workspace/opennebula-5.8.3/src/oca/python/bin/generateDS -q -f -o "pyone/bindings/supbind.py" -s "pyone/bindings/__init__.py" --super="supbind" --external-encoding="utf-8" --silence ../../../share/doc/xsd/index.xsd
#
# Current working directory (os.getcwd()):
#   python
#

import os
import sys
from pyone.util import TemplatedType
from lxml import etree as etree_

from . import supbind as supermod

def parsexml_(infile, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        parser = etree_.ETCompatXMLParser()
    try:
        if isinstance(infile, os.PathLike):
            infile = os.path.join(infile)
    except AttributeError:
        pass
    doc = etree_.parse(infile, parser=parser, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'utf-8'

#
# Data representation classes
#


class HISTORY_RECORDSSub(TemplatedType, supermod.HISTORY_RECORDS):
    def __init__(self, HISTORY=None, **kwargs_):
        super(HISTORY_RECORDSSub, self).__init__(HISTORY,  **kwargs_)
supermod.HISTORY_RECORDS.subclass = HISTORY_RECORDSSub
# end class HISTORY_RECORDSSub


class HISTORYSub(TemplatedType, supermod.HISTORY):
    def __init__(self, OID=None, SEQ=None, HOSTNAME=None, HID=None, CID=None, STIME=None, ETIME=None, VM_MAD=None, TM_MAD=None, DS_ID=None, PSTIME=None, PETIME=None, RSTIME=None, RETIME=None, ESTIME=None, EETIME=None, ACTION=None, UID=None, GID=None, REQUEST_ID=None, VM=None, **kwargs_):
        super(HISTORYSub, self).__init__(OID, SEQ, HOSTNAME, HID, CID, STIME, ETIME, VM_MAD, TM_MAD, DS_ID, PSTIME, PETIME, RSTIME, RETIME, ESTIME, EETIME, ACTION, UID, GID, REQUEST_ID, VM,  **kwargs_)
supermod.HISTORY.subclass = HISTORYSub
# end class HISTORYSub


class CLUSTER_POOLSub(TemplatedType, supermod.CLUSTER_POOL):
    def __init__(self, CLUSTER=None, **kwargs_):
        super(CLUSTER_POOLSub, self).__init__(CLUSTER,  **kwargs_)
supermod.CLUSTER_POOL.subclass = CLUSTER_POOLSub
# end class CLUSTER_POOLSub


class CLUSTERSub(TemplatedType, supermod.CLUSTER):
    def __init__(self, ID=None, NAME=None, HOSTS=None, DATASTORES=None, VNETS=None, TEMPLATE=None, **kwargs_):
        super(CLUSTERSub, self).__init__(ID, NAME, HOSTS, DATASTORES, VNETS, TEMPLATE,  **kwargs_)
supermod.CLUSTER.subclass = CLUSTERSub
# end class CLUSTERSub


class DATASTORE_POOLSub(TemplatedType, supermod.DATASTORE_POOL):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_POOLSub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_POOL.subclass = DATASTORE_POOLSub
# end class DATASTORE_POOLSub


class DATASTORESub(TemplatedType, supermod.DATASTORE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, DS_MAD=None, TM_MAD=None, BASE_PATH=None, TYPE=None, DISK_TYPE=None, STATE=None, CLUSTERS=None, TOTAL_MB=None, FREE_MB=None, USED_MB=None, IMAGES=None, TEMPLATE=None, **kwargs_):
        super(DATASTORESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, DS_MAD, TM_MAD, BASE_PATH, TYPE, DISK_TYPE, STATE, CLUSTERS, TOTAL_MB, FREE_MB, USED_MB, IMAGES, TEMPLATE,  **kwargs_)
supermod.DATASTORE.subclass = DATASTORESub
# end class DATASTORESub


class GROUP_POOLSub(TemplatedType, supermod.GROUP_POOL):
    def __init__(self, GROUP=None, QUOTAS=None, DEFAULT_GROUP_QUOTAS=None, **kwargs_):
        super(GROUP_POOLSub, self).__init__(GROUP, QUOTAS, DEFAULT_GROUP_QUOTAS,  **kwargs_)
supermod.GROUP_POOL.subclass = GROUP_POOLSub
# end class GROUP_POOLSub


class GROUPSub(TemplatedType, supermod.GROUP):
    def __init__(self, ID=None, NAME=None, TEMPLATE=None, USERS=None, ADMINS=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, DEFAULT_GROUP_QUOTAS=None, **kwargs_):
        super(GROUPSub, self).__init__(ID, NAME, TEMPLATE, USERS, ADMINS, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, DEFAULT_GROUP_QUOTAS,  **kwargs_)
supermod.GROUP.subclass = GROUPSub
# end class GROUPSub


class HOST_POOLSub(TemplatedType, supermod.HOST_POOL):
    def __init__(self, HOST=None, **kwargs_):
        super(HOST_POOLSub, self).__init__(HOST,  **kwargs_)
supermod.HOST_POOL.subclass = HOST_POOLSub
# end class HOST_POOLSub


class HOSTSub(TemplatedType, supermod.HOST):
    def __init__(self, ID=None, NAME=None, STATE=None, IM_MAD=None, VM_MAD=None, LAST_MON_TIME=None, CLUSTER_ID=None, CLUSTER=None, HOST_SHARE=None, VMS=None, TEMPLATE=None, **kwargs_):
        super(HOSTSub, self).__init__(ID, NAME, STATE, IM_MAD, VM_MAD, LAST_MON_TIME, CLUSTER_ID, CLUSTER, HOST_SHARE, VMS, TEMPLATE,  **kwargs_)
supermod.HOST.subclass = HOSTSub
# end class HOSTSub


class IMAGE_POOLSub(TemplatedType, supermod.IMAGE_POOL):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_POOLSub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_POOL.subclass = IMAGE_POOLSub
# end class IMAGE_POOLSub


class IMAGESub(TemplatedType, supermod.IMAGE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LOCK=None, PERMISSIONS=None, TYPE=None, DISK_TYPE=None, PERSISTENT=None, REGTIME=None, SOURCE=None, PATH=None, FSTYPE=None, SIZE=None, STATE=None, RUNNING_VMS=None, CLONING_OPS=None, CLONING_ID=None, TARGET_SNAPSHOT=None, DATASTORE_ID=None, DATASTORE=None, VMS=None, CLONES=None, APP_CLONES=None, TEMPLATE=None, SNAPSHOTS=None, **kwargs_):
        super(IMAGESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LOCK, PERMISSIONS, TYPE, DISK_TYPE, PERSISTENT, REGTIME, SOURCE, PATH, FSTYPE, SIZE, STATE, RUNNING_VMS, CLONING_OPS, CLONING_ID, TARGET_SNAPSHOT, DATASTORE_ID, DATASTORE, VMS, CLONES, APP_CLONES, TEMPLATE, SNAPSHOTS,  **kwargs_)
supermod.IMAGE.subclass = IMAGESub
# end class IMAGESub


class MARKETPLACEAPP_POOLSub(TemplatedType, supermod.MARKETPLACEAPP_POOL):
    def __init__(self, MARKETPLACEAPP=None, **kwargs_):
        super(MARKETPLACEAPP_POOLSub, self).__init__(MARKETPLACEAPP,  **kwargs_)
supermod.MARKETPLACEAPP_POOL.subclass = MARKETPLACEAPP_POOLSub
# end class MARKETPLACEAPP_POOLSub


class MARKETPLACEAPPSub(TemplatedType, supermod.MARKETPLACEAPP):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, LOCK=None, REGTIME=None, NAME=None, ZONE_ID=None, ORIGIN_ID=None, SOURCE=None, MD5=None, SIZE=None, DESCRIPTION=None, VERSION=None, FORMAT=None, APPTEMPLATE64=None, MARKETPLACE_ID=None, MARKETPLACE=None, STATE=None, TYPE=None, PERMISSIONS=None, TEMPLATE=None, **kwargs_):
        super(MARKETPLACEAPPSub, self).__init__(ID, UID, GID, UNAME, GNAME, LOCK, REGTIME, NAME, ZONE_ID, ORIGIN_ID, SOURCE, MD5, SIZE, DESCRIPTION, VERSION, FORMAT, APPTEMPLATE64, MARKETPLACE_ID, MARKETPLACE, STATE, TYPE, PERMISSIONS, TEMPLATE,  **kwargs_)
supermod.MARKETPLACEAPP.subclass = MARKETPLACEAPPSub
# end class MARKETPLACEAPPSub


class MARKETPLACE_POOLSub(TemplatedType, supermod.MARKETPLACE_POOL):
    def __init__(self, MARKETPLACE=None, **kwargs_):
        super(MARKETPLACE_POOLSub, self).__init__(MARKETPLACE,  **kwargs_)
supermod.MARKETPLACE_POOL.subclass = MARKETPLACE_POOLSub
# end class MARKETPLACE_POOLSub


class MARKETPLACESub(TemplatedType, supermod.MARKETPLACE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, MARKET_MAD=None, ZONE_ID=None, TOTAL_MB=None, FREE_MB=None, USED_MB=None, MARKETPLACEAPPS=None, PERMISSIONS=None, TEMPLATE=None, **kwargs_):
        super(MARKETPLACESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, MARKET_MAD, ZONE_ID, TOTAL_MB, FREE_MB, USED_MB, MARKETPLACEAPPS, PERMISSIONS, TEMPLATE,  **kwargs_)
supermod.MARKETPLACE.subclass = MARKETPLACESub
# end class MARKETPLACESub


class USER_POOLSub(TemplatedType, supermod.USER_POOL):
    def __init__(self, USER=None, QUOTAS=None, DEFAULT_USER_QUOTAS=None, **kwargs_):
        super(USER_POOLSub, self).__init__(USER, QUOTAS, DEFAULT_USER_QUOTAS,  **kwargs_)
supermod.USER_POOL.subclass = USER_POOLSub
# end class USER_POOLSub


class USERSub(TemplatedType, supermod.USER):
    def __init__(self, ID=None, GID=None, GROUPS=None, GNAME=None, NAME=None, PASSWORD=None, AUTH_DRIVER=None, ENABLED=None, LOGIN_TOKEN=None, TEMPLATE=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, DEFAULT_USER_QUOTAS=None, **kwargs_):
        super(USERSub, self).__init__(ID, GID, GROUPS, GNAME, NAME, PASSWORD, AUTH_DRIVER, ENABLED, LOGIN_TOKEN, TEMPLATE, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, DEFAULT_USER_QUOTAS,  **kwargs_)
supermod.USER.subclass = USERSub
# end class USERSub


class VDC_POOLSub(TemplatedType, supermod.VDC_POOL):
    def __init__(self, VDC=None, **kwargs_):
        super(VDC_POOLSub, self).__init__(VDC,  **kwargs_)
supermod.VDC_POOL.subclass = VDC_POOLSub
# end class VDC_POOLSub


class VDCSub(TemplatedType, supermod.VDC):
    def __init__(self, ID=None, NAME=None, GROUPS=None, CLUSTERS=None, HOSTS=None, DATASTORES=None, VNETS=None, TEMPLATE=None, **kwargs_):
        super(VDCSub, self).__init__(ID, NAME, GROUPS, CLUSTERS, HOSTS, DATASTORES, VNETS, TEMPLATE,  **kwargs_)
supermod.VDC.subclass = VDCSub
# end class VDCSub


class VM_GROUP_POOLSub(TemplatedType, supermod.VM_GROUP_POOL):
    def __init__(self, VM_GROUP=None, **kwargs_):
        super(VM_GROUP_POOLSub, self).__init__(VM_GROUP,  **kwargs_)
supermod.VM_GROUP_POOL.subclass = VM_GROUP_POOLSub
# end class VM_GROUP_POOLSub


class VM_GROUPSub(TemplatedType, supermod.VM_GROUP):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LOCK=None, ROLES=None, TEMPLATE=None, **kwargs_):
        super(VM_GROUPSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LOCK, ROLES, TEMPLATE,  **kwargs_)
supermod.VM_GROUP.subclass = VM_GROUPSub
# end class VM_GROUPSub


class VM_POOLSub(TemplatedType, supermod.VM_POOL):
    def __init__(self, VM=None, **kwargs_):
        super(VM_POOLSub, self).__init__(VM,  **kwargs_)
supermod.VM_POOL.subclass = VM_POOLSub
# end class VM_POOLSub


class VMTEMPLATE_POOLSub(TemplatedType, supermod.VMTEMPLATE_POOL):
    def __init__(self, VMTEMPLATE=None, **kwargs_):
        super(VMTEMPLATE_POOLSub, self).__init__(VMTEMPLATE,  **kwargs_)
supermod.VMTEMPLATE_POOL.subclass = VMTEMPLATE_POOLSub
# end class VMTEMPLATE_POOLSub


class VMTEMPLATESub(TemplatedType, supermod.VMTEMPLATE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LOCK=None, PERMISSIONS=None, REGTIME=None, TEMPLATE=None, **kwargs_):
        super(VMTEMPLATESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LOCK, PERMISSIONS, REGTIME, TEMPLATE,  **kwargs_)
supermod.VMTEMPLATE.subclass = VMTEMPLATESub
# end class VMTEMPLATESub


class VMSub(TemplatedType, supermod.VM):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LAST_POLL=None, STATE=None, LCM_STATE=None, PREV_STATE=None, PREV_LCM_STATE=None, RESCHED=None, STIME=None, ETIME=None, DEPLOY_ID=None, LOCK=None, MONITORING=None, TEMPLATE=None, USER_TEMPLATE=None, HISTORY_RECORDS=None, SNAPSHOTS=None, **kwargs_):
        super(VMSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LAST_POLL, STATE, LCM_STATE, PREV_STATE, PREV_LCM_STATE, RESCHED, STIME, ETIME, DEPLOY_ID, LOCK, MONITORING, TEMPLATE, USER_TEMPLATE, HISTORY_RECORDS, SNAPSHOTS,  **kwargs_)
supermod.VM.subclass = VMSub
# end class VMSub


class VNET_POOLSub(TemplatedType, supermod.VNET_POOL):
    def __init__(self, VNET=None, **kwargs_):
        super(VNET_POOLSub, self).__init__(VNET,  **kwargs_)
supermod.VNET_POOL.subclass = VNET_POOLSub
# end class VNET_POOLSub


class VNETSub(TemplatedType, supermod.VNET):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LOCK=None, PERMISSIONS=None, CLUSTERS=None, BRIDGE=None, BRIDGE_TYPE=None, PARENT_NETWORK_ID=None, VN_MAD=None, PHYDEV=None, VLAN_ID=None, OUTER_VLAN_ID=None, VLAN_ID_AUTOMATIC=None, OUTER_VLAN_ID_AUTOMATIC=None, USED_LEASES=None, VROUTERS=None, TEMPLATE=None, AR_POOL=None, **kwargs_):
        super(VNETSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LOCK, PERMISSIONS, CLUSTERS, BRIDGE, BRIDGE_TYPE, PARENT_NETWORK_ID, VN_MAD, PHYDEV, VLAN_ID, OUTER_VLAN_ID, VLAN_ID_AUTOMATIC, OUTER_VLAN_ID_AUTOMATIC, USED_LEASES, VROUTERS, TEMPLATE, AR_POOL,  **kwargs_)
supermod.VNET.subclass = VNETSub
# end class VNETSub


class VNTEMPLATE_POOLSub(TemplatedType, supermod.VNTEMPLATE_POOL):
    def __init__(self, VNTEMPLATE=None, **kwargs_):
        super(VNTEMPLATE_POOLSub, self).__init__(VNTEMPLATE,  **kwargs_)
supermod.VNTEMPLATE_POOL.subclass = VNTEMPLATE_POOLSub
# end class VNTEMPLATE_POOLSub


class VNTEMPLATESub(TemplatedType, supermod.VNTEMPLATE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LOCK=None, PERMISSIONS=None, REGTIME=None, TEMPLATE=None, **kwargs_):
        super(VNTEMPLATESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LOCK, PERMISSIONS, REGTIME, TEMPLATE,  **kwargs_)
supermod.VNTEMPLATE.subclass = VNTEMPLATESub
# end class VNTEMPLATESub


class VROUTER_POOLSub(TemplatedType, supermod.VROUTER_POOL):
    def __init__(self, VROUTER=None, **kwargs_):
        super(VROUTER_POOLSub, self).__init__(VROUTER,  **kwargs_)
supermod.VROUTER_POOL.subclass = VROUTER_POOLSub
# end class VROUTER_POOLSub


class VROUTERSub(TemplatedType, supermod.VROUTER):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LOCK=None, VMS=None, TEMPLATE=None, **kwargs_):
        super(VROUTERSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LOCK, VMS, TEMPLATE,  **kwargs_)
supermod.VROUTER.subclass = VROUTERSub
# end class VROUTERSub


class ZONE_POOLSub(TemplatedType, supermod.ZONE_POOL):
    def __init__(self, ZONE=None, **kwargs_):
        super(ZONE_POOLSub, self).__init__(ZONE,  **kwargs_)
supermod.ZONE_POOL.subclass = ZONE_POOLSub
# end class ZONE_POOLSub


class ZONESub(TemplatedType, supermod.ZONE):
    def __init__(self, ID=None, NAME=None, TEMPLATE=None, SERVER_POOL=None, **kwargs_):
        super(ZONESub, self).__init__(ID, NAME, TEMPLATE, SERVER_POOL,  **kwargs_)
supermod.ZONE.subclass = ZONESub
# end class ZONESub


class VMTypeSub(TemplatedType, supermod.VMType):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LAST_POLL=None, STATE=None, LCM_STATE=None, PREV_STATE=None, PREV_LCM_STATE=None, RESCHED=None, STIME=None, ETIME=None, DEPLOY_ID=None, MONITORING=None, TEMPLATE=None, USER_TEMPLATE=None, HISTORY_RECORDS=None, SNAPSHOTS=None, **kwargs_):
        super(VMTypeSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LAST_POLL, STATE, LCM_STATE, PREV_STATE, PREV_LCM_STATE, RESCHED, STIME, ETIME, DEPLOY_ID, MONITORING, TEMPLATE, USER_TEMPLATE, HISTORY_RECORDS, SNAPSHOTS,  **kwargs_)
supermod.VMType.subclass = VMTypeSub
# end class VMTypeSub


class PERMISSIONSTypeSub(TemplatedType, supermod.PERMISSIONSType):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSTypeSub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType.subclass = PERMISSIONSTypeSub
# end class PERMISSIONSTypeSub


class SNAPSHOTSTypeSub(TemplatedType, supermod.SNAPSHOTSType):
    def __init__(self, ALLOW_ORPHANS=None, CURRENT_BASE=None, DISK_ID=None, NEXT_SNAPSHOT=None, SNAPSHOT=None, **kwargs_):
        super(SNAPSHOTSTypeSub, self).__init__(ALLOW_ORPHANS, CURRENT_BASE, DISK_ID, NEXT_SNAPSHOT, SNAPSHOT,  **kwargs_)
supermod.SNAPSHOTSType.subclass = SNAPSHOTSTypeSub
# end class SNAPSHOTSTypeSub


class SNAPSHOTTypeSub(TemplatedType, supermod.SNAPSHOTType):
    def __init__(self, ACTIVE=None, CHILDREN=None, DATE=None, ID=None, NAME=None, PARENT=None, SIZE=None, **kwargs_):
        super(SNAPSHOTTypeSub, self).__init__(ACTIVE, CHILDREN, DATE, ID, NAME, PARENT, SIZE,  **kwargs_)
supermod.SNAPSHOTType.subclass = SNAPSHOTTypeSub
# end class SNAPSHOTTypeSub


class HOSTSTypeSub(TemplatedType, supermod.HOSTSType):
    def __init__(self, ID=None, **kwargs_):
        super(HOSTSTypeSub, self).__init__(ID,  **kwargs_)
supermod.HOSTSType.subclass = HOSTSTypeSub
# end class HOSTSTypeSub


class DATASTORESTypeSub(TemplatedType, supermod.DATASTORESType):
    def __init__(self, ID=None, **kwargs_):
        super(DATASTORESTypeSub, self).__init__(ID,  **kwargs_)
supermod.DATASTORESType.subclass = DATASTORESTypeSub
# end class DATASTORESTypeSub


class VNETSTypeSub(TemplatedType, supermod.VNETSType):
    def __init__(self, ID=None, **kwargs_):
        super(VNETSTypeSub, self).__init__(ID,  **kwargs_)
supermod.VNETSType.subclass = VNETSTypeSub
# end class VNETSTypeSub


class PERMISSIONSType1Sub(TemplatedType, supermod.PERMISSIONSType1):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType1Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType1.subclass = PERMISSIONSType1Sub
# end class PERMISSIONSType1Sub


class CLUSTERSTypeSub(TemplatedType, supermod.CLUSTERSType):
    def __init__(self, ID=None, **kwargs_):
        super(CLUSTERSTypeSub, self).__init__(ID,  **kwargs_)
supermod.CLUSTERSType.subclass = CLUSTERSTypeSub
# end class CLUSTERSTypeSub


class IMAGESTypeSub(TemplatedType, supermod.IMAGESType):
    def __init__(self, ID=None, **kwargs_):
        super(IMAGESTypeSub, self).__init__(ID,  **kwargs_)
supermod.IMAGESType.subclass = IMAGESTypeSub
# end class IMAGESTypeSub


class TEMPLATETypeSub(TemplatedType, supermod.TEMPLATEType):
    def __init__(self, VCENTER_DC_NAME=None, VCENTER_DC_REF=None, VCENTER_DS_NAME=None, VCENTER_DS_REF=None, VCENTER_HOST=None, VCENTER_INSTANCE_ID=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATETypeSub, self).__init__(VCENTER_DC_NAME, VCENTER_DC_REF, VCENTER_DS_NAME, VCENTER_DS_REF, VCENTER_HOST, VCENTER_INSTANCE_ID, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType.subclass = TEMPLATETypeSub
# end class TEMPLATETypeSub


class GROUPTypeSub(TemplatedType, supermod.GROUPType):
    def __init__(self, ID=None, NAME=None, TEMPLATE=None, USERS=None, ADMINS=None, **kwargs_):
        super(GROUPTypeSub, self).__init__(ID, NAME, TEMPLATE, USERS, ADMINS,  **kwargs_)
supermod.GROUPType.subclass = GROUPTypeSub
# end class GROUPTypeSub


class USERSTypeSub(TemplatedType, supermod.USERSType):
    def __init__(self, ID=None, **kwargs_):
        super(USERSTypeSub, self).__init__(ID,  **kwargs_)
supermod.USERSType.subclass = USERSTypeSub
# end class USERSTypeSub


class ADMINSTypeSub(TemplatedType, supermod.ADMINSType):
    def __init__(self, ID=None, **kwargs_):
        super(ADMINSTypeSub, self).__init__(ID,  **kwargs_)
supermod.ADMINSType.subclass = ADMINSTypeSub
# end class ADMINSTypeSub


class QUOTASTypeSub(TemplatedType, supermod.QUOTASType):
    def __init__(self, ID=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(QUOTASTypeSub, self).__init__(ID, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.QUOTASType.subclass = QUOTASTypeSub
# end class QUOTASTypeSub


class DATASTORE_QUOTATypeSub(TemplatedType, supermod.DATASTORE_QUOTAType):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTATypeSub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType.subclass = DATASTORE_QUOTATypeSub
# end class DATASTORE_QUOTATypeSub


class DATASTORETypeSub(TemplatedType, supermod.DATASTOREType):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTORETypeSub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType.subclass = DATASTORETypeSub
# end class DATASTORETypeSub


class NETWORK_QUOTATypeSub(TemplatedType, supermod.NETWORK_QUOTAType):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTATypeSub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType.subclass = NETWORK_QUOTATypeSub
# end class NETWORK_QUOTATypeSub


class NETWORKTypeSub(TemplatedType, supermod.NETWORKType):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKTypeSub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType.subclass = NETWORKTypeSub
# end class NETWORKTypeSub


class VM_QUOTATypeSub(TemplatedType, supermod.VM_QUOTAType):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTATypeSub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType.subclass = VM_QUOTATypeSub
# end class VM_QUOTATypeSub


class VMType2Sub(TemplatedType, supermod.VMType2):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType2Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType2.subclass = VMType2Sub
# end class VMType2Sub


class IMAGE_QUOTATypeSub(TemplatedType, supermod.IMAGE_QUOTAType):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTATypeSub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType.subclass = IMAGE_QUOTATypeSub
# end class IMAGE_QUOTATypeSub


class IMAGETypeSub(TemplatedType, supermod.IMAGEType):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGETypeSub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType.subclass = IMAGETypeSub
# end class IMAGETypeSub


class DEFAULT_GROUP_QUOTASTypeSub(TemplatedType, supermod.DEFAULT_GROUP_QUOTASType):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(DEFAULT_GROUP_QUOTASTypeSub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.DEFAULT_GROUP_QUOTASType.subclass = DEFAULT_GROUP_QUOTASTypeSub
# end class DEFAULT_GROUP_QUOTASTypeSub


class DATASTORE_QUOTAType3Sub(TemplatedType, supermod.DATASTORE_QUOTAType3):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType3Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType3.subclass = DATASTORE_QUOTAType3Sub
# end class DATASTORE_QUOTAType3Sub


class DATASTOREType4Sub(TemplatedType, supermod.DATASTOREType4):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType4Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType4.subclass = DATASTOREType4Sub
# end class DATASTOREType4Sub


class NETWORK_QUOTAType5Sub(TemplatedType, supermod.NETWORK_QUOTAType5):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType5Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType5.subclass = NETWORK_QUOTAType5Sub
# end class NETWORK_QUOTAType5Sub


class NETWORKType6Sub(TemplatedType, supermod.NETWORKType6):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType6Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType6.subclass = NETWORKType6Sub
# end class NETWORKType6Sub


class VM_QUOTAType7Sub(TemplatedType, supermod.VM_QUOTAType7):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType7Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType7.subclass = VM_QUOTAType7Sub
# end class VM_QUOTAType7Sub


class VMType8Sub(TemplatedType, supermod.VMType8):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType8Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType8.subclass = VMType8Sub
# end class VMType8Sub


class IMAGE_QUOTAType9Sub(TemplatedType, supermod.IMAGE_QUOTAType9):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType9Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType9.subclass = IMAGE_QUOTAType9Sub
# end class IMAGE_QUOTAType9Sub


class IMAGEType10Sub(TemplatedType, supermod.IMAGEType10):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType10Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType10.subclass = IMAGEType10Sub
# end class IMAGEType10Sub


class USERSType11Sub(TemplatedType, supermod.USERSType11):
    def __init__(self, ID=None, **kwargs_):
        super(USERSType11Sub, self).__init__(ID,  **kwargs_)
supermod.USERSType11.subclass = USERSType11Sub
# end class USERSType11Sub


class ADMINSType12Sub(TemplatedType, supermod.ADMINSType12):
    def __init__(self, ID=None, **kwargs_):
        super(ADMINSType12Sub, self).__init__(ID,  **kwargs_)
supermod.ADMINSType12.subclass = ADMINSType12Sub
# end class ADMINSType12Sub


class DATASTORE_QUOTAType13Sub(TemplatedType, supermod.DATASTORE_QUOTAType13):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType13Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType13.subclass = DATASTORE_QUOTAType13Sub
# end class DATASTORE_QUOTAType13Sub


class DATASTOREType14Sub(TemplatedType, supermod.DATASTOREType14):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType14Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType14.subclass = DATASTOREType14Sub
# end class DATASTOREType14Sub


class NETWORK_QUOTAType15Sub(TemplatedType, supermod.NETWORK_QUOTAType15):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType15Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType15.subclass = NETWORK_QUOTAType15Sub
# end class NETWORK_QUOTAType15Sub


class NETWORKType16Sub(TemplatedType, supermod.NETWORKType16):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType16Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType16.subclass = NETWORKType16Sub
# end class NETWORKType16Sub


class VM_QUOTAType17Sub(TemplatedType, supermod.VM_QUOTAType17):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType17Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType17.subclass = VM_QUOTAType17Sub
# end class VM_QUOTAType17Sub


class VMType18Sub(TemplatedType, supermod.VMType18):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType18Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType18.subclass = VMType18Sub
# end class VMType18Sub


class IMAGE_QUOTAType19Sub(TemplatedType, supermod.IMAGE_QUOTAType19):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType19Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType19.subclass = IMAGE_QUOTAType19Sub
# end class IMAGE_QUOTAType19Sub


class IMAGEType20Sub(TemplatedType, supermod.IMAGEType20):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType20Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType20.subclass = IMAGEType20Sub
# end class IMAGEType20Sub


class DEFAULT_GROUP_QUOTASType21Sub(TemplatedType, supermod.DEFAULT_GROUP_QUOTASType21):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(DEFAULT_GROUP_QUOTASType21Sub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.DEFAULT_GROUP_QUOTASType21.subclass = DEFAULT_GROUP_QUOTASType21Sub
# end class DEFAULT_GROUP_QUOTASType21Sub


class DATASTORE_QUOTAType22Sub(TemplatedType, supermod.DATASTORE_QUOTAType22):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType22Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType22.subclass = DATASTORE_QUOTAType22Sub
# end class DATASTORE_QUOTAType22Sub


class DATASTOREType23Sub(TemplatedType, supermod.DATASTOREType23):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType23Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType23.subclass = DATASTOREType23Sub
# end class DATASTOREType23Sub


class NETWORK_QUOTAType24Sub(TemplatedType, supermod.NETWORK_QUOTAType24):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType24Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType24.subclass = NETWORK_QUOTAType24Sub
# end class NETWORK_QUOTAType24Sub


class NETWORKType25Sub(TemplatedType, supermod.NETWORKType25):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType25Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType25.subclass = NETWORKType25Sub
# end class NETWORKType25Sub


class VM_QUOTAType26Sub(TemplatedType, supermod.VM_QUOTAType26):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType26Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType26.subclass = VM_QUOTAType26Sub
# end class VM_QUOTAType26Sub


class VMType27Sub(TemplatedType, supermod.VMType27):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType27Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType27.subclass = VMType27Sub
# end class VMType27Sub


class IMAGE_QUOTAType28Sub(TemplatedType, supermod.IMAGE_QUOTAType28):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType28Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType28.subclass = IMAGE_QUOTAType28Sub
# end class IMAGE_QUOTAType28Sub


class IMAGEType29Sub(TemplatedType, supermod.IMAGEType29):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType29Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType29.subclass = IMAGEType29Sub
# end class IMAGEType29Sub


class HOST_SHARETypeSub(TemplatedType, supermod.HOST_SHAREType):
    def __init__(self, DISK_USAGE=None, MEM_USAGE=None, CPU_USAGE=None, TOTAL_MEM=None, TOTAL_CPU=None, MAX_DISK=None, MAX_MEM=None, MAX_CPU=None, FREE_DISK=None, FREE_MEM=None, FREE_CPU=None, USED_DISK=None, USED_MEM=None, USED_CPU=None, RUNNING_VMS=None, DATASTORES=None, PCI_DEVICES=None, **kwargs_):
        super(HOST_SHARETypeSub, self).__init__(DISK_USAGE, MEM_USAGE, CPU_USAGE, TOTAL_MEM, TOTAL_CPU, MAX_DISK, MAX_MEM, MAX_CPU, FREE_DISK, FREE_MEM, FREE_CPU, USED_DISK, USED_MEM, USED_CPU, RUNNING_VMS, DATASTORES, PCI_DEVICES,  **kwargs_)
supermod.HOST_SHAREType.subclass = HOST_SHARETypeSub
# end class HOST_SHARETypeSub


class DATASTORESType30Sub(TemplatedType, supermod.DATASTORESType30):
    def __init__(self, DS=None, **kwargs_):
        super(DATASTORESType30Sub, self).__init__(DS,  **kwargs_)
supermod.DATASTORESType30.subclass = DATASTORESType30Sub
# end class DATASTORESType30Sub


class DSTypeSub(TemplatedType, supermod.DSType):
    def __init__(self, ID=None, FREE_MB=None, TOTAL_MB=None, USED_MB=None, **kwargs_):
        super(DSTypeSub, self).__init__(ID, FREE_MB, TOTAL_MB, USED_MB,  **kwargs_)
supermod.DSType.subclass = DSTypeSub
# end class DSTypeSub


class PCI_DEVICESTypeSub(TemplatedType, supermod.PCI_DEVICESType):
    def __init__(self, PCI=None, **kwargs_):
        super(PCI_DEVICESTypeSub, self).__init__(PCI,  **kwargs_)
supermod.PCI_DEVICESType.subclass = PCI_DEVICESTypeSub
# end class PCI_DEVICESTypeSub


class VMSTypeSub(TemplatedType, supermod.VMSType):
    def __init__(self, ID=None, **kwargs_):
        super(VMSTypeSub, self).__init__(ID,  **kwargs_)
supermod.VMSType.subclass = VMSTypeSub
# end class VMSTypeSub


class TEMPLATEType31Sub(TemplatedType, supermod.TEMPLATEType31):
    def __init__(self, VCENTER_CCR_REF=None, VCENTER_DS_REF=None, VCENTER_HOST=None, VCENTER_INSTANCE_ID=None, VCENTER_NAME=None, VCENTER_PASSWORD=None, VCENTER_RESOURCE_POOL_INFO=None, VCENTER_USER=None, VCENTER_VERSION=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType31Sub, self).__init__(VCENTER_CCR_REF, VCENTER_DS_REF, VCENTER_HOST, VCENTER_INSTANCE_ID, VCENTER_NAME, VCENTER_PASSWORD, VCENTER_RESOURCE_POOL_INFO, VCENTER_USER, VCENTER_VERSION, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType31.subclass = TEMPLATEType31Sub
# end class TEMPLATEType31Sub


class LOCKTypeSub(TemplatedType, supermod.LOCKType):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKTypeSub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType.subclass = LOCKTypeSub
# end class LOCKTypeSub


class PERMISSIONSType32Sub(TemplatedType, supermod.PERMISSIONSType32):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType32Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType32.subclass = PERMISSIONSType32Sub
# end class PERMISSIONSType32Sub


class VMSType33Sub(TemplatedType, supermod.VMSType33):
    def __init__(self, ID=None, **kwargs_):
        super(VMSType33Sub, self).__init__(ID,  **kwargs_)
supermod.VMSType33.subclass = VMSType33Sub
# end class VMSType33Sub


class CLONESTypeSub(TemplatedType, supermod.CLONESType):
    def __init__(self, ID=None, **kwargs_):
        super(CLONESTypeSub, self).__init__(ID,  **kwargs_)
supermod.CLONESType.subclass = CLONESTypeSub
# end class CLONESTypeSub


class APP_CLONESTypeSub(TemplatedType, supermod.APP_CLONESType):
    def __init__(self, ID=None, **kwargs_):
        super(APP_CLONESTypeSub, self).__init__(ID,  **kwargs_)
supermod.APP_CLONESType.subclass = APP_CLONESTypeSub
# end class APP_CLONESTypeSub


class TEMPLATEType34Sub(TemplatedType, supermod.TEMPLATEType34):
    def __init__(self, VCENTER_IMPORTED=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType34Sub, self).__init__(VCENTER_IMPORTED, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType34.subclass = TEMPLATEType34Sub
# end class TEMPLATEType34Sub


class SNAPSHOTSType35Sub(TemplatedType, supermod.SNAPSHOTSType35):
    def __init__(self, ALLOW_ORPHANS=None, CURRENT_BASE=None, NEXT_SNAPSHOT=None, SNAPSHOT=None, **kwargs_):
        super(SNAPSHOTSType35Sub, self).__init__(ALLOW_ORPHANS, CURRENT_BASE, NEXT_SNAPSHOT, SNAPSHOT,  **kwargs_)
supermod.SNAPSHOTSType35.subclass = SNAPSHOTSType35Sub
# end class SNAPSHOTSType35Sub


class SNAPSHOTType36Sub(TemplatedType, supermod.SNAPSHOTType36):
    def __init__(self, CHILDREN=None, ACTIVE=None, DATE=None, ID=None, NAME=None, PARENT=None, SIZE=None, **kwargs_):
        super(SNAPSHOTType36Sub, self).__init__(CHILDREN, ACTIVE, DATE, ID, NAME, PARENT, SIZE,  **kwargs_)
supermod.SNAPSHOTType36.subclass = SNAPSHOTType36Sub
# end class SNAPSHOTType36Sub


class LOCKType37Sub(TemplatedType, supermod.LOCKType37):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType37Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType37.subclass = LOCKType37Sub
# end class LOCKType37Sub


class PERMISSIONSType38Sub(TemplatedType, supermod.PERMISSIONSType38):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType38Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType38.subclass = PERMISSIONSType38Sub
# end class PERMISSIONSType38Sub


class MARKETPLACEAPPSTypeSub(TemplatedType, supermod.MARKETPLACEAPPSType):
    def __init__(self, ID=None, **kwargs_):
        super(MARKETPLACEAPPSTypeSub, self).__init__(ID,  **kwargs_)
supermod.MARKETPLACEAPPSType.subclass = MARKETPLACEAPPSTypeSub
# end class MARKETPLACEAPPSTypeSub


class PERMISSIONSType39Sub(TemplatedType, supermod.PERMISSIONSType39):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType39Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType39.subclass = PERMISSIONSType39Sub
# end class PERMISSIONSType39Sub


class USERTypeSub(TemplatedType, supermod.USERType):
    def __init__(self, ID=None, GID=None, GROUPS=None, GNAME=None, NAME=None, PASSWORD=None, AUTH_DRIVER=None, ENABLED=None, LOGIN_TOKEN=None, TEMPLATE=None, **kwargs_):
        super(USERTypeSub, self).__init__(ID, GID, GROUPS, GNAME, NAME, PASSWORD, AUTH_DRIVER, ENABLED, LOGIN_TOKEN, TEMPLATE,  **kwargs_)
supermod.USERType.subclass = USERTypeSub
# end class USERTypeSub


class GROUPSTypeSub(TemplatedType, supermod.GROUPSType):
    def __init__(self, ID=None, **kwargs_):
        super(GROUPSTypeSub, self).__init__(ID,  **kwargs_)
supermod.GROUPSType.subclass = GROUPSTypeSub
# end class GROUPSTypeSub


class LOGIN_TOKENTypeSub(TemplatedType, supermod.LOGIN_TOKENType):
    def __init__(self, TOKEN=None, EXPIRATION_TIME=None, EGID=None, **kwargs_):
        super(LOGIN_TOKENTypeSub, self).__init__(TOKEN, EXPIRATION_TIME, EGID,  **kwargs_)
supermod.LOGIN_TOKENType.subclass = LOGIN_TOKENTypeSub
# end class LOGIN_TOKENTypeSub


class QUOTASType40Sub(TemplatedType, supermod.QUOTASType40):
    def __init__(self, ID=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(QUOTASType40Sub, self).__init__(ID, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.QUOTASType40.subclass = QUOTASType40Sub
# end class QUOTASType40Sub


class DATASTORE_QUOTAType41Sub(TemplatedType, supermod.DATASTORE_QUOTAType41):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType41Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType41.subclass = DATASTORE_QUOTAType41Sub
# end class DATASTORE_QUOTAType41Sub


class DATASTOREType42Sub(TemplatedType, supermod.DATASTOREType42):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType42Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType42.subclass = DATASTOREType42Sub
# end class DATASTOREType42Sub


class NETWORK_QUOTAType43Sub(TemplatedType, supermod.NETWORK_QUOTAType43):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType43Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType43.subclass = NETWORK_QUOTAType43Sub
# end class NETWORK_QUOTAType43Sub


class NETWORKType44Sub(TemplatedType, supermod.NETWORKType44):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType44Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType44.subclass = NETWORKType44Sub
# end class NETWORKType44Sub


class VM_QUOTAType45Sub(TemplatedType, supermod.VM_QUOTAType45):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType45Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType45.subclass = VM_QUOTAType45Sub
# end class VM_QUOTAType45Sub


class VMType46Sub(TemplatedType, supermod.VMType46):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType46Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType46.subclass = VMType46Sub
# end class VMType46Sub


class IMAGE_QUOTAType47Sub(TemplatedType, supermod.IMAGE_QUOTAType47):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType47Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType47.subclass = IMAGE_QUOTAType47Sub
# end class IMAGE_QUOTAType47Sub


class IMAGEType48Sub(TemplatedType, supermod.IMAGEType48):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType48Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType48.subclass = IMAGEType48Sub
# end class IMAGEType48Sub


class DEFAULT_USER_QUOTASTypeSub(TemplatedType, supermod.DEFAULT_USER_QUOTASType):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(DEFAULT_USER_QUOTASTypeSub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.DEFAULT_USER_QUOTASType.subclass = DEFAULT_USER_QUOTASTypeSub
# end class DEFAULT_USER_QUOTASTypeSub


class DATASTORE_QUOTAType49Sub(TemplatedType, supermod.DATASTORE_QUOTAType49):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType49Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType49.subclass = DATASTORE_QUOTAType49Sub
# end class DATASTORE_QUOTAType49Sub


class DATASTOREType50Sub(TemplatedType, supermod.DATASTOREType50):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType50Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType50.subclass = DATASTOREType50Sub
# end class DATASTOREType50Sub


class NETWORK_QUOTAType51Sub(TemplatedType, supermod.NETWORK_QUOTAType51):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType51Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType51.subclass = NETWORK_QUOTAType51Sub
# end class NETWORK_QUOTAType51Sub


class NETWORKType52Sub(TemplatedType, supermod.NETWORKType52):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType52Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType52.subclass = NETWORKType52Sub
# end class NETWORKType52Sub


class VM_QUOTAType53Sub(TemplatedType, supermod.VM_QUOTAType53):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType53Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType53.subclass = VM_QUOTAType53Sub
# end class VM_QUOTAType53Sub


class VMType54Sub(TemplatedType, supermod.VMType54):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType54Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType54.subclass = VMType54Sub
# end class VMType54Sub


class IMAGE_QUOTAType55Sub(TemplatedType, supermod.IMAGE_QUOTAType55):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType55Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType55.subclass = IMAGE_QUOTAType55Sub
# end class IMAGE_QUOTAType55Sub


class IMAGEType56Sub(TemplatedType, supermod.IMAGEType56):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType56Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType56.subclass = IMAGEType56Sub
# end class IMAGEType56Sub


class GROUPSType57Sub(TemplatedType, supermod.GROUPSType57):
    def __init__(self, ID=None, **kwargs_):
        super(GROUPSType57Sub, self).__init__(ID,  **kwargs_)
supermod.GROUPSType57.subclass = GROUPSType57Sub
# end class GROUPSType57Sub


class LOGIN_TOKENType58Sub(TemplatedType, supermod.LOGIN_TOKENType58):
    def __init__(self, TOKEN=None, EXPIRATION_TIME=None, EGID=None, **kwargs_):
        super(LOGIN_TOKENType58Sub, self).__init__(TOKEN, EXPIRATION_TIME, EGID,  **kwargs_)
supermod.LOGIN_TOKENType58.subclass = LOGIN_TOKENType58Sub
# end class LOGIN_TOKENType58Sub


class DATASTORE_QUOTAType59Sub(TemplatedType, supermod.DATASTORE_QUOTAType59):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType59Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType59.subclass = DATASTORE_QUOTAType59Sub
# end class DATASTORE_QUOTAType59Sub


class DATASTOREType60Sub(TemplatedType, supermod.DATASTOREType60):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType60Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType60.subclass = DATASTOREType60Sub
# end class DATASTOREType60Sub


class NETWORK_QUOTAType61Sub(TemplatedType, supermod.NETWORK_QUOTAType61):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType61Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType61.subclass = NETWORK_QUOTAType61Sub
# end class NETWORK_QUOTAType61Sub


class NETWORKType62Sub(TemplatedType, supermod.NETWORKType62):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType62Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType62.subclass = NETWORKType62Sub
# end class NETWORKType62Sub


class VM_QUOTAType63Sub(TemplatedType, supermod.VM_QUOTAType63):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType63Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType63.subclass = VM_QUOTAType63Sub
# end class VM_QUOTAType63Sub


class VMType64Sub(TemplatedType, supermod.VMType64):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType64Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType64.subclass = VMType64Sub
# end class VMType64Sub


class IMAGE_QUOTAType65Sub(TemplatedType, supermod.IMAGE_QUOTAType65):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType65Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType65.subclass = IMAGE_QUOTAType65Sub
# end class IMAGE_QUOTAType65Sub


class IMAGEType66Sub(TemplatedType, supermod.IMAGEType66):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType66Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType66.subclass = IMAGEType66Sub
# end class IMAGEType66Sub


class DEFAULT_USER_QUOTASType67Sub(TemplatedType, supermod.DEFAULT_USER_QUOTASType67):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(DEFAULT_USER_QUOTASType67Sub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.DEFAULT_USER_QUOTASType67.subclass = DEFAULT_USER_QUOTASType67Sub
# end class DEFAULT_USER_QUOTASType67Sub


class DATASTORE_QUOTAType68Sub(TemplatedType, supermod.DATASTORE_QUOTAType68):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType68Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType68.subclass = DATASTORE_QUOTAType68Sub
# end class DATASTORE_QUOTAType68Sub


class DATASTOREType69Sub(TemplatedType, supermod.DATASTOREType69):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType69Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType69.subclass = DATASTOREType69Sub
# end class DATASTOREType69Sub


class NETWORK_QUOTAType70Sub(TemplatedType, supermod.NETWORK_QUOTAType70):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType70Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType70.subclass = NETWORK_QUOTAType70Sub
# end class NETWORK_QUOTAType70Sub


class NETWORKType71Sub(TemplatedType, supermod.NETWORKType71):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType71Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType71.subclass = NETWORKType71Sub
# end class NETWORKType71Sub


class VM_QUOTAType72Sub(TemplatedType, supermod.VM_QUOTAType72):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType72Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType72.subclass = VM_QUOTAType72Sub
# end class VM_QUOTAType72Sub


class VMType73Sub(TemplatedType, supermod.VMType73):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType73Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType73.subclass = VMType73Sub
# end class VMType73Sub


class IMAGE_QUOTAType74Sub(TemplatedType, supermod.IMAGE_QUOTAType74):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType74Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType74.subclass = IMAGE_QUOTAType74Sub
# end class IMAGE_QUOTAType74Sub


class IMAGEType75Sub(TemplatedType, supermod.IMAGEType75):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType75Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType75.subclass = IMAGEType75Sub
# end class IMAGEType75Sub


class GROUPSType76Sub(TemplatedType, supermod.GROUPSType76):
    def __init__(self, ID=None, **kwargs_):
        super(GROUPSType76Sub, self).__init__(ID,  **kwargs_)
supermod.GROUPSType76.subclass = GROUPSType76Sub
# end class GROUPSType76Sub


class CLUSTERSType77Sub(TemplatedType, supermod.CLUSTERSType77):
    def __init__(self, CLUSTER=None, **kwargs_):
        super(CLUSTERSType77Sub, self).__init__(CLUSTER,  **kwargs_)
supermod.CLUSTERSType77.subclass = CLUSTERSType77Sub
# end class CLUSTERSType77Sub


class CLUSTERTypeSub(TemplatedType, supermod.CLUSTERType):
    def __init__(self, ZONE_ID=None, CLUSTER_ID=None, **kwargs_):
        super(CLUSTERTypeSub, self).__init__(ZONE_ID, CLUSTER_ID,  **kwargs_)
supermod.CLUSTERType.subclass = CLUSTERTypeSub
# end class CLUSTERTypeSub


class HOSTSType78Sub(TemplatedType, supermod.HOSTSType78):
    def __init__(self, HOST=None, **kwargs_):
        super(HOSTSType78Sub, self).__init__(HOST,  **kwargs_)
supermod.HOSTSType78.subclass = HOSTSType78Sub
# end class HOSTSType78Sub


class HOSTTypeSub(TemplatedType, supermod.HOSTType):
    def __init__(self, ZONE_ID=None, HOST_ID=None, **kwargs_):
        super(HOSTTypeSub, self).__init__(ZONE_ID, HOST_ID,  **kwargs_)
supermod.HOSTType.subclass = HOSTTypeSub
# end class HOSTTypeSub


class DATASTORESType79Sub(TemplatedType, supermod.DATASTORESType79):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORESType79Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORESType79.subclass = DATASTORESType79Sub
# end class DATASTORESType79Sub


class DATASTOREType80Sub(TemplatedType, supermod.DATASTOREType80):
    def __init__(self, ZONE_ID=None, DATASTORE_ID=None, **kwargs_):
        super(DATASTOREType80Sub, self).__init__(ZONE_ID, DATASTORE_ID,  **kwargs_)
supermod.DATASTOREType80.subclass = DATASTOREType80Sub
# end class DATASTOREType80Sub


class VNETSType81Sub(TemplatedType, supermod.VNETSType81):
    def __init__(self, VNET=None, **kwargs_):
        super(VNETSType81Sub, self).__init__(VNET,  **kwargs_)
supermod.VNETSType81.subclass = VNETSType81Sub
# end class VNETSType81Sub


class VNETTypeSub(TemplatedType, supermod.VNETType):
    def __init__(self, ZONE_ID=None, VNET_ID=None, **kwargs_):
        super(VNETTypeSub, self).__init__(ZONE_ID, VNET_ID,  **kwargs_)
supermod.VNETType.subclass = VNETTypeSub
# end class VNETTypeSub


class PERMISSIONSType82Sub(TemplatedType, supermod.PERMISSIONSType82):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType82Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType82.subclass = PERMISSIONSType82Sub
# end class PERMISSIONSType82Sub


class LOCKType83Sub(TemplatedType, supermod.LOCKType83):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType83Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType83.subclass = LOCKType83Sub
# end class LOCKType83Sub


class ROLESTypeSub(TemplatedType, supermod.ROLESType):
    def __init__(self, ROLE=None, **kwargs_):
        super(ROLESTypeSub, self).__init__(ROLE,  **kwargs_)
supermod.ROLESType.subclass = ROLESTypeSub
# end class ROLESTypeSub


class ROLETypeSub(TemplatedType, supermod.ROLEType):
    def __init__(self, HOST_AFFINED=None, HOST_ANTI_AFFINED=None, ID=None, NAME=None, POLICY=None, **kwargs_):
        super(ROLETypeSub, self).__init__(HOST_AFFINED, HOST_ANTI_AFFINED, ID, NAME, POLICY,  **kwargs_)
supermod.ROLEType.subclass = ROLETypeSub
# end class ROLETypeSub


class VMType84Sub(TemplatedType, supermod.VMType84):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LAST_POLL=None, STATE=None, LCM_STATE=None, RESCHED=None, STIME=None, ETIME=None, DEPLOY_ID=None, TEMPLATE=None, MONITORING=None, USER_TEMPLATE=None, HISTORY_RECORDS=None, **kwargs_):
        super(VMType84Sub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LAST_POLL, STATE, LCM_STATE, RESCHED, STIME, ETIME, DEPLOY_ID, TEMPLATE, MONITORING, USER_TEMPLATE, HISTORY_RECORDS,  **kwargs_)
supermod.VMType84.subclass = VMType84Sub
# end class VMType84Sub


class TEMPLATEType85Sub(TemplatedType, supermod.TEMPLATEType85):
    def __init__(self, DISK=None, anytypeobjs_=None, NIC=None, **kwargs_):
        super(TEMPLATEType85Sub, self).__init__(DISK, anytypeobjs_, NIC, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType85.subclass = TEMPLATEType85Sub
# end class TEMPLATEType85Sub


class DISKTypeSub(TemplatedType, supermod.DISKType):
    def __init__(self, VCENTER_DS_REF=None, VCENTER_INSTANCE_ID=None, anytypeobjs_=None, **kwargs_):
        super(DISKTypeSub, self).__init__(VCENTER_DS_REF, VCENTER_INSTANCE_ID, anytypeobjs_,  **kwargs_)
supermod.DISKType.subclass = DISKTypeSub
# end class DISKTypeSub


class NICTypeSub(TemplatedType, supermod.NICType):
    def __init__(self, anytypeobjs_=None, VCENTER_INSTANCE_ID=None, VCENTER_NET_REF=None, VCENTER_PORTGROUP_TYPE=None, **kwargs_):
        super(NICTypeSub, self).__init__(anytypeobjs_, VCENTER_INSTANCE_ID, VCENTER_NET_REF, VCENTER_PORTGROUP_TYPE,  **kwargs_)
supermod.NICType.subclass = NICTypeSub
# end class NICTypeSub


class MONITORINGTypeSub(TemplatedType, supermod.MONITORINGType):
    def __init__(self, anytypeobjs_=None, **kwargs_):
        super(MONITORINGTypeSub, self).__init__(anytypeobjs_,  **kwargs_)
supermod.MONITORINGType.subclass = MONITORINGTypeSub
# end class MONITORINGTypeSub


class USER_TEMPLATETypeSub(TemplatedType, supermod.USER_TEMPLATEType):
    def __init__(self, anytypeobjs_=None, **kwargs_):
        super(USER_TEMPLATETypeSub, self).__init__(anytypeobjs_,  **kwargs_)
supermod.USER_TEMPLATEType.subclass = USER_TEMPLATETypeSub
# end class USER_TEMPLATETypeSub


class HISTORY_RECORDSTypeSub(TemplatedType, supermod.HISTORY_RECORDSType):
    def __init__(self, HISTORY=None, **kwargs_):
        super(HISTORY_RECORDSTypeSub, self).__init__(HISTORY,  **kwargs_)
supermod.HISTORY_RECORDSType.subclass = HISTORY_RECORDSTypeSub
# end class HISTORY_RECORDSTypeSub


class HISTORYTypeSub(TemplatedType, supermod.HISTORYType):
    def __init__(self, OID=None, SEQ=None, HOSTNAME=None, HID=None, CID=None, DS_ID=None, ACTION=None, **kwargs_):
        super(HISTORYTypeSub, self).__init__(OID, SEQ, HOSTNAME, HID, CID, DS_ID, ACTION,  **kwargs_)
supermod.HISTORYType.subclass = HISTORYTypeSub
# end class HISTORYTypeSub


class LOCKType86Sub(TemplatedType, supermod.LOCKType86):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType86Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType86.subclass = LOCKType86Sub
# end class LOCKType86Sub


class PERMISSIONSType87Sub(TemplatedType, supermod.PERMISSIONSType87):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType87Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType87.subclass = PERMISSIONSType87Sub
# end class PERMISSIONSType87Sub


class TEMPLATEType88Sub(TemplatedType, supermod.TEMPLATEType88):
    def __init__(self, VCENTER_CCR_REF=None, VCENTER_INSTANCE_ID=None, VCENTER_TEMPLATE_REF=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType88Sub, self).__init__(VCENTER_CCR_REF, VCENTER_INSTANCE_ID, VCENTER_TEMPLATE_REF, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType88.subclass = TEMPLATEType88Sub
# end class TEMPLATEType88Sub


class PERMISSIONSType89Sub(TemplatedType, supermod.PERMISSIONSType89):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType89Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType89.subclass = PERMISSIONSType89Sub
# end class PERMISSIONSType89Sub


class LOCKType90Sub(TemplatedType, supermod.LOCKType90):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType90Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType90.subclass = LOCKType90Sub
# end class LOCKType90Sub


class TEMPLATEType91Sub(TemplatedType, supermod.TEMPLATEType91):
    def __init__(self, DISK=None, anytypeobjs_=None, NIC=None, NIC_ALIAS=None, **kwargs_):
        super(TEMPLATEType91Sub, self).__init__(DISK, anytypeobjs_, NIC, anytypeobjs_, NIC_ALIAS, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType91.subclass = TEMPLATEType91Sub
# end class TEMPLATEType91Sub


class DISKType92Sub(TemplatedType, supermod.DISKType92):
    def __init__(self, VCENTER_DS_REF=None, VCENTER_INSTANCE_ID=None, anytypeobjs_=None, **kwargs_):
        super(DISKType92Sub, self).__init__(VCENTER_DS_REF, VCENTER_INSTANCE_ID, anytypeobjs_,  **kwargs_)
supermod.DISKType92.subclass = DISKType92Sub
# end class DISKType92Sub


class NICType93Sub(TemplatedType, supermod.NICType93):
    def __init__(self, BRIDGE_TYPE=None, anytypeobjs_=None, VCENTER_INSTANCE_ID=None, VCENTER_NET_REF=None, VCENTER_PORTGROUP_TYPE=None, **kwargs_):
        super(NICType93Sub, self).__init__(BRIDGE_TYPE, anytypeobjs_, VCENTER_INSTANCE_ID, VCENTER_NET_REF, VCENTER_PORTGROUP_TYPE,  **kwargs_)
supermod.NICType93.subclass = NICType93Sub
# end class NICType93Sub


class NIC_ALIASTypeSub(TemplatedType, supermod.NIC_ALIASType):
    def __init__(self, ALIAS_ID=None, PARENT=None, PARENT_ID=None, anytypeobjs_=None, VCENTER_INSTANCE_ID=None, VCENTER_NET_REF=None, VCENTER_PORTGROUP_TYPE=None, **kwargs_):
        super(NIC_ALIASTypeSub, self).__init__(ALIAS_ID, PARENT, PARENT_ID, anytypeobjs_, VCENTER_INSTANCE_ID, VCENTER_NET_REF, VCENTER_PORTGROUP_TYPE,  **kwargs_)
supermod.NIC_ALIASType.subclass = NIC_ALIASTypeSub
# end class NIC_ALIASTypeSub


class USER_TEMPLATEType94Sub(TemplatedType, supermod.USER_TEMPLATEType94):
    def __init__(self, VCENTER_CCR_REF=None, VCENTER_DS_REF=None, VCENTER_INSTANCE_ID=None, anytypeobjs_=None, **kwargs_):
        super(USER_TEMPLATEType94Sub, self).__init__(VCENTER_CCR_REF, VCENTER_DS_REF, VCENTER_INSTANCE_ID, anytypeobjs_,  **kwargs_)
supermod.USER_TEMPLATEType94.subclass = USER_TEMPLATEType94Sub
# end class USER_TEMPLATEType94Sub


class HISTORY_RECORDSType95Sub(TemplatedType, supermod.HISTORY_RECORDSType95):
    def __init__(self, HISTORY=None, **kwargs_):
        super(HISTORY_RECORDSType95Sub, self).__init__(HISTORY,  **kwargs_)
supermod.HISTORY_RECORDSType95.subclass = HISTORY_RECORDSType95Sub
# end class HISTORY_RECORDSType95Sub


class HISTORYType96Sub(TemplatedType, supermod.HISTORYType96):
    def __init__(self, OID=None, SEQ=None, HOSTNAME=None, HID=None, CID=None, STIME=None, ETIME=None, VM_MAD=None, TM_MAD=None, DS_ID=None, PSTIME=None, PETIME=None, RSTIME=None, RETIME=None, ESTIME=None, EETIME=None, ACTION=None, UID=None, GID=None, REQUEST_ID=None, **kwargs_):
        super(HISTORYType96Sub, self).__init__(OID, SEQ, HOSTNAME, HID, CID, STIME, ETIME, VM_MAD, TM_MAD, DS_ID, PSTIME, PETIME, RSTIME, RETIME, ESTIME, EETIME, ACTION, UID, GID, REQUEST_ID,  **kwargs_)
supermod.HISTORYType96.subclass = HISTORYType96Sub
# end class HISTORYType96Sub


class SNAPSHOTSType97Sub(TemplatedType, supermod.SNAPSHOTSType97):
    def __init__(self, ALLOW_ORPHANS=None, CURRENT_BASE=None, DISK_ID=None, NEXT_SNAPSHOT=None, SNAPSHOT=None, **kwargs_):
        super(SNAPSHOTSType97Sub, self).__init__(ALLOW_ORPHANS, CURRENT_BASE, DISK_ID, NEXT_SNAPSHOT, SNAPSHOT,  **kwargs_)
supermod.SNAPSHOTSType97.subclass = SNAPSHOTSType97Sub
# end class SNAPSHOTSType97Sub


class SNAPSHOTType98Sub(TemplatedType, supermod.SNAPSHOTType98):
    def __init__(self, ACTIVE=None, CHILDREN=None, DATE=None, ID=None, NAME=None, PARENT=None, SIZE=None, **kwargs_):
        super(SNAPSHOTType98Sub, self).__init__(ACTIVE, CHILDREN, DATE, ID, NAME, PARENT, SIZE,  **kwargs_)
supermod.SNAPSHOTType98.subclass = SNAPSHOTType98Sub
# end class SNAPSHOTType98Sub


class VNETType99Sub(TemplatedType, supermod.VNETType99):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, CLUSTERS=None, BRIDGE=None, BRIDGE_TYPE=None, PARENT_NETWORK_ID=None, VN_MAD=None, PHYDEV=None, VLAN_ID=None, OUTER_VLAN_ID=None, VLAN_ID_AUTOMATIC=None, OUTER_VLAN_ID_AUTOMATIC=None, USED_LEASES=None, VROUTERS=None, TEMPLATE=None, AR_POOL=None, **kwargs_):
        super(VNETType99Sub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, CLUSTERS, BRIDGE, BRIDGE_TYPE, PARENT_NETWORK_ID, VN_MAD, PHYDEV, VLAN_ID, OUTER_VLAN_ID, VLAN_ID_AUTOMATIC, OUTER_VLAN_ID_AUTOMATIC, USED_LEASES, VROUTERS, TEMPLATE, AR_POOL,  **kwargs_)
supermod.VNETType99.subclass = VNETType99Sub
# end class VNETType99Sub


class PERMISSIONSType100Sub(TemplatedType, supermod.PERMISSIONSType100):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType100Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType100.subclass = PERMISSIONSType100Sub
# end class PERMISSIONSType100Sub


class CLUSTERSType101Sub(TemplatedType, supermod.CLUSTERSType101):
    def __init__(self, ID=None, **kwargs_):
        super(CLUSTERSType101Sub, self).__init__(ID,  **kwargs_)
supermod.CLUSTERSType101.subclass = CLUSTERSType101Sub
# end class CLUSTERSType101Sub


class VROUTERSTypeSub(TemplatedType, supermod.VROUTERSType):
    def __init__(self, ID=None, **kwargs_):
        super(VROUTERSTypeSub, self).__init__(ID,  **kwargs_)
supermod.VROUTERSType.subclass = VROUTERSTypeSub
# end class VROUTERSTypeSub


class AR_POOLTypeSub(TemplatedType, supermod.AR_POOLType):
    def __init__(self, AR=None, **kwargs_):
        super(AR_POOLTypeSub, self).__init__(AR,  **kwargs_)
supermod.AR_POOLType.subclass = AR_POOLTypeSub
# end class AR_POOLTypeSub


class ARTypeSub(TemplatedType, supermod.ARType):
    def __init__(self, ALLOCATED=None, AR_ID=None, GLOBAL_PREFIX=None, IP=None, MAC=None, PARENT_NETWORK_AR_ID=None, SIZE=None, TYPE=None, ULA_PREFIX=None, VN_MAD=None, **kwargs_):
        super(ARTypeSub, self).__init__(ALLOCATED, AR_ID, GLOBAL_PREFIX, IP, MAC, PARENT_NETWORK_AR_ID, SIZE, TYPE, ULA_PREFIX, VN_MAD,  **kwargs_)
supermod.ARType.subclass = ARTypeSub
# end class ARTypeSub


class LOCKType102Sub(TemplatedType, supermod.LOCKType102):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType102Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType102.subclass = LOCKType102Sub
# end class LOCKType102Sub


class PERMISSIONSType103Sub(TemplatedType, supermod.PERMISSIONSType103):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType103Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType103.subclass = PERMISSIONSType103Sub
# end class PERMISSIONSType103Sub


class CLUSTERSType104Sub(TemplatedType, supermod.CLUSTERSType104):
    def __init__(self, ID=None, **kwargs_):
        super(CLUSTERSType104Sub, self).__init__(ID,  **kwargs_)
supermod.CLUSTERSType104.subclass = CLUSTERSType104Sub
# end class CLUSTERSType104Sub


class VROUTERSType105Sub(TemplatedType, supermod.VROUTERSType105):
    def __init__(self, ID=None, **kwargs_):
        super(VROUTERSType105Sub, self).__init__(ID,  **kwargs_)
supermod.VROUTERSType105.subclass = VROUTERSType105Sub
# end class VROUTERSType105Sub


class TEMPLATEType106Sub(TemplatedType, supermod.TEMPLATEType106):
    def __init__(self, CONTEXT_FORCE_IPV4=None, DNS=None, GATEWAY=None, GATEWAY6=None, GUEST_MTU=None, NETWORK_ADDRESS=None, NETWORK_MASK=None, SEARCH_DOMAIN=None, VCENTER_FROM_WILD=None, VCENTER_INSTANCE_ID=None, VCENTER_NET_REF=None, VCENTER_PORTGROUP_TYPE=None, VCENTER_TEMPLATE_REF=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType106Sub, self).__init__(CONTEXT_FORCE_IPV4, DNS, GATEWAY, GATEWAY6, GUEST_MTU, NETWORK_ADDRESS, NETWORK_MASK, SEARCH_DOMAIN, VCENTER_FROM_WILD, VCENTER_INSTANCE_ID, VCENTER_NET_REF, VCENTER_PORTGROUP_TYPE, VCENTER_TEMPLATE_REF, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType106.subclass = TEMPLATEType106Sub
# end class TEMPLATEType106Sub


class AR_POOLType107Sub(TemplatedType, supermod.AR_POOLType107):
    def __init__(self, AR=None, **kwargs_):
        super(AR_POOLType107Sub, self).__init__(AR,  **kwargs_)
supermod.AR_POOLType107.subclass = AR_POOLType107Sub
# end class AR_POOLType107Sub


class ARType108Sub(TemplatedType, supermod.ARType108):
    def __init__(self, AR_ID=None, GLOBAL_PREFIX=None, IP=None, MAC=None, PARENT_NETWORK_AR_ID=None, SIZE=None, TYPE=None, ULA_PREFIX=None, VN_MAD=None, MAC_END=None, IP_END=None, IP6_ULA=None, IP6_ULA_END=None, IP6_GLOBAL=None, IP6_GLOBAL_END=None, IP6=None, IP6_END=None, USED_LEASES=None, LEASES=None, **kwargs_):
        super(ARType108Sub, self).__init__(AR_ID, GLOBAL_PREFIX, IP, MAC, PARENT_NETWORK_AR_ID, SIZE, TYPE, ULA_PREFIX, VN_MAD, MAC_END, IP_END, IP6_ULA, IP6_ULA_END, IP6_GLOBAL, IP6_GLOBAL_END, IP6, IP6_END, USED_LEASES, LEASES,  **kwargs_)
supermod.ARType108.subclass = ARType108Sub
# end class ARType108Sub


class LEASESTypeSub(TemplatedType, supermod.LEASESType):
    def __init__(self, LEASE=None, **kwargs_):
        super(LEASESTypeSub, self).__init__(LEASE,  **kwargs_)
supermod.LEASESType.subclass = LEASESTypeSub
# end class LEASESTypeSub


class LEASETypeSub(TemplatedType, supermod.LEASEType):
    def __init__(self, IP=None, IP6=None, IP6_GLOBAL=None, IP6_LINK=None, IP6_ULA=None, MAC=None, VM=None, VNET=None, VROUTER=None, **kwargs_):
        super(LEASETypeSub, self).__init__(IP, IP6, IP6_GLOBAL, IP6_LINK, IP6_ULA, MAC, VM, VNET, VROUTER,  **kwargs_)
supermod.LEASEType.subclass = LEASETypeSub
# end class LEASETypeSub


class LOCKType109Sub(TemplatedType, supermod.LOCKType109):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType109Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType109.subclass = LOCKType109Sub
# end class LOCKType109Sub


class PERMISSIONSType110Sub(TemplatedType, supermod.PERMISSIONSType110):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType110Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType110.subclass = PERMISSIONSType110Sub
# end class PERMISSIONSType110Sub


class TEMPLATEType111Sub(TemplatedType, supermod.TEMPLATEType111):
    def __init__(self, VN_MAD=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType111Sub, self).__init__(VN_MAD, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType111.subclass = TEMPLATEType111Sub
# end class TEMPLATEType111Sub


class PERMISSIONSType112Sub(TemplatedType, supermod.PERMISSIONSType112):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType112Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType112.subclass = PERMISSIONSType112Sub
# end class PERMISSIONSType112Sub


class LOCKType113Sub(TemplatedType, supermod.LOCKType113):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType113Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType113.subclass = LOCKType113Sub
# end class LOCKType113Sub


class VMSType114Sub(TemplatedType, supermod.VMSType114):
    def __init__(self, ID=None, **kwargs_):
        super(VMSType114Sub, self).__init__(ID,  **kwargs_)
supermod.VMSType114.subclass = VMSType114Sub
# end class VMSType114Sub


class ZONETypeSub(TemplatedType, supermod.ZONEType):
    def __init__(self, ID=None, NAME=None, TEMPLATE=None, SERVER_POOL=None, **kwargs_):
        super(ZONETypeSub, self).__init__(ID, NAME, TEMPLATE, SERVER_POOL,  **kwargs_)
supermod.ZONEType.subclass = ZONETypeSub
# end class ZONETypeSub


class TEMPLATEType115Sub(TemplatedType, supermod.TEMPLATEType115):
    def __init__(self, ENDPOINT=None, **kwargs_):
        super(TEMPLATEType115Sub, self).__init__(ENDPOINT,  **kwargs_)
supermod.TEMPLATEType115.subclass = TEMPLATEType115Sub
# end class TEMPLATEType115Sub


class SERVER_POOLTypeSub(TemplatedType, supermod.SERVER_POOLType):
    def __init__(self, SERVER=None, **kwargs_):
        super(SERVER_POOLTypeSub, self).__init__(SERVER,  **kwargs_)
supermod.SERVER_POOLType.subclass = SERVER_POOLTypeSub
# end class SERVER_POOLTypeSub


class SERVERTypeSub(TemplatedType, supermod.SERVERType):
    def __init__(self, ENDPOINT=None, ID=None, NAME=None, **kwargs_):
        super(SERVERTypeSub, self).__init__(ENDPOINT, ID, NAME,  **kwargs_)
supermod.SERVERType.subclass = SERVERTypeSub
# end class SERVERTypeSub


class TEMPLATEType116Sub(TemplatedType, supermod.TEMPLATEType116):
    def __init__(self, ENDPOINT=None, **kwargs_):
        super(TEMPLATEType116Sub, self).__init__(ENDPOINT,  **kwargs_)
supermod.TEMPLATEType116.subclass = TEMPLATEType116Sub
# end class TEMPLATEType116Sub


class SERVER_POOLType117Sub(TemplatedType, supermod.SERVER_POOLType117):
    def __init__(self, SERVER=None, **kwargs_):
        super(SERVER_POOLType117Sub, self).__init__(SERVER,  **kwargs_)
supermod.SERVER_POOLType117.subclass = SERVER_POOLType117Sub
# end class SERVER_POOLType117Sub


class SERVERType118Sub(TemplatedType, supermod.SERVERType118):
    def __init__(self, ENDPOINT=None, ID=None, NAME=None, STATE=None, TERM=None, VOTEDFOR=None, COMMIT=None, LOG_INDEX=None, FEDLOG_INDEX=None, **kwargs_):
        super(SERVERType118Sub, self).__init__(ENDPOINT, ID, NAME, STATE, TERM, VOTEDFOR, COMMIT, LOG_INDEX, FEDLOG_INDEX,  **kwargs_)
supermod.SERVERType118.subclass = SERVERType118Sub
# end class SERVERType118Sub


def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    rootClass = supermod.GDSClassesMapping.get(tag)
    if rootClass is None and hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     if not silence:
##         sys.stdout.write('<?xml version="1.0" ?>\n')
##         rootObj.export(
##             sys.stdout, 0, name_=rootTag,
##             namespacedef_='',
##             pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    mapping = {}
    rootElement = rootObj.to_etree(None, name_=rootTag, mapping_=mapping)
    reverse_mapping = rootObj.gds_reverse_node_mapping(mapping)
##     if not silence:
##         content = etree_.tostring(
##             rootElement, pretty_print=True,
##             xml_declaration=True, encoding="utf-8")
##         sys.stdout.write(content)
##         sys.stdout.write('\n')
    return rootObj, rootElement, mapping, reverse_mapping


def parseString(inString, silence=False):
    if sys.version_info.major == 2:
        from StringIO import StringIO
    else:
        from io import BytesIO as StringIO
    parser = None
    doc = parsexml_(StringIO(inString), parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     if not silence:
##         sys.stdout.write('<?xml version="1.0" ?>\n')
##         rootObj.export(
##             sys.stdout, 0, name_=rootTag,
##             namespacedef_='')
    return rootObj


def parseLiteral(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     if not silence:
##         sys.stdout.write('#from supbind import *\n\n')
##         sys.stdout.write('from . import supbind as model_\n\n')
##         sys.stdout.write('rootObj = model_.rootClass(\n')
##         rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
##         sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()
