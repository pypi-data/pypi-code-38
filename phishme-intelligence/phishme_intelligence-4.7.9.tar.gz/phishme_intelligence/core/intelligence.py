#Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
#This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
#including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
#disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
#consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
#this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import


class Malware(object):
    """
    Malware class holds a single PhishMe Intelligence object.
    """

    def __init__(self, malware, config=None):
        """
        Initialize Malware object.

        :param str malware:
        :param ConfigParser config:
        """

        # Each of the items with a return value of None is handled by a property and setter.

        self.json = malware
        """
        The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.Malware` object.

        :return: String representation of this object.
        :rtype: str
        """

        self.config = config
        """
        The config.ini data used to configure the integration processing this intelligence
        
        :return: Config.ini (ConfigParser)
        :rtype: ConfigParser or None
        """

        self.first_published = self.json.get('firstPublished')
        """
        The first time this campaign was published by PhishMe Intelligence.

        :return: A timestamp in epoch milliseconds.
        :rtype: int
        """

        self.last_published = self.json.get('lastPublished')
        """
        The last time this campaign was published by PhishMe Intelligence.

        :return: A timestamp in epoch milliseconds.
        :rtype: int
        """

        self.active_threat_report = self.json.get('reportURL')
        """
        A direct URL accessible with PhishMe Intelligence portal credentials to a human-readable document intended to 
        provide a more accessible explanation for the sum of a malware campaign's significance.

        :return: A URL to a PhishMe Intelligence Active Threat Report.
        :rtype: str
        """


        self.threathq_url = self.json.get('threatDetailURL')
        """
        .. deprecated:: 4.0.0

        Use :func:`phishme_intelligence.core.intelligence.Malware.threat_detail_url()` instead.

        :return: URL to this Threat ID in PhishMe Intelligence portal.
        :rtype: str
        """

        self.threat_detail_url = self.json.get('threatDetailURL')
        """
        A direct URL to the PhishMe Intelligence portal for this specific Threat ID.

        :return: URL to this Threat ID in PhishMe Intelligence portal.
        :rtype: str
        """

        self.threat_id = self.json.get('id')
        """
        A unique identifier across all malware attacks recorded by PhishMe.

        :return: A numeric identifier for a campaign.
        :rtype: str
        """

        self.label = self.json.get('label')
        """
        Short summary of the topic, brand, and malware families involved in this Threat ID.

        :return: Summary of the campaign, can be used as a title.
        :rtype: str
        """

        self.executiveSummary = self.json.get('executiveSummary')
        """
        .. deprecated:: 4.0.0

        Use :func:`phishme_intelligence.core.intelligence.Malware.executive_summary()` instead.

        :return: A summary of this campaign.
        :rtype: str
        """

        self.executive_summary = self.json.get('executiveSummary')
        """
        The executive summary from the Active Threat Report associated with this campaign.

        :return: A summary of this campaign.
        :rtype: str
        """

        # self.active_threat_report_api = self.json.get('apiReportURL')
        self.active_threat_report_api = None
        """
        A direct URL accessible with API credentials to a human-readable document intended to provide a more accessible 
        explanation for the sum of a malware campaign's significance.

        :return: A URL to a PhishMe Intelligence Active Threat Report.
        :rtype: str
        """

        self.brand = None
        """
        A list of all the brands being imitated by this malware campaign

        :return: A comma-separated list of brand.
        :rtype: str or None
        """

        self.malware_family = None
        """
        A list of all the malware families included in this campaign.

        :return: A comma-separated list of the malware families.
        :rtype: str or None
        """

        self.block_set = None
        """
        .. seealso:: :class:`phishme_intelligence.core.intelligence.Malware.BlockSet`

        :return: list of :class:`phishme_intelligence.core.intelligence.Malware.BlockSet`
        :rtype: list
        """

        self.domain_set = None
        """
        .. seealso:: :class:`phishme_intelligence.core.intelligence.Malware.DomainSet`

        :return: list of :class:`phishme_intelligence.core.intelligence.Malware.DomainSet`
        :rtype: list
        """

        self.executable_set = None
        """
        .. seealso:: :class:`phishme_intelligence.core.intelligence.Malware.ExecutableSet`

        :return: list of :class:`phishme_intelligence.core.intelligence.Malware.ExecutableSet`
        :rtype: list
        """

        self.sender_ip_set = None
        """
        .. seealso:: :class:`phishme_intelligence.core.intelligence.Malware.SenderIPSet`

        :return: list of :class:`phishme_intelligence.core.intelligence.Malware.SenderIPSet`
        :rtype: list
        """

        self.spam_url_set = None
        """
        .. seealso:: :class:`phishme_intelligence.core.intelligence.Malware.SpamURLSet`

        :return: list of :class:`phishme_intelligence.core.intelligence.Malware.SpamURLSet`
        :rtype: list
        """

        self.subject_set = None
        """
        .. seealso:: :class:`phishme_intelligence.core.intelligence.Malware.SubjectSet`

        :return: list of :class:`phishme_intelligence.core.intelligence.Malware.SubjectSet`
        :rtype: list
        """

        self.sender_email_set = None
        """
        .. seealso:: :class:`phishme_intelligence.core.intelligence.Malware.SenderEmailSet`

        :return: list of :class:`phishme_intelligence.core.intelligence.Malware.SenderEmailSet`
        :rtype: list
        """
    @property
    def active_threat_report_api(self):
        """

        :return:
        """
        return self._active_threat_report_api

    @active_threat_report_api.setter
    def active_threat_report_api(self, value):
        """

        :param value:
        :return:
        """
        if self.config != None:
            normal_base_url = 'https://www.threathq.com/apiv1'
            configured_base_url = self.config.get("pm_api", "base_url")
            if configured_base_url != normal_base_url:
                self._active_threat_report_api = self.json.get('apiReportURL').replace(normal_base_url, configured_base_url)
            else:
                self._active_threat_report_api = self.json.get('apiReportURL')
        else:
            self._active_threat_report_api = self.json.get('apiReportURL')


    @property
    def malware_family(self):
        """
        :rtype: str
        """

        return self._malware_family

    @malware_family.setter
    def malware_family(self, value):
        """
        :param value:
        :return: None
        """

        if self.json.get('malwareFamilySet'):
            family_temp = []
            for family in self.json.get('malwareFamilySet'):
                family_temp.append(family.get('familyName'))
            self._malware_family = ', '.join(family_temp)
        else:
            self._malware_family = None

    @property
    def brand(self):
        """
        :rtype: str or None
        """

        return self._brand

    @brand.setter
    def brand(self, value):
        """
        :param value:
        :return: None
        """

        if self.json.get('campaignBrandSet'):
            brand_temp = []
            for brand in self.json.get('campaignBrandSet'):
                brand_temp.append(brand.get('brand').get('text'))
            self._brand = ', '.join(brand_temp)
        else:
            self._brand = None

    @property
    def block_set(self):
        """
        :rtype: list of :class:`phishme_intelligence.core.intelligence.Malware.BlockSet`
        """

        return self._block_set

    @block_set.setter
    def block_set(self, value):
        """
        :param value:
        :return: None
        """

        return_list = []

        for item in self.json.get('blockSet'):
            return_list.append(self.BlockSet(item))

        self._block_set = return_list

    @property
    def domain_set(self):
        """
        :rtype: list of :class:`phishme_intelligence.core.intelligence.Malware.DomainSet`
        """

        return self._domain_set

    @domain_set.setter
    def domain_set(self, value):
        """

        :param value:
        :return: None
        """

        return_list = []

        for item in self.json.get('domainSet'):
            return_list.append(self.DomainSet(item))

        self._domain_set = return_list

    @property
    def executable_set(self):
        """
        :rtype: list of :class:`phishme_intelligence.core.intelligence.Malware.ExecutableSet`
        """

        return self._executable_set

    @executable_set.setter
    def executable_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('executableSet'):
            return_list.append(self.ExecutableSet(item))

        self._executable_set = return_list

    @property
    def sender_ip_set(self):
        """
        :rtype: list of :class:`phishme_intelligence.core.intelligence.Malware.SenderIPSet`
        """

        return self._sender_ip_set

    @sender_ip_set.setter
    def sender_ip_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('senderIpSet'):
            return_list.append(self.SenderIPSet(item))

        self._sender_ip_set = return_list

    @property
    def sender_email_set(self):
        """
        :rtype: list of :class:`phishme_intelligence.core.intelligence.Malware.SenderEmailSet`
        """

        return self._sender_email_set

    @sender_email_set.setter
    def sender_email_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('senderEmailSet'):
            return_list.append(self.SenderEmailSet(item))

        self._sender_email_set = return_list

    @property
    def subject_set(self):
        """
        :rtype: list of :class:`phishme_intelligence.core.intelligence.Malware.SubjectSet`
        """

        return self._subject_set

    @subject_set.setter
    def subject_set(self, value):
        """

        :param value:
        :return: None
        """

        return_list = []

        for item in self.json.get('subjectSet'):
            return_list.append(self.SubjectSet(item))

        self._subject_set = return_list

    @property
    def spam_url_set(self):
        """
        :rtype: list of :class:`phishme_intelligence.core.intelligence.Malware.SpamURLSet`
        """

        return self._spam_url_set

    @spam_url_set.setter
    def spam_url_set(self, value):
        """

        :param value:
        :return: None
        """

        return_list = []

        for item in self.json.get('spamUrlSet'):
            return_list.append(self.SpamURLSet(item))

        self._spam_url_set = return_list

    @property
    def block_set(self):
        """

        :return:
        """

        return self._block_set

    @block_set.setter
    def block_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('blockSet'):
            return_list.append(self.BlockSet(item))

        self._block_set = return_list

    @property
    def malware_family(self):
        """

        :param self:
        :return:
        """

        return self._malware_family

    @malware_family.setter
    def malware_family(self, value):
        """
        Return comma-separated list of malware families.

        :param value:
        :return:
        """

        if self.json.get('malwareFamilySet'):
            family_temp = []
            for family in self.json.get('malwareFamilySet'):
                family_temp.append(family.get('familyName'))
            self._malware_family = ', '.join(family_temp)
        else:
            self._malware_family = None

    @property
    def brand(self):
        """

        :return:
        """

        return self._brand

    @brand.setter
    def brand(self, value):
        """
        Return comma-separated list of brands.
        """

        if self.json.get('campaignBrandSet'):
            brand_temp = []
            for brand in self.json.get('campaignBrandSet'):
                brand_temp.append(brand.get('brand').get('text'))
            self._brand = ', '.join(brand_temp)
        else:
            self._brand = None

    class BlockSet(object):
        """
        .. _block_set:

        Each web location described in the set of watchlist indicators associated with a Threat ID has a series of description fields meant to provide detail about the nature of that indicator. Each of these corresponds to a finite set of possible entries at any given time.
        """

        def __init__(self, block_set):
            """
            Initialize BlockSet object.

            :param str block_set: The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.Malware.BlockSet` object.
            """

            # Each of the items with a return value of None is handled by a property and setter.
            self.json = block_set
            """
            The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.Malware.BlockSet` object.

            :return: String representation of this object.
            :rtype: str
            """

            self.block_type = self.json.get('blockType')
            """
            The data type of the IOC contained in this object.

            :return: One of [Domain Name, Email, IPv4 Address, URL].
            :rtype: str
            """

            self.impact = self.json.get('impact')
            """
            .. _block_set_impact:
            
            Imparts the risk presented by communication with this indicator. These values are borrowed from the STIX v1 Impact Rating Vocabulary, but their application is enhanced by the following guidelines used by PhishMe Intelligence analysts:

            ========    ==========
            Value       Guideline
            ========    ==========
            Major       Indicates a location owned or maintained by a criminal, specifically for malware operations. Interaction with these indicators 1) provides malware to an endpoint, 2) provides direct support to existing malware on endpoint (updates including additional malware, configuration data for existing malware, command and control communications, ex-filtration of victim data), 3) may also be applied to Domains, IPv4s, or URLs whose sole purpose is to support infections.
            Moderate    Indicates a location used by the criminal, but not owned by them (but possibly maintained) and does not exist solely to support malware infections. This may include compromised domains or locations which are used by malware but do not provide any direct support.
            Minor       Indicates a location in a neighborhood of content supporting malware infections while not directly related to malicious content. Typically, they include a significant amount of benign content. For example, an IPv4 which hosts multiple domains or URLs of which only a subset is malicious.
            None        Indicates communication to a non-malicious location, but is contacted by malware to determine internet connectivity or its public IPv4 address, etc.
            ========    ==========

            :return: One of [Major, Moderate, Minor, None].
            :rtype: str
            """

            self.role = self.json.get('role')
            """
            .. _block_set_role:
            
            Used to classify how the location is used by malware. Possible values for this field and their meanings are presented in the table below. Note: this is not a closed set, so new values may be added by PhishMe analysts at any time:

            ======== ===========
            Value    Description
            ======== ===========
            C2	     Command and control used by malware.
            IDinfo	 3rd party location used by malware to identify the IP address of the infected machine.
            InfURL	 URL provided in email as means for infection.
            Payload	 Location from which a payload is obtained.
            PaySite	 Cryptographic ransomware extortion site.
            ======== ===========

            :return: One of the Values from the table above, but subject to additions at any time.
            :rtype: str
            """

            self.role_description = self.json.get('roleDescription')
            """
            .. _block_set_role_description:
            
            Further description about what the Infrastructure Type means. Possible values for this field are presented in the table below. Note: this is not a closed set, so new values may be added by PhishMe analysts at any time.
            
            ======  ===========
            Value   Description
            ======  ===========
            Comp    Location compromised for use as C2.
            Comp    Location compromised for distributing payload.
            Comp    Compromised.
            Exfil   Command and control host to which victim information is shared by the malware.
            I2P     Location hosted within Invisible Internet Protocol network.
            Loader  A C2 dedicated to providing payload files.
            Redir   Redirector location.
            STUN    Host which responds to STUN protocol requests.
            Upd     Update server or standard C2.
            ======  ===========

            :return: One of the Values from the table above, but subject to additions at any time.
            :rtype: str
            """

            self.malware_family = None
            """
            Malware family name.

            :return: Malware family name.
            :rtype: str
            """

            self.malware_family_description = None
            """
            Primary function of this malware family.

            :return: Primary function of this malware family.
            :rtype: str
            """

            self.watchlist_ioc = None
            """
            The IOC represented by this object. This will be one of the following:
            
            1. A domain name indicator of compromise. Note: This category contains both second-level domains and fully 
               qualified domains (FQDN). Where applicable, our analysts add an entry for both the FQDN and the 
               second-level domain name. In some cases, the second-level domain may receive a lesser Impact Rating.
               
            2. An email address used for data exfiltration. Typically, this will be found associated with a keylogger 
               type malware.
            
            3. An IPv4 indicator of compromise.
            
            4. An URL Indicator of compromise

            :return: A malicious IOC.
            :rtype: str
            """

            self.watchlist_ioc_host = None
            """
            If :func:`phishme_intelligence.core.intelligence.Malware.BlockSet.block_type` == URL, then this field is the hostname extracted from :func:`phishme_intelligence.core.intelligence.Malware.BlockSet.watchlist_ioc`, else None.

            :return: The host portion of a URI or None.
            :rtype: str
            """

            self.watchlist_ioc_path = None
            """
            If :func:`phishme_intelligence.core.intelligence.Malware.BlockSet.block_type` == URL, then this field is the path extracted from :func:`phishme_intelligence.core.intelligence.Malware.BlockSet.watchlist_ioc`, else None.

            :return: The path portion of a URI or None.
            :rtype: str
            """


        @property
        def malware_family(self):
            """
            :rtype: str or None
            """

            return self._malware_family

        @malware_family.setter
        def malware_family(self, value):
            """
            :param value:
            :return: None
            """

            try:
                self._malware_family = self.json.get('malwareFamily').get('familyName')
            except AttributeError as exception:
                self._malware_family = None

        @property
        def malware_family_description(self):
            """
            :return: str or None
            """

            return self._malware_family_description

        @malware_family_description.setter
        def malware_family_description(self, value):
            """
            :param value:
            :return: None
            """

            try:
                self._malware_family_description = self.json.get('malwareFamily').get('description')
            except AttributeError as exception:
                self._malware_family_description = None

        @property
        def watchlist_ioc(self):
            """
            :return: str
            """

            return self._watchlist_ioc

        @watchlist_ioc.setter
        def watchlist_ioc(self, value):
            """

            :param value:
            :return: None
            """

            if self.block_type == 'URL':
                self._watchlist_ioc = self.json.get('data_1').get('url')
            else:
                self._watchlist_ioc = self.json.get('data_1')

        @property
        def watchlist_ioc_host(self):
            """
            :return: str or None
            """

            return self._watchlist_ioc_host

        @watchlist_ioc_host.setter
        def watchlist_ioc_host(self, value):
            """

            :param value:
            :return: None
            """

            if self.block_type == 'URL':
                self._watchlist_ioc_host = self.json.get('data_1').get('host')
            else:
                self._watchlist_ioc_host = None

        @property
        def watchlist_ioc_path(self):
            """
            :return: str or None
            """

            return self._watchlist_ioc_path

        @watchlist_ioc_path.setter
        def watchlist_ioc_path(self, value):
            """

            :param value:
            :return: None
            """

            if self.block_type == 'URL':
                self._watchlist_ioc_path = self.json.get('data_1').get('path')
            else:
                self._watchlist_ioc_path = None

    class DomainSet(object):
        """
        .. _domain_set:

        This is the domain name of the sending address or the TO: field. These are highly likely to be spoofed and should not be relied on as the true sender.
        """

        def __init__(self, domain_set):
            """
            Initialize DomainSet object.
            """

            # Each of the items with a return value of None is handled by a property and setter.
            self.json = domain_set
            """
            The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.Malware.DomainSet` object.

            :return: String representation of this object.
            :rtype: str
            """

            self.domain = self.json.get('domain')
            """
            Sender domain name.

            :return: Sender domain name.
            :rtype: str
            """

            self.total_count = self.json.get('totalCount')
            """
            Count of the instances of the sender domain name named above.

            :return: The number of times this item was observed.
            :rtype: int
            """

    class ExecutableSet(object):
        """
        .. _executable_set:

        These are all the files placed on an endpoint during the course of a malware infection.
        """

        def __init__(self, executable_set):
            """
            Initialize ExecutableSet object
            """

            # Each of the items with a return value of None is handled by a property and setter.
            self.json = executable_set
            """
            The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.Malware.ExecutableSet` object.

            :return: String representation of this object.
            :rtype: str
            """

            self.file_name = executable_set.get('fileName')
            """
            The file name of any file discovered during a malware infection.

            :return: File name.
            :rtype: str
            """

            self.type = executable_set.get('type')
            """
            Describes the means by which the malware artifact was introduced to the infected environment. Note: this is not a closed set, so new items may be added at any time.

            :return: Vector of introduction.
            :rtype: str
            """

            self.md5 = executable_set.get('md5Hex')
            """
            The MD5 hash of the file in this object.

            :return: MD5 hash.
            :rtype: str
            """

            self.sha1 = executable_set.get('sha1Hex')
            """
            The SHA-1 hash of the file in this object.

            :return: SHA-1 hash.
            :rtype: str
            """

            self.sha224 = executable_set.get('sha224Hex')
            """
            The SHA-224 hash of the file in this object.

            :return: SHA-224 hash.
            :rtype: str
            """

            self.sha256 = executable_set.get('sha256Hex')
            """
            The SHA-256 hash of the file in this object.

            :return: SHA-256 hash.
            :rtype: str
            """

            self.sha384 = executable_set.get('sha384Hex')
            """
            The SHA-384 hash of the file in this object.

            :return: SHA-384 hash.
            :rtype: str
            """

            self.sha512 = executable_set.get('sha512Hex')
            """
            The SHA-512 hash of the file in this object.

            :return: SHA-512 hash.
            :rtype: str
            """

            self.ssdeep = executable_set.get('ssdeep')
            """
            The `ssdeep <http://ssdeep.sourceforge.net>`_ hash of the file in this object.

            :return: ssdeep hash.
            :rtype: str
            """

            self.malware_family = None
            """
            Malware family name.

            :return: Malware family name.
            :rtype: str or None
            """

            self.malware_family_description = None
            """
            Primary function of this malware family.

            :return: Primary function of this malware family.
            :rtype: str or None
            """

            self.subtype = None
            """
            Additional context for purpose of the infected binary within infected endpoint.

            :return: Purpose of infected binary.
            :rtype: str or None
            """
            self.severity = None
            """
            Impact Rating associated with this malware file
            
            :return: Impact Rating value
            :rtype: str
            """
            # Implement at a later date.
            # self.confidence = None

        @property
        def severity(self):
            """

            :param self:
            :return:
            """

            return self._severity

        @severity.setter
        def severity(self, value):
            """

            :param self:
            :return:
            """

            try:
                self._severity = self.json.get('severityLevel')
            except AttributeError as exception:
                self._severity = 'Major'

        @property
        def subtype(self):
            """
            :rtype: str or None
            """

            return self._subtype

        @subtype.setter
        def subtype(self, value):
            """
            :param value:
            :return: None
            """

            try:
                self._subtype = self.json.get('executableSubtype').get('description')
            except AttributeError as exception:
                self._subtype = None

        @property
        def malware_family(self):
            """
            :rtype: str or None
            """

            return self._malware_family

        @malware_family.setter
        def malware_family(self, value):
            """
            :param value:
            :return: None
            """

            try:
                self._malware_family = self.json.get('malwareFamily').get('familyName')
            except AttributeError as exception:
                self._malware_family = None

        @property
        def malware_family_description(self):
            """
            :rtype: str or None
            """

            return self._malware_family_description

        @malware_family_description.setter
        def malware_family_description(self, value):
            """
            :param value:
            :return: None
            """

            try:
                self._malware_family_description = self.json.get('malwareFamily').get('description')
            except AttributeError as exception:
                self._malware_family_description = None

    class SubjectSet(object):
        """
        .. _sender_subject_set:

        This is the subject line of all malicious emails determined to be part of this campaign.
        """

        def __init__(self, subject_set):
            """
            Initialize SubjectSet object
            """

            # Each of the items with a return value of None is handled by a property and setter.
            self.json = subject_set
            """
            The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.Malware.SubjectSet` object.

            :return: String representation of this object.
            :rtype: str
            """

            self.subject = self.json.get('subject')
            """
            Email subject line.

            :return: Email subject line.
            :rtype: str
            """

            self.total_count = self.json.get('totalCount')
            """
            Count of the instances of email subject line within this campaign.

            :return: A count.
            :rtype: int
            """

    class SenderIPSet(object):
        """
        .. _sender_ip_set:

        These are the IP addresses being used to deliver the mail. Due to the nature of mail headers, some of these IPs may be spoofed.
        """

        def __init__(self, sender_ip_set):
            """
            Initialize SenderIPSet object
            """

            # Each of the items with a return value of None is handled by a property and setter.
            self.json = sender_ip_set
            """
            The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.Malware.SenderIPSet` object.

            :return: String representation of this object.
            :rtype: str
            """

            self.ip = sender_ip_set.get('ip')
            """
            One of possibly many IPs used in the delivery of the email.

            :return: An IPv4 address.
            :rtype: str
            """

            self.total_count = sender_ip_set.get('totalCount')
            """
            Count of the instances of a email delivery IP within this campaign.

            :return: A count.
            :rtype: int
            """

    class SenderEmailSet(object):
        """
        .. _sender_email_set:

        These are the email addresses being used to deliver the mail. Due to the nature of mail headers, some of these email addresses may be spoofed.
        """

        def __init__(self, sender_email_set):
            """
            Initialize SenderEmailSet object
            """

            # Each of the items with a return value of None is handled by a property and setter.
            self.json = sender_email_set
            """
            The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.Malware.SenderEmailSet` object.

            :return: String representation of this object.
            :rtype: str
            """

            self.sender_email = sender_email_set.get('senderEmail')
            """
            The possibly spoofed email address used in the delivery of the email.

            :return: An email address.
            :rtype: str
            """

            self.total_count = sender_email_set.get('totalCount')
            """
            Count of the possibly spoofed email addresses within this campaign.

            :return: A count.
            :rtype: int
            """

    class SpamURLSet(object):
        """
        Spam URLs (if any) associated with a particular campaign.
        """

        def __init__(self, spam_url_set):
            """
            Initialize SpamURLSet object.
            """

            # Each of the items with a return value of None is handled by a property and setter.
            self.json = spam_url_set
            """
            The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.Malware.SpamURLSet` object.

            :return: String representation of this object.
            :rtype: str
            """

            self.url = URL(self.json.get('url_1'))
            """
            Spam URL associated with a particular campaign.

            :return: A URI.
            :rtype: str
            """

            self.total_count = self.json.get('totalCount')
            """
            Count of the instances of this item within this campaign.

            :return: A count.
            :rtype: int
            """


