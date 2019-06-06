# Copyright 2013-2016 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import

import datetime

# from threatconnect import ResourceType


class IntelligenceProcessor(object):
    """
    Helper class for storing PhishMe Intelligence before sending to ThreatConnect. It builds out the Batch API dictionary
    for those ThreatConnect types that support it and helps with direct creation of those ThreatConnect types that don't
    """

    def __init__(self, owner, logger, tcex):
        """
        Initialize the PhishMeIntelligenceProcessor object

        :param str owner:  ThreatConnect owner/group for PhishMe Intelligence
        :param logger: The logging object to use for logging
        :type logger: :class:`logging.logger`
        :param tcex: The TcEx object used for interaction with the Batch API
        :type tcex: :class:`tcex.TcEx`
        :param tc: The ThreatConnect object used for communication with ThreatConnect
        :type tc: :class:`threatconnect.ThreatConnect`
        """

        self.logger = logger
        self.logger.debug("__init__ of PhishMeIntelligenceProcessor")
        self.owner = owner
        self.indicator_list = []
        self.current_indicator = {}
        self.malware_family_ids = []
        self.current_group = None
        self.current_document = None
        self.current_group_id = None
        self.current_document_id = None
        self.batch= tcex.batch(owner=self.owner, halt_on_error=False)

        self._initialize_indicator()
        self._initialize_group()
        self._initialize_document()

    def add_malware_family(self, malware_family, description):
        return # TODO: Convert this to batching, this is a nice to have but not required at the moment
        self.logger.debug("add_malware_family of PhishMeIntelligenceProcessor")
        # Query tc to see if a group for this malware family exists
        threats = self.threatconnect.threats()
        search = threats.add_filter()
        search.add_owner(self.owner)
        search.add_tag(malware_family)
        self.logger.debug('Searching for threats with the name '+ malware_family)
        try:
            threats.retrieve()
        except RuntimeError as e:
            self.logger.error("Error getting the malware family " + malware_family + str(e))


        # If it doesn't exist then create the group and get the id
        found_threat = False

        for threat in threats:
            self.logger.debug('Found threat for ' + malware_family)
            self.logger.debug('Adding family_id ' + str(threat.id))
            found_threat = True
            self.logger.debug('Associating with current group')
            threat.associate_group(ResourceType.THREATS, self.current_group_id)
            try:
                threat.commit()
            except RuntimeError as e:
                self.logger.error('Error associating {0} with {1}'.format(self.current_group_id, malware_family))
        if found_threat:
            return
        
        self.logger.debug('No threat found, adding new threat')
        self.logger.debug('Adding family ' + malware_family)
        new_family = self.threatconnect.threats().add(malware_family, self.owner)
        new_family.add_tag(malware_family)
        new_family.add_attribute('Description', description)
        new_family.associate_group(ResourceType.THREATS, self.current_group_id)
        try:
            new_family.commit()

        except RuntimeError as e:
            self.logger.error("Error creating the group for the malware family named " + malware_family + str(e))
            return

    def _add_indicator(self, indicator_type, indicator):

        indicator_xid = self.batch.generate_xid([self.owner, indicator, indicator_type])

        current_indicator = self.batch.indicators[indicator_xid] if indicator_xid in self.batch.indicators else None
        
        if not current_indicator:
            current_indicator = {"xid": indicator_xid, "summary": indicator, "type": indicator_type}
        else:
            self.duplicate_indicator = True
            self.logger.debug("Indicator already exists so we're just associating the group")
        
        if "associatedGroups" not in current_indicator:
            current_indicator["associatedGroups"] = []

        if self.current_group_xid not in current_indicator["associatedGroups"]:
            current_indicator["associatedGroups"].append({"groupXid": self.current_group_xid})

        self.current_indicator = current_indicator

    def add_ip_indicator(self, ip):
        """
        Create ThreatConnect indicator of type Address (and group association) for Batch API list

        :param str ip: The Ip Address to add
        """
        self.logger.debug("add_ip_indicator of PhishMeIntelligenceProcessor")
        self._add_indicator("Address", ip)

    def add_email_indicator(self, email):
        """
        Create ThreatConnect indicator of type EmailAddress (and group association) for Batch API list

        :param str email: The email address to add
        """
        self.logger.debug("add_email_indicator of PhishMeIntelligenceProcessor")
        self._add_indicator("EmailAddress", email)

    def add_host_indicator(self, host):
        """
        Create ThreatConnect indicator of type Host (and group association) for Batch API list

        :param str host: The hostname to add
        """
        self.logger.debug("add_host_indicator of PhishMeIntelligenceProcessor")
        self._add_indicator("Host", host)

    def add_domain_indicator(self, domain):
        self.logger.debug("add_domain_indicator of PhishMeIntelligenceProcessor")
        self._add_indicator("Domain", domain)

    def add_url_indicator(self, url):
        """
        Create ThreatConnect indicator of type URL (and group association) for Batch API list

        :param str url: The URL to add
        """
        self.logger.debug("add_url_indicator of PhishMeIntelligenceProcessor")
        self._add_indicator("URL", url)

    def add_file_indicator(self, md5, sha1=None, sha256=None):
        """
        Create ThreatConnect indicator of type File (and group association) for Batch API list

        :param str md5: MD5 of file indicator
        :param sha1: SHA-1 of file indicator
        :param sha256: SHA-256 of file indicator
        """
        self.logger.debug("add_file_indicator of PhishMeIntelligenceProcessor")
        hashes = "{} : {} : {}".format(md5, sha1, sha256)
        self._add_indicator("File", hashes)
        self.add_indicator_rating(3)

    def _add_indicator_group_association(self, indicator):
        """
        Sets up group association for indicator being processed

        :param dict indicator: indicator to add association to
        """
        self.logger.debug("_add_indicator_group_association of PhishMeIntelligenceProcessor")
        
        indicator["associatedGroups"] = []

        if self.current_group_xid is not None:
            self.logger.debug('{0} is associated to group_xid {1}'.format(indicator["summary"], self.current_group_xid))
            indicator["associatedGroups"].append({"groupXid": str(self.current_group_xid)})
            
        if self.current_document_id is not None:
            indicator["associatedGroups"].append({"groupXid": str(self.current_document_id)})

    def add_indicator_attribute(self, attribute_type, value):
        """
        Add ThreatConnect attribute for current indicator being processed

        :param str attribute_type:  Type of attribute
        :param str value: Value of attribute
        """
        self.logger.debug("add_indicator_attribute of PhishMeIntelligenceProcessor")
        if "attribute" not in self.current_indicator:
            self.current_indicator["attribute"] = []

        new_indicator_attribute = {"type": attribute_type,
                                   "value": value}
        if new_indicator_attribute not in self.current_indicator["attribute"]:
            self.current_indicator["attribute"].append(new_indicator_attribute)

    def add_group_attribute(self, attribute_type, value):
        """
        Add ThreatConnect attribute to current group being processed

        :param str attribute_type:  Type of attribute
        :param str value: Value of attribute
        """
        self.logger.debug("add_group_attribute of PhishMeIntelligenceProcessor")
        self.current_group.attribute(attribute_type, value)

    def add_indicator_tag(self, name):
        """
        add tag to current indicator being processed

        :param str name: tag to add
        """
        self.logger.debug("add_indicator_tag of PhishMeIntelligenceProcessor")
        if "tag" not in self.current_indicator:
            self.current_indicator["tag"] = []

        self.logger.debug('Adding tag {0} to {1}'.format(name, self.current_indicator['summary']))
        new_tag = {"name": name}
        if new_tag not in self.current_indicator["tag"]:
            self.current_indicator["tag"].append(new_tag)

    def add_group_tag(self, name):
        """
        add tag to current group being processed

        :param str name: tag to add
        """
        self.logger.debug("add_group_tag of PhishMeIntelligenceProcessor")
        self.current_group.tag(name)

    def add_indicator_rating(self, rating):
        """
        add rating value to current indicator being processed

        :param str rating: tag to add
        """
        self.logger.debug("add_indicator_rating of PhishMeIntelligenceProcessor")
        # If the rating of the current indicator is higher than or equal to the new rating then ignore this.
        # Keeping the higher rating
        if "rating" in self.current_indicator and self.current_indicator["rating"] >= rating:
            return
        self.current_indicator["rating"] = rating

    def _generate_group_xid(self, threat_id, group_type, owner):
        return self.batch.generate_xid([str(threat_id), group_type, owner])

    def add_group(self, group_type, group_name, published_date, threat_id):
        """
        Create group stub (this is not the commit to ThreatConnect)

        :param str group_type:  Type of group
        :param str group_name:  Name of group
        :param int published_date: published date (epoch timestamp)
        """
        self.logger.debug("add_group of PhishMeIntelligenceProcessor")
        self.logger.debug('Calling add_group in pm_intel_processor. group_type: {}, group_name: {}, published_date: {}'
                          .format(group_type, group_name, published_date))

        group_xid = self._generate_group_xid(threat_id, group_type, self.owner)

        group_type = "Threat" if group_type.lower().strip() == "threat" else "Incident"
        
        self.current_group = self.batch.group(group_type, group_name, xid=group_xid, date_added=published_date/1000)
        self.current_group_xid = group_xid

        if group_type == "Incident":
            self.current_group.add_key_value('eventDate', datetime.datetime.fromtimestamp(published_date/1000).strftime('%Y-%m-%dT%X'))

    def add_document(self, document_name, file_name, active_threat_report, group_type, threat_id):
        """
        Create document stub (this is not the commit to ThreatConnect)

        :param str document_name: Name to give Document type
        :param str file_name:  Name of document
        :param str active_threat_report:
        :param str group_type: Type of group this document will be associated wit
        """
        self.logger.debug("add_document of PhishMeIntelligenceProcessor")
        self.current_document_xid = self._generate_group_xid("Document", document_name, str(threat_id))
        self.current_document = self.batch.group("Document", document_name, xid=self.current_document_xid, associatedGroupXid=[self.current_group_xid])
        self.current_document.add_key_value('fileName', file_name)
        self.current_document.add_file(file_name, active_threat_report)

    def add_document_attribute(self, attribute_type, value):
        """
        Add ThreatConnect attribute to current document being processed

        :param str attribute_type:  Type of attribute
        :param str value: Value of attribute
        """
        self.logger.debug("add_document_attribute of PhishMeIntelligenceProcessor")
        self.current_document.attribute(attribute_type, value)

    def add_document_tag(self, tag):
        """
        add tag to current document being processed

        :param str name: tag to add
        """
        self.logger.debug("add_document_tag of PhishMeIntelligenceProcessor")

        self.current_document.tag(tag)

    def group_ready(self):
        """
        Call this method to indicate that group is ready to be "processed" (sent to ThreatConnect instance)

        :return: None
        """
        self.logger.debug("group_ready of PhishMeIntelligenceProcessor")
        self._process_group(self.current_group)

    def document_ready(self):
        """
        Call this method to indicate that document is ready to be "processed" (sent to ThreatConnect instance)

        :return: None
        """
        self.logger.debug("document_ready of PhishMeIntelligenceProcessor")
        self._process_document(self.current_document)

    def indicator_ready(self, source, threat_id):
        """
        Call this method to indicate that indicator is ready to be processed. This method also handles the situation
        where duplicate indicators exist in the current batch.

        :param str source: source of intelligence (always PhishMe Intelligence at this point)
        :param int threat_id:  Current Phishme Intelligence threat id being processed
        :return: None
        """
        self._process_indicator()

    def _process_group(self, group):
        """
        Commit group to ThreatConnect and prepare for next group

        :param group: ThreatConnect group object
        :type group: :class:`threatconnect-python.threatconnect.GroupObject`
        """
        self.logger.debug("process_group of PhishMeIntelligenceProcessor")
        self.current_group_xid = group.xid
        self._initialize_group()

    def _process_document(self, document):
        """
        Commit document to ThreatConnect and prepare for next group

        :param document: ThreatConnect document object
        :type doucment: :class:`threatconnect-python.threatconnect.DocumentObject`
        """
        self.logger.debug("process_document of PhishMeIntelligenceProcessor")
        self.current_document_xid = document.xid
        self._initialize_document()

    def _process_indicator(self):
        """
        Add ThreatConnect indicator to batch processing queue

        :param dict indicator: ThreatConnect Indicator is is ready for batch processing
        """
        self.logger.debug("_process_indicator of PhishMeIntelligenceProcessor")
        self.logger.debug(str(self.current_indicator))
        self.logger.debug("Adding indicator with xid: {}".format(self.current_indicator["xid"]))
        self.batch.add_indicator(self.current_indicator)
        self._initialize_indicator()

    def _check_for_duplicate_indicator(self, indicator):
        """
        Helper method to search for a duplicate indicator; if it exists return it and remove it from current list

        :param indicator: indicator that we are looking for a duplicate of
        :return: Duplicate indicator (if one exists)
        :rtype: dict or None
        """
        self.logger.debug("_check_for_duplicate_indicator of PhishMeIntelligenceProcessor")

        try:
            existing_indicators = self.batch.indicators
            self.logger.debug(type(existing_indicators))
            self.logger.debug(dir(existing_indicators))
            self.logger.debug(str(existing_indicators))
            # We have found a match
            matched_indicator = next(i for i in existing_indicators if
                                     i["xid"] == indicator["xid"])
            # Remove match from existing list and return
            existing_indicators[:] = [i for i in existing_indicators if
                                      i["xid"] != indicator["xid"]]
            self.batch.unprocessed_indicators = existing_indicators
            # Return matched indicator
            self.logger.debug("Indicator " + indicator["summary"].split(" :")[0] + " Is already in processing list...")
            return matched_indicator
        except StopIteration:
            # No existing indicator, so
            return None

    def commit(self):
        """
        Kick off batch processing of indicators to push into ThreatConnect

        :return: None
        """
        self.logger.debug("commit of PhishMeIntelligenceProcessor")
        try:
            self.logger.debug('processing jobs')
            self.batch.submit_all(halt_on_error=False)
            #self.logger.debug('indicator_results {}'.format(self.batch.indicator_results))
        except Exception as e:
            self.logger.error("Failure Batch Processing Indicators: " + str(e))

    def _initialize_indicator(self):
        """
        Preparation for processing new Indicator to add to ThreatConnect batch processing queue
        """
        self.logger.debug("_initialize_indicator of PhishMeIntelligenceProcessor")
        self.current_indicator = {"confidence": 100}  # Always high confidence due to analyst vetting
        self.duplicate_indicator = False
        

    def _initialize_group(self):
        """
        Preparation for processing new group to push into ThreatConnect
        """
        self.logger.debug("_initialize_group of PhishMeIntelligenceProcessor")
        self.current_group = None
        self.current_document = None
        self.current_document_id = None

    def _initialize_document(self):
        """
        Prepartion for processing new document to push into ThreatConnect
        """
        self.logger.debug("_initialize_document of PhishMeIntelligenceProcessor")
        self.current_document = None
