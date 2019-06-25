##
# File:    PubMedReader.py
# Author:  J. Westbrook
# Date:    27-Apr-2019
# Version: 0.001
#
# Update:
#
##
"""
Various utilities for extracting data from PubMed citations and related reference data.

"""
import logging

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class PubMedReader(object):
    """ Limited parser for PubMed XML entry data.
    """

    def __init__(self):
        self.__ns = ""

    def readString(self, xmlText):
        rD = {}
        logger.debug("Text is %r", xmlText)
        rootEl = ET.fromstring(xmlText)
        for pmEl in rootEl:
            logger.debug("root is %r", pmEl)
            dD = self.__processPubMedElement(pmEl)
            if "pmid" in dD:
                rD[dD["pmid"]] = dD

        return rD

    def __processPubMedElement(self, pmEl):

        assert pmEl.tag == "{ns}PubmedArticle".format(ns=self.__ns)

        doc = {"pmid": pmEl.findtext("{ns}MedlineCitation/{ns}PMID".format(ns=self.__ns))}

        #
        el = pmEl.find("{ns}MedlineCitation/{ns}Article".format(ns=self.__ns))
        logger.debug("article model %r", el.get("PubModel"))
        doc["article"] = self.__processArticle(el) if el is not None else {}
        #
        el = pmEl.find("{ns}MedlineCitation/{ns}ChemicalList".format(ns=self.__ns))
        doc["chemicals"] = self.__processChemicals(el) if el is not None else []
        #
        el = pmEl.find("{ns}MedlineCitation/{ns}MeshHeadingList".format(ns=self.__ns))
        doc["mesh"] = self.__processMesh(el) if el is not None else []
        #
        el = pmEl.find("{ns}PubmedData".format(ns=self.__ns))
        doc["related_ids"] = self.__processData(el) if el is not None else {}
        #
        #
        return doc

    def __processData(self, el):
        """
         <PubmedData>
         <ArticleIdList>
                <ArticleId IdType="pubmed">21540484</ArticleId>
                <ArticleId IdType="pii">M111.221069</ArticleId>
                <ArticleId IdType="doi">10.1074/jbc.M111.221069</ArticleId>
                <ArticleId IdType="pmc">PMC3123100</ArticleId>
                ...
        """
        doc = {}
        for ael in el.findall("{ns}ArticleIdList/{ns}ArticleId".format(ns=self.__ns)):
            if ael.get("IdType") in ["pmc"]:
                doc["pmcid"] = ael.text
            elif ael.get("IdType") in ["doi"]:
                doc["doi"] = ael.text
        #
        return doc

    def __processMesh(self, el):
        """
        <MeshHeadingList>
                <MeshHeading>
                    <DescriptorName UI="D000444" MajorTopicYN="N">Aldehyde Dehydrogenase</DescriptorName>
                    <QualifierName UI="Q000737" MajorTopicYN="Y">chemistry</QualifierName>
                    <QualifierName UI="Q000235" MajorTopicYN="N">genetics</QualifierName>
                    <QualifierName UI="Q000378" MajorTopicYN="N">metabolism</QualifierName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D019943" MajorTopicYN="N">Amino Acid Substitution</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D020134" MajorTopicYN="Y">Catalytic Domain</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D003067" MajorTopicYN="N">Coenzymes</DescriptorName>
                    <QualifierName UI="Q000737" MajorTopicYN="Y">chemistry</QualifierName>
                    <QualifierName UI="Q000235" MajorTopicYN="N">genetics</QualifierName>
                    <QualifierName UI="Q000378" MajorTopicYN="N">metabolism</QualifierName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D018360" MajorTopicYN="N">Crystallography, X-Ray</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D006801" MajorTopicYN="N">Humans</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D020125" MajorTopicYN="N">Mutation, Missense</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D009249" MajorTopicYN="N">NADP</DescriptorName>
                    <QualifierName UI="Q000737" MajorTopicYN="Y">chemistry</QualifierName>
                    <QualifierName UI="Q000235" MajorTopicYN="N">genetics</QualifierName>
                    <QualifierName UI="Q000378" MajorTopicYN="N">metabolism</QualifierName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D011485" MajorTopicYN="N">Protein Binding</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D017433" MajorTopicYN="N">Protein Structure, Secondary</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D017434" MajorTopicYN="N">Protein Structure, Tertiary</DescriptorName>
                </MeshHeading>
            </MeshHeadingList>
        """
        rL = []
        try:
            rL = [{"term": ml.text, "id": ml.get("UI"), "major": ml.get("MajorTopicYN")} for ml in el.findall("{ns}MeshHeading/{ns}DescriptorName".format(ns=self.__ns))]
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return rL

    def __processChemicals(self, el):
        """
         <ChemicalList>
                <Chemical>
                    <RegistryNumber>0</RegistryNumber>
                    <NameOfSubstance UI="D003067">Coenzymes</NameOfSubstance>
                </Chemical>
                <Chemical>
                    <RegistryNumber>53-59-8</RegistryNumber>
                    <NameOfSubstance UI="D009249">NADP</NameOfSubstance>
                </Chemical>
                <Chemical>
                    <RegistryNumber>EC 1.2.1.3</RegistryNumber>
                    <NameOfSubstance UI="D000444">Aldehyde Dehydrogenase</NameOfSubstance>
                </Chemical>
                <Chemical>
                    <RegistryNumber>EC 1.5.1.6</RegistryNumber>
                    <NameOfSubstance UI="C534194">ALDH1L1 protein, human</NameOfSubstance>
                </Chemical>
            </ChemicalList>
        """
        rL = []
        try:
            rL = [
                {"registry_number": cl.findtext("{ns}RegistryNumber".format(ns=self.__ns)), "name": cl.findtext("{ns}NameOfSubstance".format(ns=self.__ns))}
                for cl in el.findall("{ns}Chemical".format(ns=self.__ns))
            ]
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return rL

    def __processArticle(self, el):
        """
        <Article PubModel="Print-Electronic">
                <Journal>
                    <ISSN IssnType="Electronic">1083-351X</ISSN>
                    <JournalIssue CitedMedium="Internet">
                        <Volume>286</Volume>
                        <Issue>26</Issue>
                        <PubDate>
                            <Year>2011</Year>
                            <Month>Jul</Month>
                            <Day>01</Day>
                        </PubDate>
                    </JournalIssue>
                    <Title>The Journal of biological chemistry</Title>
                    <ISOAbbreviation>J. Biol. Chem.</ISOAbbreviation>
                </Journal>
                <ArticleTitle>
                    Conserved catalytic residues of the ALDH1L1 aldehyde dehydrogenase domain control binding and discharging of the coenzyme.
                </ArticleTitle>
                <Pagination>
                    <MedlinePgn>23357-67</MedlinePgn>
                </Pagination>
                <ELocationID EIdType="doi" ValidYN="Y">10.1074/jbc.M111.221069</ELocationID>
                <Abstract>
                    <AbstractText>
                        The C-terminal domain (C(t)-FDH) of 10-formyltetrahydrofolate dehydrogenase (FDH, ALDH1L1) is an ...
                    </AbstractText>
                </Abstract>
                <AuthorList CompleteYN="Y">
                    <Author ValidYN="Y">
                        <LastName>Tsybovsky</LastName>
                        <ForeName>Yaroslav</ForeName>
                        <Initials>Y</Initials>
                        <AffiliationInfo>
                            <Affiliation>
                                Department of Biochemistry and Molecular Biology, Medical University of South Carolina, Charleston, South Carolina 29425, USA.
                            </Affiliation>
                        </AffiliationInfo>
                    </Author>
                    <Author ValidYN="Y">
                        <LastName>Krupenko</LastName>
                        <ForeName>Sergey A</ForeName>
                        <Initials>SA</Initials>
                    </Author>
                </AuthorList>
                <Language>eng</Language>
                <DataBankList CompleteYN="Y">
                    <DataBank>
                        <DataBankName>PDB</DataBankName>
                        <AccessionNumberList>
                            <AccessionNumber>3RHJ</AccessionNumber>
                            <AccessionNumber>3RHL</AccessionNumber>
                            <AccessionNumber>3RHM</AccessionNumber>
                            <AccessionNumber>3RHO</AccessionNumber>
                            <AccessionNumber>3RHP</AccessionNumber>
                            <AccessionNumber>3RHQ</AccessionNumber>
                            <AccessionNumber>3RHR</AccessionNumber>
                        </AccessionNumberList>
                    </DataBank>
                </DataBankList>
                <GrantList CompleteYN="Y">
                    <Grant>
                        <GrantID>R01 DK054388</GrantID>
                        <Acronym>DK</Acronym>
                        <Agency>NIDDK NIH HHS</Agency>
                        <Country>United States</Country>
                    </Grant>
                    <Grant>
                        <GrantID>DK54388</GrantID>
                        <Acronym>DK</Acronym>
                        <Agency>NIDDK NIH HHS</Agency>
                        <Country>United States</Country>
                    </Grant>
                </GrantList>
                <PublicationTypeList>
                    <PublicationType UI="D016428">Journal Article</PublicationType>
                    <PublicationType UI="D052061">Research Support, N.I.H., Extramural</PublicationType>
                    <PublicationType UI="D013485">Research Support, Non-U.S. Gov't</PublicationType>
                </PublicationTypeList>
                <ArticleDate DateType="Electronic">
                    <Year>2011</Year>
                    <Month>05</Month>
                    <Day>03</Day>
                </ArticleDate>
            </Article>
        """
        aD = {
            "pubmed_model": el.attrib["PubModel"],
            "ISSN": el.findtext("{ns}Journal/{ns}ISSN".format(ns=self.__ns)),
            "journal_title": el.findtext("{ns}Journal/{ns}Title".format(ns=self.__ns)),
            "journal_title_iso_abbrev": el.findtext("{ns}Journal/{ns}ISOAbbreviation".format(ns=self.__ns)),
            #
            "article_volume": el.findtext("{ns}Journal/{ns}JournalIssue/{ns}Volume".format(ns=self.__ns)),
            "article_isssue": el.findtext("{ns}Journal/{ns}JournalIssue/{ns}Issue".format(ns=self.__ns)),
            "articleYear": el.findtext("{ns}Journal/{ns}JournalIssue/{ns}PubDate/{ns}Year".format(ns=self.__ns)),
            #
            "article_title": el.findtext("{ns}ArticleTitle".format(ns=self.__ns)),
            "article_page_range": el.findtext("{ns}Pagination/{ns}MedlinePgn".format(ns=self.__ns)),
            "authors": [
                {
                    "last_name": al.findtext("{ns}LastName".format(ns=self.__ns)),
                    "fore_name": al.findtext("{ns}ForeName".format(ns=self.__ns)),
                    "initials": al.findtext("{ns}Initials".format(ns=self.__ns)),
                    "affiliations": [aal.findtext("{ns}Affiliation".format(ns=self.__ns)) for aal in al.findall("{ns}AffiliationInfo".format(ns=self.__ns))],
                }
                for al in el.findall("{ns}AuthorList/{ns}Author".format(ns=self.__ns))
            ],
            "grants": [
                {
                    "grant_id": al.findtext("{ns}GrantID".format(ns=self.__ns)),
                    "acronym": al.findtext("{ns}Acronym".format(ns=self.__ns)),
                    "agency": al.findtext("{ns}Agency".format(ns=self.__ns)),
                    "country": al.findtext("{ns}Country".format(ns=self.__ns)),
                }
                for al in el.findall("{ns}GrantList/{ns}Grant".format(ns=self.__ns))
            ],
            "abstract": el.findtext("{ns}Abstract/{ns}AbstractText".format(ns=self.__ns)),
        }
        #
        return aD
