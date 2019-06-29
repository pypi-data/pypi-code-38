import os
import sys
import json
from shutil import copy2
import re
from datetime import datetime, date

try:
    from pymongo import MongoClient
except:
    raise Exception("You must install the package pymongo - http://api.mongodb.org/python/current/installation.html")

# Note: must install FMQL fmaf
# from fmaf.fileManInfo import FileManInfo, loadFileManInfoFromCache
# from fmaf.analytics.fileManInfoPartition import reduceLinks, reachableFromFull, VISTA_META_EXCLUDES 

# TODO: replace with reporterUtils

"""
TODO:
- split out the VDM assembly into a separate step (feeds off a download VDM step 1 and refine step 3)
"""

# national vs local -- will move to refineMVDMMeta and may go to FMAF along with the
# reference chasing ie/ CLASS with isNational returns national type or None
# ... will be used to generate a JSON in the MVDM set that gives detailed about ... may
# add to about.json (can be used for browsing meta repo)
        
"""
sameAs (from FMQL) definition

Import gets 'vuid' now and makes a vuid ref value

RESVS(FILENUM,IEN,DEFLABEL,SAMEAS) ;
 I FILENUM="50.7" D RESVS50dot7(IEN,.SAMEAS) Q  ; PHARMACY ORDERABLE
 I FILENUM="50" D RESVS50(IEN,.SAMEAS) Q  ; DRUG
 I FILENUM="71" D RESVS71(IEN,.SAMEAS) Q  ; RAD/NUC PROCEDURE <----- not in meta (yet)
 I FILENUM="790.2" D RESVS790dot2(IEN,.SAMEAS) Q  ; WV PROCEDURE <---- not in meta (yet) 
 I FILENUM="757" D RESVS757(IEN,.SAMEAS) Q  ; Major Concept
 I FILENUM="757.01" D RESVS757dot01(IEN,.SAMEAS) Q  ; EXP
 I FILENUM="9999999.27" D RESVS9999999dot27(IEN,.SAMEAS) Q  ; Prov Nav
 I FILENUM="60" D RESVS60(IEN,.SAMEAS) Q  ; Lab Local
 I FILENUM="64" D RESVS64(IEN,.SAMEAS) Q  ; Lab National WKLD <-------- not in meta (yet) as no RPC in scope
 I FILENUM="200" D RESVS200(IEN,.SAMEAS) Q  ; NPI for Providers
 D RESVSVAFIXED(FILENUM,IEN,DEFLABEL,.SAMEAS) Q:$D(SAMEAS("URI")) <--- 5, 11, 13 (see below) ... fixed IENs so just national
 D RESVSSTANDARD(FILENUM,IEN,DEFLABEL,.SAMEAS) Q:$D(SAMEAS("URI")) <--- 80/81/8932.1 which embed an external code (should replace appropriate fields with sameAs
 D RESVSVUID(FILENUM,IEN,DEFLABEL,.SAMEAS) Q:$D(SAMEAS("URI")) <--- note 8985_1 represents
 a global VUID map. Not in yet as no RPC in scope.
 Q
"""

"""
Variation of National (TODO)

National Records with local IENs (ex/ Package or Build etc)

Could handle with national urls and "stationIEN" as an array.
"""