class IPv4(object):
    """

    """

    def __init__(self, ipv4):
        """
        Initialize IPv4 object.
        """
        if ipv4:
            self.json = ipv4
            """
            The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.IPv4` object.

            :return: String representation of this object.
            :rtype: str
            """

            self.asn = ipv4.getint('asn')
            """
            The number which refers to a network operator of the IP address associated with this Watchlist item at time of publishing this information.

            :return: The AS number.
            :rtype: int
            """

            self.asn_organization = ipv4.get('asnOrganization')
            """
            The long form name of the organization responsible for this ASN.

            :return: The organization name.
            :rtype: str
            """

            self.continent_code = ipv4.get('continentCode')
            """
            Two-letter continent code. Watch out for 'AQ'.

            :return: The continent code.
            :rtype: str
            """

            self.continent_name = ipv4.get('continentName')
            """
            Continent name.

            :return: Continent name.
            :rtype: str
            """

            self.country_iso_code = ipv4.get('countryIsoCode')
            """
            `Two-letter country code. <http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Current_codes>`_

            :return: Two-letter country code.
            :rtype: str
            """

            self.country_name = ipv4.get('countryName')
            """
            Country name.

            :return: Country name.
            :rtype: str
            """

            self.ip = ipv4.get('ip')
            """
            The IP address associated with this object.

            :return: IPv4 address.
            :rtype: str
            """

            self.isp = ipv4.get('isp')
            """
            Internet Service Provider (ISP) for this object.

            :return: Name of ISP.
            :rtype: str
            """

            self.latitude = ipv4.get('latitude')
            """
            Latitude of ISP.

            :return: latitude
            :rtype: str
            """

            self.longitude = ipv4.get('longitude')
            """
            Longitude of ISP.

            :return: longitude
            :rtype: str
            """

            self.lookup_on = ipv4.get('lookupOn')
            """
            The timestamp when ASN information was retrieved about this.

            :return: Epoch timestamp.
            :rtype: int
            """

            self.metro_code = ipv4.get('metroCode')
            """
            Telephone metro code.

            :return: Telephone metro code.
            :rtype: int
            """

            self.organization = ipv4.get('organization')
            """
            The short form name of the organization responsible for this ASN.

            :return: The organization name.
            :rtype: str
            """

            self.postal_code = ipv4.get('postalCode')
            """
            Postal or zip code.

            :return: Postal or zip code.
            :rtype: str
            """

            self.subdivision_name = ipv4.get('subdivisionName')
            """
            State name.

            :return: State name.
            :rtype: str
            """

            self.subdivision_iso_code = ipv4.get('subdivisionIsoCode')
            """
            Two-letter state code.

            :return: State code.
            :rtype: str
            """

            self.time_zone = ipv4.get('timeZone')
            """
            Time zone.

            :return: Time zone.
            :rtype: str
            """

            self.user_type = ipv4.get('userType')
            """
            Type of user.

            :return: Type of user.
            :rtype: str
            """

    def __getattr__(self, item):
        return None


class URL(object):
    """

    """

    def __init__(self, url):
        """
        Initialize URL object.
        """

        self.json = url
        """
        The raw JSON used to create the :class:`phishme_intelligence.core.intelligence.URL` object.

        :return: String representation of this object
        :rtype: str
        """

        self.domain = url.get('domain')
        """
        The domain name part of the URI

        :return: URI domain
        :rtype: str
        """

        self.host = url.get('host')
        """
        The FQDN portion of the URI.

        :return: URI host.
        :rtype: str
        """

        self.path = url.get('path')
        """
        The portion of the URL following the domain name.

        :return: URI path.
        :rtype: str
        """

        self.protocol = url.get('protocol')
        """
        The TCP/IP protocol portion of a URI.

        :return: URI protocol.
        :rtype: str
        """

        self.query = url.get('query')
        """
        The portion of a URI after a '?' symbol.

        :return: URI query.
        :rtype: str
        """

        self.url = url.get('url')
        """
        The full URI.

        :return: URI.
        :rtype: str
        """

    def __getattr__(self, item):
            return None
