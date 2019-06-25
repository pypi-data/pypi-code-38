##
# File:    DrugBankUtils.py
# Author:  J. Westbrook
# Date:    17-Oct-2018
# Version: 0.001
#
# Update:
#
##
"""
Various utilities for extracting data from DrugBank repository data.

Approach is inspired by a useful examples at:

https://github.com/dhimmel/drugbank/blob/gh-pages/parse.ipynb
and https://github.com/bio2bel

"""
import gzip
import itertools as itt
import logging
import time
from datetime import datetime

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class DrugBankUtils(object):
    """
    """

    def __init__(self):
        self.__ns = "{http://www.drugbank.ca}"

    def read(self, filePath):
        xrt = self.__parse(filePath)
        rL = []
        for drugElement in xrt:
            rL.append(self.__processDrugElement(drugElement))
        return rL
        #

    def __parse(self, filePath):
        """ Parse the iput DrugBank export XML data file.
        """
        tree = []
        if filePath[-3:] == ".gz":
            with gzip.open(filePath, mode="rb") as ifh:
                logger.debug("Parsing drugbank at %s", filePath)
                tV = time.time()
                tree = ET.parse(ifh)
                logger.debug("Parsed drugbank in %.2f seconds", time.time() - tV)
        else:
            with open(filePath, mode="rb") as ifh:
                logger.debug("Parsing drugbank at %s", filePath)
                tV = time.time()
                tree = ET.parse(ifh)
                logger.debug("Parsed drugbank in %.2f seconds", time.time() - tV)
        return tree.getroot()

    def __processDrugElement(self, drugElement):
        """
        """
        assert drugElement.tag == "{ns}drug".format(ns=self.__ns)

        doc = {
            "type": drugElement.get("type"),
            "drugbank_id": drugElement.findtext("{ns}drugbank-id[@primary='true']".format(ns=self.__ns)),
            "cas_number": drugElement.findtext("{ns}cas-number".format(ns=self.__ns)),
            "name": drugElement.findtext("{ns}name".format(ns=self.__ns)),
            "description": drugElement.findtext("{ns}description".format(ns=self.__ns)),
            "indication": drugElement.findtext("{ns}indication".format(ns=self.__ns)),
            "pharmacodynamics": drugElement.findtext("{ns}pharmacodynamics".format(ns=self.__ns)),
            "mechanism-of-action": drugElement.findtext("{ns}mechanism-of-action".format(ns=self.__ns)),
            "groups": [group.text for group in drugElement.findall("{ns}groups/{ns}group".format(ns=self.__ns))],
            "affected-organisms": [org.text for org in drugElement.findall("{ns}affected-organisms/{ns}affected-organism".format(ns=self.__ns))],
            "atc_codes": [code.get("code") for code in drugElement.findall("{ns}atc-codes/{ns}atc-code".format(ns=self.__ns))],
            "categories": [
                {"name": el.findtext("{ns}category".format(ns=self.__ns)), "mesh_id": el.findtext("{ns}mesh-id".format(ns=self.__ns))}
                for el in drugElement.findall("{ns}categories/{ns}category".format(ns=self.__ns))
            ],
            "patents": [
                {
                    "patent_id": el.findtext("{ns}number".format(ns=self.__ns)),
                    "country": el.findtext("{ns}country".format(ns=self.__ns)),
                    "approved": datetime.strptime(el.findtext("{ns}approved".format(ns=self.__ns)), "%Y-%m-%d"),
                    "expires": datetime.strptime(el.findtext("{ns}expires".format(ns=self.__ns)), "%Y-%m-%d"),
                    "pediatric_extension": el.findtext("{ns}pediatric-extension".format(ns=self.__ns)) != "false",
                }
                for el in drugElement.findall("{ns}patents/{ns}patent".format(ns=self.__ns))
            ],
            "external_identifiers": [
                {"resource": el.findtext("{ns}resource".format(ns=self.__ns)), "identifier": el.findtext("{ns}identifier".format(ns=self.__ns))}
                for el in drugElement.findall("{ns}external-identifiers/{ns}external-identifier".format(ns=self.__ns))
            ],
            "pdb_entries": [pdbId.text for pdbId in drugElement.findall("{ns}pdb-entries/{ns}pdb-entry".format(ns=self.__ns))],
            "inchi": drugElement.findtext("{ns}calculated-properties/{ns}property[{ns}kind='InChI']/{ns}value".format(ns=self.__ns)),
            "inchikey": drugElement.findtext("{ns}calculated-properties/{ns}property[{ns}kind='InChIKey']/{ns}value".format(ns=self.__ns)),
            "exp_prop": [
                {
                    "kind": el.findtext("{ns}kind".format(ns=self.__ns)),
                    "value": el.findtext("{ns}value".format(ns=self.__ns)),
                    "source": el.findtext("{ns}source".format(ns=self.__ns)),
                }
                for el in drugElement.findall("{ns}experimental-properties/{ns}property".format(ns=self.__ns))
            ],
            "calc_prop": [
                {
                    "kind": el.findtext("{ns}kind".format(ns=self.__ns)),
                    "value": el.findtext("{ns}value".format(ns=self.__ns)),
                    "source": el.findtext("{ns}source".format(ns=self.__ns)),
                }
                for el in drugElement.findall("{ns}calculated-properties/{ns}property".format(ns=self.__ns))
            ],
            "products": [
                {
                    "name": el.findtext("{ns}name".format(ns=self.__ns)),
                    "labeller": el.findtext("{ns}labeller".format(ns=self.__ns)),
                    "ndc-id": el.findtext("{ns}ndc-id".format(ns=self.__ns)),
                    "ndc-product-code": el.findtext("{ns}ndc-product-code".format(ns=self.__ns)),
                    "dpd-id": el.findtext("{ns}dpd-id".format(ns=self.__ns)),
                    "ema-product-code": el.findtext("{ns}ema-product-code".format(ns=self.__ns)),
                    "ema-ma-number": el.findtext("{ns}ema-ma-number".format(ns=self.__ns)),
                    "started-marketing-on": el.findtext("{ns}started-marketing-on".format(ns=self.__ns)),
                    "ended-marketing-on": el.findtext("{ns}ended-marketing-on".format(ns=self.__ns)),
                    "dosage-form": el.findtext("{ns}dosage-form".format(ns=self.__ns)),
                    "strength": el.findtext("{ns}strength".format(ns=self.__ns)),
                    "route": el.findtext("{ns}route".format(ns=self.__ns)),
                    "fda-application-number": el.findtext("{ns}fda-application-number".format(ns=self.__ns)),
                    "generic": el.findtext("{ns}generic".format(ns=self.__ns)),
                    "over-the-counter": el.findtext("{ns}over-the-counter".format(ns=self.__ns)),
                    "approved": el.findtext("{ns}approved".format(ns=self.__ns)),
                    "country": el.findtext("{ns}country".format(ns=self.__ns)),
                    "source": el.findtext("{ns}source".format(ns=self.__ns)),
                }
                for el in drugElement.findall("{ns}products/{ns}product".format(ns=self.__ns))
            ],
        }
        aliases = {
            elem.text.strip().encode("ascii", "xmlcharrefreplace").decode("utf-8")
            for elem in itt.chain(drugElement.findall("{ns}synonyms/{ns}synonym".format(ns=self.__ns)), drugElement.findall("{ns}salts/{ns}salt/{ns}name".format(ns=self.__ns)))
            if elem.text.strip()
        }
        aliases.add(doc["name"])
        doc["aliases"] = aliases

        products = {
            elem.text.strip().encode("ascii", "xmlcharrefreplace").decode("utf-8")
            for elem in itt.chain(
                drugElement.findall("{ns}international-brands/{ns}international-brand".format(ns=self.__ns)),
                drugElement.findall("{ns}products/{ns}product/{ns}name".format(ns=self.__ns)),
            )
            if elem.text.strip()
        }
        doc["products"] = list(products)
        #
        doc["target_interactions"] = []
        targetCategories = ["target", "enzyme", "carrier", "transporter"]
        for category in targetCategories:
            targets = drugElement.findall("{ns}{category}s/{ns}{category}".format(ns=self.__ns, category=category))
            for target in targets:
                targetDoc = self.__getTargetInfo(category, target)
                if not targetDoc:
                    continue
                doc["target_interactions"].append(targetDoc)

        if "categories" in doc and doc["categories"]:
            doc["drug_categories"] = [c["name"] for c in doc["categories"]]
        return doc

    def __getTargetInfo(self, category, target):
        doc = {
            "category": category,
            "organism": target.findtext("{ns}organism".format(ns=self.__ns)),
            "known_action": target.findtext("{ns}known-action".format(ns=self.__ns)),
            "name": target.findtext("{ns}name".format(ns=self.__ns)),
            "amino-acid-sequence": target.findtext('{ns}polypeptide/{ns}amino-acid-sequence[@format="FASTA"]'.format(ns=self.__ns)),
            "actions": [action.text for action in target.findall("{ns}actions/{ns}action".format(ns=self.__ns))],
            "articles": [
                pubmed_element.text for pubmed_element in target.findall("{ns}references/{ns}articles/{ns}article/{ns}pubmed-id".format(ns=self.__ns)) if pubmed_element.text
            ],
        }

        uniprotIds = [
            polypep.text
            for polypep in target.findall("{ns}polypeptide/{ns}external-identifiers/{ns}external-identifier[{ns}resource='UniProtKB']/{ns}identifier".format(ns=self.__ns))
        ]
        if uniprotIds:
            doc["uniprot_ids"] = uniprotIds[0]

        hgncIds = [
            polypep.text
            for polypep in target.findall(
                "{ns}polypeptide/{ns}external-identifiers/{ns}external-identifier[{ns}resource='HUGO Gene Nomenclature Committee (HGNC)']/{ns}identifier".format(ns=self.__ns)
            )
        ]
        if len(hgncIds) == 1:
            doc["hgnc_id"] = hgncIds[0][len("HGNC:") :]

        return doc