"""
#
# Note on National Files:
# -----------------------
# - assuming all of Lexicon except concept usage (757.001) is national
#   - note: could reframe concept usage and move station id into entries as fields. Could #     merge usage and record per site.
# - Pharmacy has pseudo locked files like 51, Medication Instruction, that are frozen 
#   AFTER pharmacy turn up but each of 130 could be different?
#   - it also has files like 50 or 51_2 that are local pharmacy files that proxy to 
#     national equivalents if a mapping exists. This presents
#     an opportunity to sameAs or to flip to national ids. TODO: these mapping should be 
#     recognized formally in the MongoDB representation
# - mixed files (801.41): "This file contains a combination of nationally distributed 
#   entries, local auto-generated entries, site and VISN exchanged 
#   entries and local manually created entries. Nationally distributed dialog, element, 
#   and group entries have their name prefixed with VA-." 
#   (not split here but national id should be noted). Could split off in national dialog 
#   file (vs local) and standardize those.
# - 8926 is personal preferences for TIU (ie/ not in parameters). Logical to move it.
# - 8932.1 is Person Class/HPTC ie/ has X12 codes too. Assuming IEN locked but comment 
#   doesn't say so. Will need to check. ie/ ala vuid. Index x12?
# - 8989.51, Parameter Definition, are exported by packages. Assume name is unique even if 
#   IEN isn't => should use name as id?
# - 8989.518 is probably locked but are IENs locked or just entries?
# - 9.4 (Package) not locked by IEN but has standard id ala VUID etc.
# - 9999999.09 (Education Topic), 9999999.14 (Immunization) have a national name or code 
#   notion too 
# - 9999999.27 is a local map to lexicon entries (or a fresh entry if no lexicon)
# - 100.03 Order Reason has description with 'Sites may wish to modify the entries in this file to fit their needs'
#
# For mix of national or national without fixed IEN ... could preserve local entries and 
# separate national entries. Patient data could be
# represented using national ids and mapped back for RPC export using station specific 
# mapping tables ie/ name the type mapped and per station
# and ien.
#

[1] Key Automate from HDI files etc + [2] designate src of national id (HDI | Comment | Manual)

  * use 7115.6 and 4.001 as one source of national files ie/ list of managed (Mark source of designation of National ie/ HDI or Comment or Manual
    * domain interesting too http://localhost:9000/rambler#7115_1 as list areas standardized (OP but not IP pharmacy!)
  * in clones, see if any entries deprecated as no vuid (ie/ exs of non national - just for local data) <------------ KEY TO SEE IF 'REALLY' all NATIONAL or some mix of national/local needed
  * REM: symptoms (120.83) listing checks SCREEN^XTID to check if national entry is current or should be listed. Presumably this is a general thing for national files.
  * Examine other XTID checks like GET/SETVUID, GET/SETSTAT (status), GET/SETMASTR (master) manage VUIDs (national ids) for national concepts. References to these in Package code reflect management with VUIDs.
  
Also see: https://github.com/vistadataproject/DataExtractNSync/issues/25 on normalizing ACTIVE/INACTIVE ...
"""

# NOTE: TMP - TODO move to FMAF along with VISTA_META_EXCLUDES
STATIC_NATIONAL_FILES = [ # released centrally - no need for station no qualifier ... isLocked: True 

    '50.416', '50.6', '50.605', '50.67', '50.68', # Pharmacy meta - NDCs and VUIDed Drugs. All but 50.67 have 'Per VHA Directive {pending directive #}, this file has been "locked down" by Data Standardization (DS).'
    
    '120.82', # from 120.8 like the 50's and locked

    '757', '757.01', '757.011', '757.014', '757.018', '757.02', '757.03', '757.033', '757.04', '757.05', '757.1', '757.11', '757.12', '757.13', '757.14', '757.2', '757.21', '757.3', '757.31', '757.32', '757.33', '757.4', '757.41', '757.5', # 757.001 (Concept Usage) is not national. It's a log of sorts 

    '80', '80.1', '80.4', # Comment in Schema: 'This table file should NOT be edited in anyway by the site.'

    '8932.1', # assuming X12/person class fixed (TODO: will work 

    '9999999.28', # Skin Test has 'Per VHA Directive, this file has been "locked down"'
    
    '4.11', # Agency - doesn't say lock down but surely is
    
    '120.51',
    
    '5', '11', '13', # Note: none in set so far as no RPC grabs state/marital status/... but will be added once include all meta referenced by in scope clinical data files
    
    '1.71', # WORLD TIME ZONES (makes sense to be National
    
    '66.3', # MASTER LABORATORY TEST (66_3) - standardizing lab the new way

    '71.9', # MASTER RADIOLOGY PROCEDURE - standardizing radiology
    
    '8_1', # MAS ELIGILIBILITY CODE (8 is local) ... could use 'negative impact on the performance of the MAS module'
    
    '8989_518' # "Any additions to this file must be coordinated with Toolkit developers so a patch can be issued." ... parameter entities - IEN is file number referenced
];

