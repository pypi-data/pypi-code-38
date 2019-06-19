from __future__ import unicode_literals, absolute_import
'''
 Copyright 2013-2019 Cofense, Inc.  All rights reserved.

 This software is provided by PhishMe, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
 including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
 disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
 consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
 this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.
'''


class ThreatReport(object):

    def __init__(self, threat_json):

        self.json = threat_json

        self.threat_id = self.json.get('id')

        self.first_published = self.json.get('firstPublished') or self.json.get('firstDate')

        self.last_published = self.json.get('lastPublished') or self.json.get('lastDate')

        self.threat_type = self.json.get('threatType')

        self.human_readable_url = self.json.get('threatDetailURL')

        self.brands = self.json.get('campaignBrandSet') or self.json.get('brands')

    @property
    def brands(self):
        return self._brands

    @brands.setter
    def brands(self, brands):
        brand_names = []
        for brand in brands:
            if brand.get('brand'):
                brand_names.append(brand.get('brand').get('text'))
            elif brand.get('text'):
                brand_names.append(brand.get('text'))
            else:
                brand_names = None

        self._brands = brand_names


class MalwareThreatReport(ThreatReport):
    """
    Malware class holds a single Cofense Intelligence malware object.
    """

    def __init__(self, threat_json):
        super(MalwareThreatReport, self).__init__(threat_json)
        """
        Initialize Malware object.

        :param str malware:
        :param ConfigParser config:
        """

        self.label = self.json.get('label')
        """
        Short summary of the topic, brand, and malware families involved in this ThreatReport ID.

        :return: Summary of the campaign, can be used as a title.
        :rtype: str
        """

        self.executiveSummary = self.json.get('executiveSummary')
        """
        .. deprecated:: 4.0.0

        Use :func:`Cofense_intelligence.core.intelligence.Malware.executive_summary()` instead.

        :return: A summary of this campaign.
        :rtype: str
        """

        self.executive_summary = self.json.get('executiveSummary')
        """
        The executive summary from the Active ThreatReport Report associated with this campaign.

        :return: A summary of this campaign.
        :rtype: str
        """

        self.report_html = 'https://www.threathq.com/apiv1/t3/malware/{}/html'.format(self.threat_id)
        """
        A direct URL accessible with API credentials to a human-readable html document intended to provide a more accessible 
        explanation for the sum of a malware campaign's significance.

        :return: A URL to a Cofense Intelligence Active ThreatReport Report.
        :rtype: str
        """

        self.report_pdf = 'https://www.threathq.com/apiv1/t3/malware/{}/pdf'.format(self.threat_id)
        """
        A direct URL accessible with API credentials to a human-readable pdf document intended to provide a more accessible 
        explanation for the sum of a malware campaign's significance.

        :return: A URL to a Cofense Intelligence Active ThreatReport Report.
        :rtype: str
        """

        self.malware_families = self.json.get('malwareFamilySet')
        """
        A list of all the malware families included in this campaign.

        :return: A list of the malware families.
        :rtype: lst or None
        """

        self.block_set = self.json.get('blockSet')
        """
        .. seealso:: :class:`Cofense_intelligence.core.intelligence.Malware.BlockSet`

        :return: list of :class:`Cofense_intelligence.core.intelligence.Malware.BlockSet`
        :rtype: list
        """

        self.domain_set = self.json.get('domainSet')
        """
        .. seealso:: :class:`Cofense_intelligence.core.intelligence.Malware.DomainSet`

        :return: list of :class:`Cofense_intelligence.core.intelligence.Malware.DomainSet`
        :rtype: list
        """

        self.executable_set = self.json.get('executableSet')
        """
        .. seealso:: :class:`Cofense_intelligence.core.intelligence.Malware.ExecutableSet`

        :return: list of :class:`Cofense_intelligence.core.intelligence.Malware.ExecutableSet`
        :rtype: list
        """

        self.sender_ip_set = self.json.get('senderIpSet')
        """
        .. seealso:: :class:`Cofense_intelligence.core.intelligence.Malware.SenderIPSet`

        :return: list of :class:`Cofense_intelligence.core.intelligence.Malware.SenderIPSet`
        :rtype: list
        """

        self.spam_url_set = self.json.get('spamUrlSet')
        """
        .. seealso:: :class:`Cofense_intelligence.core.intelligence.Malware.SpamURLSet`

        :return: list of :class:`Cofense_intelligence.core.intelligence.Malware.SpamURLSet`
        :rtype: list
        """

        self.subject_set = self.json.get('subjectSet')
        """
        .. seealso:: :class:`Cofense_intelligence.core.intelligence.Malware.SubjectSet`

        :return: list of :class:`Cofense_intelligence.core.intelligence.Malware.SubjectSet`
        :rtype: list
        """

        self.sender_email_set = self.json.get('senderEmailSet')
        """
        .. seealso:: :class:`Cofense_intelligence.core.intelligence.Malware.SenderEmailSet`

        :return: list of :class:`Cofense_intelligence.core.intelligence.Malware.SenderEmailSet`
        :rtype: list
        """

    @property
    def malware_families(self):
        """
        :rtype: str
        """

        return self._malware_families

    @malware_families.setter
    def malware_families(self, family_json):
        """
        :param family_json:
        :return: None
        """
        if family_json:
            self._malware_families = [family.get('familyName') for family in family_json]
        else:
            self._malware_families = None

    @property
    def block_set(self):
        """
        :rtype: list of :class:`Cofense_intelligence.core.intelligence.Malware.BlockSet`
        """

        return self._block_set

    @block_set.setter
    def block_set(self, block_set_json):
        """
        :param block_set_json:
        :return: None
        """

        self._block_set = [self.BlockSet(item) for item in block_set_json]

    @property
    def domain_set(self):
        """
        :rtype: list of :class:`Cofense_intelligence.core.intelligence.Malware.DomainSet`
        """

        return self._domain_set

    @domain_set.setter
    def domain_set(self, domain_set_json):
        """

        :param domain_set_json:
        :return: None
        """

        self._domain_set = [self.DomainSet(item) for item in domain_set_json]

    @property
    def executable_set(self):
        """
        :rtype: list of :class:`Cofense_intelligence.core.intelligence.Malware.ExecutableSet`
        """

        return self._executable_set

    @executable_set.setter
    def executable_set(self, exec_set_json):
        """

        :param exec_set_json:
        :return:
        """

        self._executable_set = [self.ExecutableSet(item) for item in exec_set_json]

    @property
    def sender_ip_set(self):
        """
        :rtype: list of :class:`Cofense_intelligence.core.intelligence.Malware.SenderIPSet`
        """

        return self._sender_ip_set

    @sender_ip_set.setter
    def sender_ip_set(self, sender_ip_json):
        """

        :param sender_ip_json:
        :return:
        """
        self._sender_ip_set = [self.SenderIPSet(item) for item in sender_ip_json]

    @property
    def sender_email_set(self):
        """
        :rtype: list of :class:`Cofense_intelligence.core.intelligence.Malware.SenderEmailSet`
        """

        return self._sender_email_set

    @sender_email_set.setter
    def sender_email_set(self, sender_email_json):
        """

        :param sender_email_json:
        :return:
        """
        self._sender_email_set = [self.SenderEmailSet(item) for item in sender_email_json]

    @property
    def subject_set(self):
        """
        :rtype: list of :class:`Cofense_intelligence.core.intelligence.Malware.SubjectSet`
        """

        return self._subject_set

    @subject_set.setter
    def subject_set(self, subject_json):
        """

        :param subject_json:
        :return: None
        """
        self._subject_set = [self.SubjectSet(item) for item in subject_json]

    @property
    def spam_url_set(self):
        """
        :rtype: list of :class:`Cofense_intelligence.core.intelligence.Malware.SpamURLSet`
        """

        return self._spam_url_set

    @spam_url_set.setter
    def spam_url_set(self, spam_url_json):
        """

        :param spam_url_json:
        :return: None
        """
        self._spam_url_set = [self.SpamURLSet(item) for item in spam_url_json]

    class BlockSet(object):
        """
        .. _block_set:

        Each web location described in the set of watchlist indicators associated with a ThreatReport ID has a series of description fields meant to provide detail about the nature of that indicator. Each of these corresponds to a finite set of possible entries at any given time.
        """

        def __init__(self, block_set):
            """
            Initialize BlockSet object.

            :param dict block_set: The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.Malware.BlockSet` object.
            """

            # Each of the items with a return value of None is handled by a property and setter.
            self.json = block_set
            """
            The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.Malware.BlockSet` object.

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
            
            Imparts the risk presented by communication with this indicator. These values are borrowed from the STIX v1 Impact Rating Vocabulary, but their application is enhanced by the following guidelines used by Cofense Intelligence analysts:

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
            
            Used to classify how the location is used by malware. Possible values for this field and their meanings are presented in the table below. Note: this is not a closed set, so new values may be added by Cofense analysts at any time:

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
            
            Further description about what the Infrastructure Type means. Possible values for this field are presented in the table below. Note: this is not a closed set, so new values may be added by Cofense analysts at any time.
            
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

            self.malware_family = self.json.get('malwareFamily')
            """
            Malware family name.

            :return: Malware family name.
            :rtype: str
            """

            self.malware_family_description = self.json.get('malwareFamily')
            """
            Primary function of this malware family.

            :return: Primary function of this malware family.
            :rtype: str
            """

            if self.block_type == 'URL':
                data_1 = self.json.get('data_1')
                if data_1:
                    self.watchlist_ioc = data_1.get('url')
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

                self.watchlist_ioc_host = data_1.get('host')
                """
                If :func:`Cofense_intelligence.core.intelligence.Malware.BlockSet.block_type` == URL, then this field is the hostname extracted from :func:`Cofense_intelligence.core.intelligence.Malware.BlockSet.watchlist_ioc`, else None.
                
                :return: The host portion of a URI or None.
                :rtype: str
                """

                self.watchlist_ioc_path = data_1.get('path')
                """
                If :func:`Cofense_intelligence.core.intelligence.Malware.BlockSet.block_type` == URL, then this field is the path extracted from :func:`Cofense_intelligence.core.intelligence.Malware.BlockSet.watchlist_ioc`, else None.

                :return: The path portion of a URI or None.
                :rtype: str
                """

            else:
                self.watchlist_ioc = self.json.get('data_1')
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

        @property
        def malware_family(self):
            """
            :rtype: str or None
            """

            return self._malware_family

        @malware_family.setter
        def malware_family(self, malware_family_json):
            """
            :param malware_family_json:
            :return: None
            """
            if malware_family_json:
                self._malware_family = malware_family_json.get('familyName')
            else:
                self._malware_family = None

        @property
        def malware_family_description(self):
            """
            :return: str or None
            """

            return self._malware_family_description

        @malware_family_description.setter
        def malware_family_description(self, malware_family_json):
            """
            :param malware_family_json:
            :return: None
            """
            if malware_family_json:
                self._malware_family_description = malware_family_json.get('description')
            else:
                self._malware_family_description = None

        @property
        def watchlist_ioc(self):
            """
            :return: str
            """

            return self._watchlist_ioc

        @watchlist_ioc.setter
        def watchlist_ioc(self, ioc):
            """

            :param ioc:
            :return: None
            """
            self._watchlist_ioc = ioc

        @property
        def watchlist_ioc_host(self):
            """
            :return: str or None
            """

            return self._watchlist_ioc_host

        @watchlist_ioc_host.setter
        def watchlist_ioc_host(self, host):
            """

            :param host:
            :return: None
            """
            self._watchlist_ioc_host = host

        @property
        def watchlist_ioc_path(self):
            """
            :return: str or None
            """

            return self._watchlist_ioc_path

        @watchlist_ioc_path.setter
        def watchlist_ioc_path(self, path):
            """

            :param path:
            :return: None
            """
            self._watchlist_ioc_path = path

    # TODO: refactor to have one corralory indicator set class
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
            The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.Malware.DomainSet` object.

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
            The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.Malware.ExecutableSet` object.

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

            try:
                self.malware_family = self.json.get('malwareFamily').get('familyName') or None
            except AttributeError:
                self.malware_family = None

            try:
                self.malware_family_description = self.json.get('malwareFamily').get('description')
            except AttributeError:
                self.malware_family_description = None

            try:
                self.subtype = self.json.get('executableSubtype').get('description')
            except AttributeError:
                self.subtype = None

            self.severity = self.json.get('severityLevel') or 'Major'
            # TODO: confidence

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
            The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.Malware.SubjectSet` object.

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
            The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.Malware.SenderIPSet` object.

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
            The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.Malware.SenderEmailSet` object.

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
            The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.Malware.SpamURLSet` object.

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


class PhishThreatReport(ThreatReport):
    """
    Phish class holds a single Cofense Brand Intelligence object.
    """

    def __init__(self, threat_json):
        """
        Initialize a Cofense Brand Intelligence object.

        :param dict threat_json:
        """

        super(PhishThreatReport, self).__init__(threat_json)

        self.confirmed_date = self.json.get('confirmedDate')
        """
        The time when the threat_json was confirmed as being a phishing threat.
        
        :return: A timestamp in epoch milliseconds.
        :rtype: int
        """

        self.web_components = self.json.get('webComponents')
        """
        .. _web_components:
        
        These are the web components used to build a phishing website within a victim's browser. This collection of 
        files can include files like javascript, cascading style sheets, or images hosted by the legitimate website of 
        the targeted brand. These cases are excellent opportunities for the targeted brand to retrieve referral logs 
        which will reveal the victim's IP as they access a phishing site. Criminals may choose to reference these files 
        hosted by the legitimate website for simplicity or to keep the look and feel of their phishing site equivalent 
        to the legitimate site they're imitating. These files are downloadable as a single encrypted archive.
        
        :return: list of web components as dictionary value 
        :rtype: list of dicts
        """

        self.kits = self.json.get('kits')
        """
        .. _kits:
        .. _kit_files:
        
        These are the phishing kits retrieved during our processing of a phishing site. These kits are downloadable 
        from ThreatHQ as a single encrypted archive. 
        
        Within this data is alsoEmail addresses found within a phishing kit. These are typically drop email addresses, 
        but may include any email addresses found within the body of the phishing kit. Reasons for the presence of a 
        non-drop email address include contact info for the phishing kit creator, contact info for the author of a 
        particular script within the phishing site, or the spoofed "from" email address that will be used to create the 
        email to the criminal. 
        
        :return: list of web components as dictionary value 
        :rtype: list of dicts
        """

        self.title = self.json.get('title')
        """
        The text from the raw HTML used to display the phishing URL, typically found within the <title> </title> tags. 
        This is the text displayed by a browser at the top of the browser or tab.
        
        :return: The title text
        :rtype: str
        """

        self.language = self.json.get('language')
        """
        The primary language used in the visible portions of the phishing site, as determined by an NLP library.
        
        :return: The language details about the phishing threat
        :rtype: dict
        """
        self.reported_url_list = self.json.get('reportedURLs_1')
        """
        .. _reported_urls:
        
        List of reported URLs. These are the original URLs reported to Cofense. They might be the same as the Phishing 
        URL or they might be a re-director of some type, either a compromised site or a shortened URL like bit.ly or 
        tinyurl. 
        
        :return: list of :class:`Cofense_intelligence.core.brand_intelligence.URL`
        :rtype: list
        """

        self.phish_url = self.json.get('phishingURL_1')
        """
        .. _phish_urls:
        
        These components represent the current location of a phishing page, whether hosted on a compromised website or 
        a domain specifically registered for phishing purposes.
        
        :return: :class:`Cofense_intelligence.core.brand_intelligence.URL`
        :rtype: :class:`Cofense_intelligence.core.brand_intelligence.URL` or None
        """

        self.action_url_list = self.json.get('actionURLs_1')
        """
        .. _action_urls:
         
        This is the next URL to be called when the victim submits their information to the phishing site. It might lead 
        directly to a second page of the phishing site, it might be an intermediate PHP script that submits credentials 
        to the criminal, it might lead to an exit URL, or it may be some combination of these things. Note: each page of 
        a phishing attack will have an action URL, Cofense is only capturing the Action URL for the first page.
        
        :return: list of :class:`Cofense_intelligence.core.brand_intelligence.URL`
        :rtype: list
        """

        self.screenshot_url = None
        """
        A screenshot captured of the phishing URL. If you were to visit the phishing URL directly, you should expect 
        the same visual experience as you see in this screenshot.       
        
        :return: :class:`Cofense_intelligence.core.brand_intelligence.URL`
        :rtype: :class:`Cofense_intelligence.core.brand_intelligence.URL` or None
        """

        self.ip = self.json.get('ipDetail')
        """
        Information about the IP address associated with the phishing URL 
        
        :return: :class:`Cofense_intelligence.core.brand_intelligence.IPv4`
        :rtype: :class:`Cofense_intelligence.core.brand_intelligence.IPv4` or None
        """

    @property
    def kits(self):
        """

        :return:
        """

        return self._kits

    @kits.setter
    def kits(self, kts):
        """

        :param kts:
        :return:
        """
        if kts:
            self._kits = [self.Kit(kt) for kt in kts]
        else:
            self._kits = []

    @property
    def ip(self):
        """

        :return:
        """
        return self._ip

    @ip.setter
    def ip(self, ip_detail):
        """

        :param ip_detail:
        :return:
        """
        if ip_detail:
            self._ip = IPv4(ip_detail)
        else:
            self._ip = None

    @property
    def phish_url(self):
        """

        :return:
        """

        return self._phish_url

    @phish_url.setter
    def phish_url(self, phish_urls):
        """

        :param phish_urls:
        :return:
        """
        if phish_urls:
            self._phish_url = URL(phish_urls)
        else:
            self._phish_url = None

    @property
    def screenshot_url(self):
        """

        :return:
        """
        return self._screenshot_url

    @screenshot_url.setter
    def screenshot_url(self, value):
        """

        :param screenshot_url_data:
        :return:
        """
        try:
            self._screenshot_url = URL(self.json.get('screenshot').get('url_1')).url
        except AttributeError:
            self._screenshot_url = None

    @property
    def reported_url_list(self):
        """

        :return:
        """

        return self._reported_url_list

    @reported_url_list.setter
    def reported_url_list(self, reported_urls):
        """

        :param reported_urls:
        :return:
        """
        self._reported_url_list = [URL(item) for item in reported_urls]

    @property
    def action_url_list(self):
        """

        :return:
        """

        return self._action_url_list

    @action_url_list.setter
    def action_url_list(self, action_urls):
        """

        :param action_urls:
        :return:
        """
        self._action_url_list = [URL(item) for item in action_urls]

    class Kit(object):
        """
        Kit
        """

        def __init__(self, kit):
            """
            Initialize kit object.
            """

            self.json = kit
            self.kit_name = kit.get('kitName')
            self.size = kit.get('fileSize')
            self.md5 = kit.get('md5')
            self.sha1 = kit.get('sha1')
            self.sha224 = kit.get('sha224')
            self.sha256 = kit.get('sha256')
            self.sha384 = kit.get('sha384')
            self.sha512 = kit.get('sha512')
            self.ssdeep = kit.get('ssdeep')
            self.kit_files = None

        @property
        def kit_files(self):
            """

            :return:
            """

            return self._kit_files

        @kit_files.setter
        def kit_files(self, value):
            """

            :param value:
            :return:
            """

            return_list = []

            for item in self.json.get('files'):
                return_list.append(self.KitFile(item))

            self._kit_files = return_list

        class KitFile(object):
            """
            KitFile object.
            """

            def __init__(self, kit_file):
                """
                Initialize kit file.
                """

                self.json = kit_file
                self.file_name = kit_file.get('fileName')
                self.size = kit_file.get('size')
                self.path = kit_file.get('path')
                self.md5 = kit_file.get('md5')
                self.sha1 = kit_file.get('sha1')
                self.sha224 = kit_file.get('sha224')
                self.sha256 = kit_file.get('sha256')
                self.sha384 = kit_file.get('sha384')
                self.sha512 = kit_file.get('sha512')
                self.ssdeep = kit_file.get('ssdeep')
                self.observed_emails = None

            @property
            def observed_emails(self):
                """

                :return:
                """

                return self._emails

            @observed_emails.setter
            def observed_emails(self, value):
                """

                :param value:
                :return:
                """

                return_list = []

                for item in self.json.get('emails'):
                    return_list.append(self.Email(item))

                self._emails = return_list

            class Email(object):
                """
                Email object.
                """

                def __init__(self, observed_email):
                    """
                    Initialize email.
                    :return:
                    """

                    self.json = observed_email
                    self.email_address = observed_email.get('email')
                    self.obfuscation_type = observed_email.get('obfuscationType')


class IPv4(object):

    def __init__(self, ipv4):
        """
    Initialize IPv4 object.
    """
        self.json = ipv4
        """
    The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.IPv4` object.
    
    :return: String representation of this object.
    :rtype: str
    """

        self.asn = ipv4.get('asn')
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

    def __init__(self, url):
        """
    Initialize URL object.
    """

        self.json = url
        """
    The raw JSON used to create the :class:`Cofense_intelligence.core.intelligence.URL` object.
    
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
