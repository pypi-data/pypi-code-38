##
# File:    UniProtReader.py
# Date:    15-Mar-2019
#          JDW - Adapted from earlier SBKB code -
##

import copy
import logging
import string
from xml.dom import minidom

logger = logging.getLogger(__name__)


class UniProtReader(object):
    """Read Uniprot entry xml file and put the following information into  dictionary:

           dict['db_code']           - code
           dict['db_accession']      - primary accession code
           dict['accessions']        - all accessions
           dict['sequence']          - sequence
           dict['keywords']           - keywords
           dict['names']              - protein names
           dict['gene']               - gene namesd
           dict['source_scientific'] - source scientific name
           dict['source_common']     - source common name
           dict['taxonomy_id']       - source taxonomy ID
           dict['comments']          - Uniprot comments
           dict['dbReferences']      - various related annotations

        If there is a registered variant, <isoform> tags are parsed:

           <isoform>
             <id>P42284-2</id>
             <name>V</name>
             <name>Ohsako-G</name>
             <sequence type="displayed"/>
           </isoform>
           <isoform>
             <id>P42284-3</id>
             <name>H</name>
             <name>Ohsako-M</name>
             <sequence type="described" ref="VSP_015404 VSP_015406"/>
           </isoform>

       and <feature type="splice variant"> tags:

           <feature type="splice variant" id="VSP_015404" description="(in isoform H)">
             <original>DVSTNQTVVLPHYSIYHYYSNIYYLLSHTTIYEADRTVSVSCPGKLNCLPQRNDLQETKSVTVL</original>
             <variation>DEAGQNEGGESRIRVRNWLMLADKSIIGKSSDEPSVLHIVLLLSTHRHIISFLLIIQSFIDKIY</variation>
             <location>
               <begin position="455"/>
               <end position="518"/>
             </location>
           </feature>
           <feature type="splice variant" id="VSP_015406" description="(in isoform H)">
             <location>
               <begin position="519"/>
               <end position="549"/>
             </location>
           </feature>

       to find the isoform sequence. If no match found, the default sequence from <sequence> tag
       will be used.
    """

    def __init__(self):
        self.__variantD = {}
        self.__accessionD = {}

    def readFile(self, fileName):
        eDict = {}
        try:
            doc = minidom.parse(fileName)
            self.__updateAccessionDict()
            eDict = self.__parse(doc)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return eDict

    def readString(self, data):
        eDict = {}
        try:
            logger.debug("Using variants %r", self.__variantD)
            doc = minidom.parseString(data)
            self.__updateAccessionDict()
            logger.debug("Using accessionD %r", self.__accessionD)
            eDict = self.__parse(doc)
            logger.debug("eDict keys %r", list(eDict.keys()))
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return eDict

    def addVariant(self, accessionId, varId):
        """ Register a variant id with the input accession code.
        """
        try:
            self.__variantD[varId] = accessionId
            return True
        except Exception:
            return False

    def __updateAccessionDict(self):
        """ Update the list of registered variants for each accession code.
        """
        self.__accessionD = {}
        for vId, aId in self.__variantD.items():
            self.__accessionD.setdefault(aId, []).append(vId)

    def __getVariantList(self, accessionId):
        try:
            return self.__accessionD[accessionId]
        except Exception:
            return []

    def __parse(self, doc):
        entryDict = {}
        entryList = doc.getElementsByTagName("entry")

        entryDict = {}
        for entry in entryList:

            # JDW 3-June-2014 Return the data set as db_name -- using PDB conventions --
            if entry.nodeType != entry.ELEMENT_NODE:
                continue

            tDict = {}
            tDict["db_name"] = entry.attributes["dataset"].value
            tDict["version"] = entry.attributes["version"].value
            tDict["modification_date"] = entry.attributes["modified"].value
            #
            for node in entry.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue

                if node.tagName == "name":
                    # Get entry code
                    tDict["db_code"] = node.firstChild.data

                elif node.tagName == "accession":
                    # Get entry first accession
                    if "db_accession" in tDict:
                        pass
                    else:
                        tDict["db_accession"] = node.firstChild.data
                    tDict.setdefault("accessions", []).append(node.firstChild.data)
                elif node.tagName == "sequence":
                    # Get sequence
                    # Sequence must have newlines removed
                    tDict["sequence"] = node.firstChild.data.replace("\n", "")

                elif node.tagName == "protein":
                    self.__getProteinNames(node.childNodes, tDict)

                elif node.tagName == "gene":
                    self.__getGeneNames(node.childNodes, tDict)

                elif node.tagName == "organism":
                    self.__getSourceOrganism(node.childNodes, tDict)

                elif node.tagName == "dbReference":
                    self.__getDbReference(node, tDict)

                elif node.tagName == "keyword":
                    # Get keyword from <keyword id="KW-0181">Complete proteome</keyword>
                    #    and concatenate them using comma separator
                    tDict.setdefault("keywords", []).append(node.firstChild.data)
                elif node.tagName == "comment":
                    self.__getComments(node, tDict)

            #
            # This is an improbable situation of entry lacking an accession code.
            #
            if "db_accession" not in tDict:
                continue

            dbAccession = tDict["db_accession"]
            # --------------- ---------------  --------------- ---------------  ---------------
            # Add variants if these have been specified --
            #
            vList = self.__getVariantList(dbAccession)
            if vList and "sequence" in tDict:
                for vId in vList:
                    vDict = copy.deepcopy(tDict)
                    ok, seqUpdated, isoformD = self.__getIsoFormSeq(doc, vId, vDict)
                    if seqUpdated:
                        vDict["isoform_sequence_updated"] = "Y"
                    else:
                        vDict["isoform_sequence_updated"] = "N"
                    if isoformD:
                        vDict["isoform_names"] = isoformD["names"]
                        if "isoform_edits" in isoformD:
                            vDict["isoform_edits"] = isoformD["isoform_edits"]
                    if ok:
                        vDict["db_isoform"] = vId
                        entryDict[vId] = vDict
            # --------------- ---------------  --------------- ---------------  ---------------
            entryDict[tDict["db_accession"]] = tDict

        return entryDict

    def __getDbReference(self, node, tDict):
        """

        :param nodelList:
        :param dict:
        :return:

                <dbReference type="EC" id="1.14.13.25"/>
                <dbReference type="EMBL" id="M90050">
                    <property type="protein sequence ID" value="AAB62391.2"/>
                    <property type="molecule type" value="Genomic_DNA"/>
                </dbReference>
                <dbReference type="EMBL" id="AE017282">
                    <property type="protein sequence ID" value="AAU92722.1"/>
                    <property type="molecule type" value="Genomic_DNA"/>
                </dbReference>
                <dbReference type="PIR" id="JQ0701">
                    <property type="entry name" value="JQ0701"/>
                </dbReference>
                <dbReference type="RefSeq" id="WP_010960487.1">
                    <property type="nucleotide sequence ID" value="NC_002977.6"/>
                <dbReference type="GO" id="GO:0030246">
                    <property type="term" value="F:carbohydrate binding"/>
                    <property type="evidence" value="ECO:0000501"/>
                    <property type="project" value="UniProtKB-KW"/>
                </dbReference>
                <dbReference type="GO" id="GO:0038023">
                    <property type="term" value="F:signaling receptor activity"/>
                    <property type="evidence" value="ECO:0000314"/>
                    <property type="project" value="MGI"/>

        """
        dbType = node.attributes["type"].value
        dbId = node.attributes["id"].value
        tD = {"resource": dbType, "id_code": dbId}
        #
        if dbType in ["EC", "PIR"]:
            tDict.setdefault("dbReferences", []).append(tD)
        elif dbType in ["EMBL", "GO", "RefSeq", "Pfam", "InterPro"]:
            pD = self.__getProperties(node.childNodes)
            tD.update(pD)
            tDict.setdefault("dbReferences", []).append(tD)

    def __getProperties(self, nodeList):
        dD = {}
        try:
            for node in nodeList:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                if node.tagName in ["property"]:
                    pType = node.attributes["type"].value if "type" in node.attributes else None
                    if pType and "value" in node.attributes:
                        dD[pType] = node.attributes["value"].value
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return dD

    def __getProteinNames(self, nodeList, tDict):
        """In content:
              <recommendedName>
                <fullName>Platelet-derived growth factor subunit B</fullName>
                <shortName>PDGF subunit B</shortName>
              </recommendedName>
              <alternativeName>
                <fullName>Platelet-derived growth factor B chain</fullName>
              </alternativeName>
              <alternativeName>
                <fullName>Platelet-derived growth factor beta polypeptide</fullName>
              </alternativeName>
              .....
            Get protein name from <recommendedName><fullName>...</fullName></recommendedName>
            and put rest names to synonyms using comma separator
        """

        for node in nodeList:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            if node.tagName in ["recommendedName", "alternativeName", "submittedName"]:
                nameD = self.__getNames(node.childNodes, nameType=node.tagName)
                tDict.setdefault("names", []).append(nameD)

    def __getNames(self, nodeList, nameType=None):
        """Get names from <fullName> & <shortName> tags:

                <fullName>Platelet-derived growth factor subunit B</fullName>
                <shortName>PDGF subunit B</shortName>
        """
        dD = {}
        for node in nodeList:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            if node.tagName in ["fullName", "shortName"]:
                dD["name"] = node.firstChild.data
                dD["isAbbrev"] = True if node.tagName == "shortName" else False
                dD["nameType"] = nameType

        return dD

    def __getGeneNames(self, nodeList, tDict):
        """Get genes from
              <gene>
                <name type="primary">PDGFB</name>
                <name type="synonym">PDGF2</name>
                <name type="synonym">SIS</name>
              </gene>
           and concatenate them using comma separator
        """
        for node in nodeList:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            if node.tagName == "name":
                tType = node.attributes["type"].value
                tDict.setdefault("gene", []).append({"name": node.firstChild.data, "type": tType})

    def __getSourceOrganism(self, nodeList, tDict):
        """Get organism's scientific name, common name and NCBI Taxonomy ID from
               <name type="scientific">Homo sapiens</name>
               <name type="common">Human</name>
               <dbReference type="NCBI Taxonomy" key="1" id="9606"/>
        """
        for node in nodeList:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            if node.tagName == "name":
                tType = node.attributes["type"]
                if tType:
                    if tType.value == "scientific":
                        tDict["source_scientific"] = node.firstChild.data
                    elif tType.value == "common":
                        tDict["source_common"] = node.firstChild.data

            elif node.tagName == "dbReference":
                tType = node.attributes["type"]
                if tType and tType.value == "NCBI Taxonomy":
                    tDict["taxonomy_id"] = int(node.attributes["id"].value)

    def __getComments(self, node, tDict):
        """From
              <comment type="function">
                <text>Platelet-derived .... </text>
              </comment>
              <comment type="subunit" evidence="EC1">
                <text status="by similarity">Antiparallel disulfide-linked .... </text>
              </comment>
              <comment type="miscellaneous">
                <text>A-A and B-B, as well as A-B, dimers can bind to the PDGF receptor.</text>
              </comment>
              <comment type="similarity">
                <text>Belongs to the PDGF/VEGF growth factor family.</text>
              </comment>
              .....
              <comment type="online information" name="Regranex">
                <link uri="http://www.regranex.com/"/>
                <text>Clinical information on Regranex</text>
              </comment>
           Get "type": "text" content and concatenate them using newline separator
           Comments from <comment type="online information"> will be ignored.
        """

        tType = node.attributes["type"]
        if tType and tType.value != "online information":
            text = self.__getText(node.childNodes)
            if text is not None:
                tDict.setdefault("comments", []).append({"type": tType.value, "text": text})

    def __getText(self, nodeList):
        """Get text value from
           <text status="by similarity">Antiparallel disulfide-linked .... </text>
        """
        for node in nodeList:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            if node.tagName == "text":
                return node.firstChild.data
        return None

    def __getIsoFormSeq(self, doc, vId, tDict):
        """Get isoform sequence for vId if it exists  -

           Returns: bool, bool, isoformD  status, sequenceUpdatedFlag, isoform name/type Dictionary
        """
        logger.debug("Starting vId %s", vId)
        try:
            isoformdic = self.__getIsoFormIds(doc)
            logger.debug("vId %s isoformdic  %r", vId, isoformdic.items())

            if not isoformdic:
                return False, False, None

            if vId not in isoformdic:
                return False, False, None

            # JDW 12-DEC-2015  Remove this test for a reference - Finding isoform data in comments lacking this
            if isoformdic[vId]["type"] == "displayed" or "ref" not in isoformdic[vId]:
                # return True, False
                return True, False, isoformdic[vId]

            refdic = self.__getIsoFormRefs(doc)
            logger.debug(" vId %s refdic  %r", vId, refdic.items())

            if not refdic:
                # return with sequence updated = False
                return True, False, isoformdic[vId]

            reflist = isoformdic[vId]["ref"].split(" ")
            # Reverse the ref list order so that sequence manipulation starts from C-terminal
            reflist.reverse()
            isoformEdits = []
            for ref in reflist:
                if ref in refdic:
                    tDict["sequence"] = self.__processIsoFormSeq(tDict["sequence"], refdic[ref])
                    isoformEdits.append(refdic[ref])
            if isoformEdits:
                isoformdic[vId]["isoform_edits"] = isoformEdits
            # return with seqquence updated = True
            return True, True, isoformdic[vId]
        except Exception as e:
            logger.exception("Failing with vId %s %s", vId, str(e))

        return False, False, None

    def __getIsoFormIds(self, doc):
        """Get isoform information from:
               <isoform>
                 <id>P42284-2</id>
                 <name>V</name>
                 <name>Ohsako-G</name>
                 <sequence type="displayed"/>
               </isoform>
               <isoform>
                 <id>P42284-3</id>
                 <name>H</name>
                 <name>Ohsako-M</name>
                 <sequence type="described" ref="VSP_015404 VSP_015406"/>
               </isoform>

           and put them into dictionary:

               { 'P42284-2' : { 'type' : 'displayed'},
                 'P42284-3' : { 'type' : 'described', 'ref' : 'VSP_015404 VSP_015406' } }
        """
        tDict = {}
        entryList = doc.getElementsByTagName("isoform")
        if not entryList:
            return tDict

        for node in entryList:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            # id = None
            tId = []
            names = []
            tType = None
            ref = None
            for node1 in node.childNodes:
                if node1.nodeType != node1.ELEMENT_NODE:
                    continue
                if node1.tagName == "id":
                    tId.append(node1.firstChild.data)
                elif node1.tagName == "name":
                    names.append(node1.firstChild.data)
                elif node1.tagName == "sequence":
                    tType = node1.attributes["type"].value
                    # JDW Aug-26 The following is behaving badly  --
                    try:
                        if "ref" in node1.attributes:
                            ref = node1.attributes["ref"].value
                    except Exception:
                        pass

            if not tId or not tType:
                continue
            dD = {}
            dD["type"] = tType
            dD["names"] = names
            if ref:
                dD["ref"] = ref
            tDict[tId[0]] = dD

        return tDict

    def __getIsoFormRefs(self, doc):
        """Get variant information from

               <feature type="splice variant" id="VSP_015404" description="(in isoform H)">
                 <original>DVSTNQTVVLPHYSIYHYYSNIYYLLSHTTIYEADRTVSVSCPGKLNCLPQRNDLQETKSVTVL</original>
                 <variation>DEAGQNEGGESRIRVRNWLMLADKSIIGKSSDEPSVLHIVLLLSTHRHIISFLLIIQSFIDKIY</variation>
                 <location>
                   <begin position="455"/>
                   <end position="518"/>
                 </location>
               </feature>
               <feature type="splice variant" id="VSP_015406" description="(in isoform H)">
                 <location>
                   <begin position="519"/>
                   <end position="549"/>
                 </location>
               </feature>

           and put them into dictionary:

               { 'VSP_015404' : { 'begin' : '455', 'end' : '518', 'variation' : 'DEAGQNEGG....' },
                 'VSP_015406' : { 'begin' : '519', 'end' : '549' } }
        """
        dic = {}
        entryList = doc.getElementsByTagName("feature")
        if not entryList:
            return dic

        for node in entryList:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            if node.attributes["type"].value != "splice variant":
                continue

            if "id" not in node.attributes:
                continue

            tId = node.attributes["id"].value
            begin = None
            end = None
            variation = None
            for node1 in node.childNodes:
                if node1.nodeType != node1.ELEMENT_NODE:
                    continue
                if node1.tagName == "variation":
                    variation = node1.firstChild.data.replace("\n", "")
                elif node1.tagName == "location":
                    for node2 in node1.childNodes:
                        if node2.nodeType != node2.ELEMENT_NODE:
                            continue
                        if node2.tagName == "begin":
                            begin = node2.attributes["position"].value
                        elif node2.tagName == "end":
                            end = node2.attributes["position"].value

            if not begin or not end:
                continue
            dD = {}
            dD["begin"] = begin
            dD["end"] = end
            if variation:
                dD["variation"] = variation
            dic[tId] = dD

        return dic

    def __processIsoFormSeq(self, seq, ref):
        """Manipulate sequence using information from dictionary ref:

               { 'begin' : '455', 'end' : '518', 'variation' : 'DEAGQNEGG....' }
        """
        begin = int(ref["begin"]) - 1
        end = int(ref["end"])
        seq1 = seq[0:begin]
        if "variation" in ref:
            seq1 += ref["variation"]
        seq1 += seq[end:]
        return seq1

    def __cleanString(self, strIn):
        sL = []
        for ss in strIn:
            if ss in string.whitespace:
                continue
            sL.append(ss)
        return "".join(sL)