# From nodeVISTA - these are the 32 locked down files (not all are in VAM but all
# should be in basic meta
# ... note: was forced to make 9999999.14 local as NV differed from 442. Others may
# ... need to be too. Gotta analyze

# NB: see https://github.com/vistadataproject/DataExtractNSync/blob/master/Reporters/Reports/comparisonHDIVUID999442.md ... must remove 120.82 and 9999999_14 from list (will effect Mike - I openned an issue)
HDI_7115_6s = ["100.01", "100.02", "120.51", "120.52", "120.53", "120.82", "120.83", "50.416", "50.6", "50.605", "50.68", "51.23", "51.24", "66.3", "71.99", "8925.6", "8926.1", "8926.2", "8926.3", "8926.4", "8926.5", "8926.6", "920", "920.1", "920.2", "920.3", "920.4", "920.5", "95.3", "9999999.04", "9999999.14", "9999999.28"]

# BIG TODO: mixed 101.24 -- "ORW... START" uses this ... reading what to do for report building. 1000+ are national, lower #'s are local.

"""
Work out Locked Files from description
"""
LOCK_MARK_ONE = "locked down" # by Data Standardization (DS) and ERT etc.
LOCK_MARK_TWO = "should NOT be edited in anyway by the site" # ex/ ICD 80
LOCK_MARK_THREE = "FILE SHOULD NOT BE EDITED DIRECTLY. IT IS A STANDARDIZED NATIONAL FILE" # 64 has this 
LOCK_MARK_FOUR = "entries should remain as distributed" # from 5
LOCK_MARK_FIVE = "MARTIAL STATUS file currently consists of six entries which are distributed by the MAS development team" # only 11
LOCK_MARK_SIX = "This file should not be added to nor should entries in it be altered or deleted by the facility" # 13 
LOCK_MARK_SEVEN = "this file definition should not be modified"

# *** NEW ... example is PERIOD OF SERVICE (21) and MAS Eligibility Code (8_1) and Marital Status (11) ... now covered too particularly by LOCK_MARK_FIVE
# ... should ISOLATE A MAS SET vs other locked down etc ie/ categorize national properly ...
# ... MAS == Medical Administration Service
# Others: "Alteration of existing entries or addition of new ones will undoubtedly have a negative impact on the efficient operation of the MAS module and other modules" 
# "MAS developers may have a negative impact on the performance of the MAS module as well as other modules."
LOCK_MARK_EIGHT = "contains \d+ entries as determined by VACO MAS"

def isolateNationalFilesByDescription(systemStationNo):

    locked = {}
    for info in json.load(open(safeLocn("../Definitions/vdmSummary{}.json".format(systemStationNo)))):
        if "description" not in info:
            continue
        descr = info["description"]
        srch = re.search("({}|{}|{}|{}|{}|{}|{})".format(LOCK_MARK_ONE, LOCK_MARK_TWO, LOCK_MARK_THREE, LOCK_MARK_FOUR, LOCK_MARK_FIVE, LOCK_MARK_SIX, LOCK_MARK_SEVEN), descr)
        if not srch:
            continue
        locked[info["id"]] = srch.group(1)
        
    # Need to manually exclude IMMUNIZATION (9999999.14) as Mike saw NV and Cheyenne differ
    if "9999999.14" in locked:
        del locked["9999999.14"]
        
    return locked
    
"""
Go through Schema and produce a simple file id to file name map along with indication of what files a file references

Per specific system

ie/ cache in form I want

ADD:
- use FileInfo
- use .01 for label/name work
- get singletons
"""
def generateVDMSummary(systemName, systemStationNumber):

    reducedDefns = []
    mpropsByChildId = {}
    schemaLocn = "/data/{}/JSON/".format(systemName)
    for sfl in os.listdir(schemaLocn):
        if not re.match(r'SCHEMA', sfl):
            continue
        schemaJSON = json.load(open(schemaLocn + sfl))
        info = {"id": schemaJSON["number"], "label": schemaJSON["name"]}
        if "parent" in schemaJSON:
            info["parent"] = schemaJSON["parent"]
            if len(schemaJSON["fields"]) == 1:
                info["isSingleton"] = True
        if "description" in schemaJSON:
            info["description"] = schemaJSON["description"]["value"]
        for fieldInfo in schemaJSON["fields"]:
            if fieldInfo["type"] == "9":
                mpropsByChildId[fieldInfo["details"]] = fieldInfo["pred"]
        reducedDefns.append(info)

    reducedDefnsById = dict((info["id"], info) for info in reducedDefns)

    # tops will get one or more child singleton paths (rem: no multiple types
    # in JSON
    for info in reducedDefns:
        if "parent" in info and "isSingleton" in info:
            pinfo = info
            path = []
            while True:
                if "parent" not in pinfo:
                    break
                path.insert(0, mpropsByChildId[pinfo["id"]])
                pinfo = reducedDefnsById[pinfo["parent"]]
            if "singletonPaths" not in pinfo:
                pinfo["singletonPaths"] = []
            pinfo["singletonPaths"].append("/".join(path))
        
    json.dump(reducedDefns, open("../Definitions/vdmSummary{}.json".format(systemStationNumber), "w"))
    
# ############################ Station # ####################

"""
Presumption is one top level institution per VISTA and that gives the VISTA's site number.

Series of sources:
------------------
(see old issue: https://github.com/vistadataproject/VDM/issues/33#issuecomment-227789518)
a. VPR uses FAC^VPRD which usually drives off a file 44 (or file 40.8 through 4) entry to get the institution and from the the station# which it calls facilityId
b. VPR can - if no 44 passed to FAC^VPRD fall back on default setting in time-sensitive 8989 picked out by site^vasite 389.9
c. RPCRUN mimicing broker uses kernel system parameters (XUS;17) for institition
d. another variation called through CHKDIV^XUS1, checks user's division (2;0) multiple which gives 4's of user. User may have to pick on.
e. ehmp guide () says use $$SITE^VASITE which returns site name and station #

National vs Local 4:
--------------------
>  National entries are facilities that have a STATION NUMBER (#99) approved by Information Management Service (045A4). National entries are maintained by the Master File Server located on FORUM. Local entries are facilities that are entered locally. Local entries no not have a STATION NUMBER (#99). (Only offically approved station numbers are allowed in the STATION NUMBER (#99) field.) All national entries will have a STATUS (#11) of NATIONAL
... 99 and 100 hold the station number and official VA name for a facility.
... Note: points to file 4 being one with national entries at different ids with a possibility to split the file into InstitionNational, InstitutionLocal.

From: http://www.hardhats.org/projects/New/InitializeVistA.html (need to redo nodeVISTA)

Setup your Institution

VistA has a very complex structure to deal with the question of: in what hospital are you signed in right now? The answer determines the value of the all important variable DUZ(2) and the API SITE^VASITE().

There are five files that are important in that regard: INSTITUTION (#4), STATION NUMBER (TIME SENSITIVE) (#389.9), KERNEL SYSTEM PARAMETERS (#8989.3), MEDICAL CENTER DIVISION file (#40.8), and MASTER PATIENT INDEX (LOCAL NUMBERS) (984.1). We will add our Hopstial to the INSTITUTION file first, with the station number 999. Then we will make sure that the STATION NUMBER file says 999; and then will will point the KERNEL SYSTEM PARAMETERS and MEDICAL CENTER DIVISION to our new Hospital. In MASTER PATIENT INDEX, we tell it our station number and the range of numbers for our Integration Control Numbers (ICNs), the number used to identify patients across systems.

(Note: no 984.1 in Cheyenne set; 40_8 in Secondary Meta; 389_9 in primary!)

By default, FOIA VistA comes with station number 050, and the institution is called SOFTWARE SERVICE. We can't leave that alone because VistA malfunctions with station numbers are are just 2 digits long (050 becomes 50 in code).

and 

> What's your station number? If you use VISTA or RPMS deployed by VA, IHS, or an external vendor; they will assign you your station number. Otherwise, pick a number from 130 to 199; or 971 to 999. These numbers are not used by the VA in VistA. In this guide, we will use 999.

and

> The INSITUTION file is protected from editing by requiring the variable XUMF to be defined. That tells us that inside of the VA, the file is updated by something called Standard Terminology Services (STS), which works by sending VistA mail messages of what to update, and VistA creates the entry based on that mail message. (ie/ locking and how)

Note more on MFS and now Lab Standardized: http://foia-vista.osehra.org/Patches_By_Application/LR-LABORATORY/LR-5P2_SEQ-383_PAT-468.TXT ...
>  The system will include the addition of new fields to the LABORATORY 
 TEST file (#60) and creation of the MASTER LABORATORY TEST file (#66.3)
 (MLTF).
  
 The local facility Laboratory Information Manager(LIM) will need to 
 associate the local tests/specimen in LABORATORY TEST file (#60)
 to Gold Names in MASTER LABORATORY TEST file (#66.3).
 
and for Radiology ...

> http://foia-vista.osehra.org/Patches_By_Application/RA-RADIOLOGY/RA-5_SEQ-115_PAT-127.TXT

> need to associate the local procedure names in file #71
 to Gold Names in file #71.99.
> will be necessary to develop a national standard of radiology
 procedures and map to their respective Current Procedural Terminology
 (CPT) code and Logical Observation Identifiers Names and Codes (LOINC)
 will be populated under the direction of the VHA Radiology Program
 Office
> will match each active entry in the RAD/NUC MED
 PROCEDURES file (# 71) to an entry in the MASTER RADIOLOGY PROCEDURES file
 (#71.99) (MRPF)
> When a new procedure is entered into the RAD/NUC
 MED PROCEDURES file (# 71) an email is automatically sent to the NEW
 TERMINOLOGY RAPID TURNAROUND (NTRT) team for the creation of a new entry
 in the MRPF.
> VHA Radiology Program Office

... does 50 lead to mails?

> REM: we're moving meta data management OUT OF VISTA and into national, centralized services. This should greatly accelerate the push for centralized identity management in general

... TODO: identify all VA national offices and people responsible for national/standard files in VISTA, files we are moving out to our services.

D ^DINIT ... init fileman with 'test suite' and site number
"""
def stationNumber(): # get for data set

    # Hard code for now
    SYSTEM_STATION_NO = "442" # Cheyenne VAMC
    
    return SYSTEM_STATION_NO
    
# ############################# VDM Subsetting for Meta (Fan out) ##############

"""
Required to subset VDMs BEFORE making MVDMs with national ids etc.

Presume VISTA files in meta/I, K, S (form taken from clone) 
... note: may change this input form

Want:
- primary meta == used by RPCs
- secondary meta == referenced by primary meta
"""

CHEY_DATA = "/data/cheyenne2011/meta/"
CHEY_VAM_META_BASE = "/data/cheyenne2011/metaVDM442"

NV_DATA = "/data/nodeVISTA/Data/"
NV_VAM_META_BASE = "/data/nodeVISTA/metaVDM999"

# ex/ slicePrimary(CHEY_DATA, CHEY_VAM_META_BASE, True)
"""
Note: nodeVISTA missing some

Empty/Missing (expect 550 - CMOP SYSTEM) set([u'409.95', u'69.2', u'51', u'125.1', u'8926', u'811.7', u'801.5']) ... print things and others empty in FOIA.
"""
def slicePrimary(fromDir, toDirBase, useIKS=False):

    pvamFiles = set(json.load(open(metaRPCMeta))["files"])
    print "Primary VAM meta files", len(pvamFiles)

    def fileWanted(flTyp):
        # cover 757 and explicit vam files
        if not (re.match(r'757', flTyp) or flTyp in pvamFiles):
            return False
        return True

    copiedFlTyps = sliceVDMMeta(fileWanted, fromDir, toDirBase + "/primary", useIKS)

    # 550 missing - why?
    print "\tMissing (expect 550 - CMOP SYSTEM)", pvamFiles - copiedFlTyps
    
# ex/ sliceSecondary(CHEY_DATA, CHEY_VAM_META_BASE, True)
def sliceSecondary(systemStationNo, fromDir, toDirBase, useIKS=False):
    """
    Files referenced by Primary files
    
    NOTE: re-run secondaryMetaFiles first
    """
    print "... warning: did you run 'secondaryMetaFiles' first?"
    
    svamFiles = set(re.sub(r'\_', '.', flId) for flId in json.load(open("../Definitions/secondaryMetaFiles{}.json".format(systemStationNo))))
    
    def fileWanted(flTyp):
        if flTyp not in svamFiles:
            return False
        return True
        
    copiedFlTyps = sliceVDMMeta(fileWanted, fromDir, toDirBase + "/secondary", useIKS)
    
    # Missing set([u'9999999.41', u'774', u'82.13', u'194.4', u'445.6', u'441', u'445', u'82.1', u'52.53', u'445.4']) ... Cheyenne missing copy
    print "\tMissing", (svamFiles - copiedFlTyps)

def sliceVDMMeta(fileWantedTest, fromDir, toDir, useIKS=False):

    flTyps = set()
    
    def loopFiles(dir):
        for fl in os.listdir(dir):
            if not re.search(r'\.json$', fl):
                continue
            flTyp = re.sub(r'\_', '.', fl.split("-")[0])
            if not fileWantedTest(flTyp):
                continue
            flTyps.add(flTyp)
            copy2(fromDir + "/" + fl, toDir) 
        
    try:
        os.stat(toDir)
    except:
        os.mkdir(toDir)
        
    if useIKS:
        for iks in ["I", "K", "S", "params"]:
            loopFiles(fromDir + "/" + iks)
    else:
        loopFiles(fromDir)

    print "Copied VDM meta for", len(flTyps)
    
    return flTyps
        
"""
From Schema (VDM) definitions, fan out to pull in all meta files referenced
by meta files used by RPCs (so 2 #'s: core and full)

Bonus: ensure national files only reference national files

Uses FMAF - used by subsetting above

- systemName: cheyenne2011 | nodeVISTA
- systemStationNumber: 442 | 999

Note: depends on a pre-built vdmModel and its labels for ids and this may fail in time
"""
def secondaryMetaFiles(systemName, systemStationNumber):
    
    """
    primaryFiles (used by RPCs). Need files that they use ie/ rely on slice pre-existing
    """
    # Get core meta files
    META_DIR = "/data/{}/metaVDM{}/primary".format(systemName, systemStationNumber) 
    flTyps = set()
    for fl in os.listdir(META_DIR):
        if not re.search(r'\.json$', fl):
            continue
        flTyps.add(fl.split("-")[0])
    coreRPCMetaFiles = list(flTyps)
    print "Covered Meta Files:", coreRPCMetaFiles
    print 

    # Load full schema defns for walk outs
    cacheBase = "/data/"
    sysType = "VISTA"
    print "Loading Schema (FileManInfo) of", systemName, "..."
    baseLocation = cacheBase + systemName
    cacheLocation = baseLocation + "/JSON/" # assuming META in JSON
    print "... cache location {}".format(cacheLocation)
    if not os.path.isdir(cacheLocation):
        raise Exception("Can't find cache location: " + cacheLocation)
    # Third argument, description, not passed in
    fileManInfo = loadFileManInfoFromCache(cacheLocation, systemName, sysType)
    allTopFiles = set([fi.id for fi in fileManInfo if not fi.parent])
    fmLabelById = dict((fi.id, fi.label) for fi in fileManInfo)
    print "... loaded with", fileManInfo.size, "with", len(allTopFiles), "tops"
    print 
    
    print "Building link reduction ..."
    fromsByTo, tosByFrom = reduceLinks(fileManInfo)
    print "... got", len(fromsByTo), "destination points of which", sum(1 for to in fromsByTo if re.match(r'M:', to)), "are multiples"

    print
    print
    print "Passing in", coreRPCMetaFiles
    excludes = VISTA_META_EXCLUDES
    excludes.append("M:550_215") # already in new FMAF - adding for old
    excludes.append("20") # don't want 20 in there either
    expandFiles, excludedPaths = reachableFromFull(tosByFrom, coreRPCMetaFiles, excludes=excludes)
    print

    # possible that some expands are NOT valid ie/ bad refs 
    # ... Usually need to add to VISTA_META_EXCLUDES from FMAF 
    expandFilesBad = set(expandFiles) - allTopFiles
    print "Some Expanded files are bad:", expandFilesBad, "-- removing them"
    print
    expandFiles = sorted([flId for flId in expandFiles if flId in allTopFiles], key=lambda x: float(re.sub(r'\_', '.', x)))

    # For QA: crude list of key patient files. Make sure not in set
    PFILE_SAMPLE = set(["2", "63", "100_21", "100", "9000001", "9000010", "74", "123", "130", "2005", "405", "409_68", "8925", "190", "190_1", "190_3"])
    if len(PFILE_SAMPLE & set(expandFiles)):
        raise Exception("Expand out takes in patient files:", PFILE_SAMPLE & set(expandFiles))
        
    vdmM = VDMModel(systemStationNumber) # could be old as a cache. Need to divorce and import in fmaf
        
    print "# All expand files {} - from {} core files".format(len(expandFiles), len(coreRPCMetaFiles))
    for i, flId in enumerate(expandFiles, 1):
        dflId = re.sub(r'\_', '.', flId)
        label = vdmM.name(dflId) # or could just use FM - label = fmLabelById[flId] -
        # ... but want isNational from vdmM too 
        print "\t{}. {} ({}){}".format(i, label, flId, " - YES" if vdmM.isNational(dflId) else "")
    print
    
    # Gotta change to make station no primary
    json.dump(expandFiles, open("../Definitions/secondaryMetaFiles{}.json".format(systemStationNumber), "w"))
    
"""
Simple Utility that takes a set of top files and returns those files which come from that list. It also returns "bad files" ie/ files not in top so scheme is corrupt.
"""
def expandFromFilesForSystem(systemName, fromFiles, excludes=[], shouldHavePFiles=False):

    # Load full schema defns for walk outs
    cacheBase = "/data/"
    sysType = "VISTA"
    print "Loading Schema (FileManInfo) of", systemName, "..."
    baseLocation = cacheBase + systemName
    cacheLocation = baseLocation + "/JSON/" # assuming META in JSON
    print "... cache location {}".format(cacheLocation)
    if not os.path.isdir(cacheLocation):
        raise Exception("Can't find cache location: " + cacheLocation)
    # Third argument, description, not passed in
    fileManInfo = loadFileManInfoFromCache(cacheLocation, systemName, sysType)
    allTopFiles = set([fi.id for fi in fileManInfo if not fi.parent])
    fmLabelById = dict((fi.id, fi.label) for fi in fileManInfo)
    print "... loaded with", fileManInfo.size, "with", len(allTopFiles), "tops"
    print 
    
    print "Building link reduction ..."
    fromsByTo, tosByFrom = reduceLinks(fileManInfo)
    print "... got", len(fromsByTo), "destination points of which", sum(1 for to in fromsByTo if re.match(r'M:', to)), "are multiples"
    
    expandFiles, excludedPaths = reachableFromFull(tosByFrom, fromFiles, excludes=excludes)
    print

    # possible that some expands are NOT valid ie/ bad refs 
    # ... Usually need to add to VISTA_META_EXCLUDES from FMAF 
    expandFilesBad = set(expandFiles) - allTopFiles
    
    PFILE_SAMPLE = set(["2", "63", "100_21", "100", "9000001", "9000010", "74", "123", "130", "2005", "405", "409_68", "8925", "190", "190_1", "190_3"])
    if not shouldHavePFiles and len(PFILE_SAMPLE & set(expandFiles.keys())):
        badPFiles = PFILE_SAMPLE & set(expandFiles.keys())
    else:
        badPFiles = None
    
    return expandFiles, expandFilesBad, badPFiles

# ############################# Capture Analysis/Comparison ###############

"""
Originally in 'processCapture'

Want to redo http://vistadataproject.info/artifacts/cprsRPCBreakdown/bdStart (as doing scoping)

Surprising missing meta:
- XUS DIVISION GET (http://vistadataproject.info/artifacts/devdocs/VISTARPC/XUS_DIVISION_GET)
- ORWU DT (http://vistadataproject.info/artifacts/devdocs/VISTARPC/ORWU_DT)
  ORWU VALDT too
  and these tests: https://github.com/vistadataproject/nonClinicalRPCs/blob/98544c23e3ae1d7fbeb8c157799fe9b681f7f2e1/prototypes/utility/rpcUtilities-spec.js
- ORWGRPC TYPES ... has a DFN arg (so clinical?) but in P1 and pasted 0, 0

- OR GET COMBAT VET missing (good as clinical) and ORWPT LEGACY etc (patient file stuff I can pull for demo work)

http://vistadataproject.info/artifacts/cprsRPCBreakdown/bdAuthentication etc
"""
CAPTURE_LOCN = "../../metaVDP/definitions/RPC/captures/" # ex "capture-p1bpsel.txt"

def compareCapture(rpcs, captureFiles): # split out a capture file or files

    rpcInfoList = []
    for captureFile in captureFiles:
        rpcInfoList.extend(json.load(open(CAPTURE_LOCN + captureFile)))
    # Exclude
    excludedRPCs = set(["TCPConnect", "XUS SIGNON SETUP", "XUS AV CODE", "XWB CREATE CONTEXT", "ORWRP GET DEFAULT PRINTER"])
    captureRPCs = set(rpcInfo["name"] for rpcInfo in rpcInfoList if rpcInfo["name"] not in excludedRPCs)
    print "{} has {} RPC calls, {} distinct RPCs".format("/".join(captureFiles), len(rpcInfoList), len(captureRPCs))
    
    rpcs = set(rpcs)
    
    print "RPCs in capture", len(rpcs & captureRPCs)
    print "RPCs not in capture", len(rpcs - captureRPCs)
    print "Capture RPCs not in RPCs passed", len(captureRPCs - rpcs)
    print "\t{}".format(captureRPCs - rpcs)
    
    print
    
    return
    
"""
Separate Cheyenne specific ie/ clone specific files (from FOIA/national files)
...
of the 3256, which is specific to Cheyenne?

Six # -- 442\d\d\d[_\d\d] ... all global DIZ?

Need to get stations from file 4 and work from there ie/ have that reduced
so can do analysis.

GO thru and get #'s

Secondary: may lookup in Builds - need to load builds into Mongo
Package 9.4 ... class ... I:NATIONAL, II:Inactive, III:Local
... will be part of meta gathering too.
"""      
        
# ############################# Driver ####################################

def main():

    systemStationNumber = "999"
    vdmM = VDMModel(systemStationNumber)
    print json.dumps(vdmM.nationals())
    return

    slicePrimary(NV_DATA, NV_VAM_META_BASE, False)
    generateVDMSummary("nodeVISTA", "999")
    secondaryMetaFiles("nodeVISTA", "999")
    sliceSecondary("999", NV_DATA, NV_VAM_META_BASE, False)
    return

    mRPCs = MetaCoveredRPC().rpcs()
    compareCapture(mRPCs, ["capture-p1bpsel.txt", "capture-p2psel.txt", "capture-p3allergies.txt"])    
    return

    # VDM slicing
    slicePrimary(NV_DATA, NV_VAM_META_BASE, False)
    generateVDMSummary("nodeVISTA", "999")
    secondaryMetaFiles("nodeVISTA", "999")
    sliceSecondary("999", NV_DATA, NV_VAM_META_BASE, False)
    return

    vdmM = VDMModel(systemStationNumber)
    print vdmM.isNational("757.02")
    return
        
if __name__ == "__main__":
    main()
