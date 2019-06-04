from __future__ import print_function
import pan.xapi
import sys
import xmltodict


class Panorama:
    """Class for interacting with Panorama"""

    def __init__(self, hostname, username, password, DEBUG=False):
        self.DEBUG = DEBUG
        self.xpaths = self._get_xpaths()
        self.api = self._login(hostname, username, password)
        self.address_types = ['ip-netmask', 'ip-range', 'fqdn']
        self.shared_address = None
        self.shared_address_groups = None
        self.shared_tags = None
        self.colors = self._colors()

    @staticmethod
    def _get_xpaths():
        xpaths = {}
        xpaths['shared'] = {}
        xpaths['shared']['all'] = "/config/shared/"
        xpaths['shared']['address'] = "/config/shared/address"
        xpaths['shared']['address-groups'] = "/config/shared/address-group"
        xpaths['shared']['tags'] = "/config/shared/tag"
        xpaths['device-group'] = "/config/devices/entry[@name='localhost.localdomain']/device-group"
        xpaths['template'] = "/config/devices/entry[@name='localhost.localdomain']/template"
        xpaths['template-stack'] = "/config/devices/entry[@name='localhost.localdomain']/template-stack"
        return xpaths

    @staticmethod
    def _login(hostname, username, password):
        """
        :param hostname: Panorama hostname or IP
        :param username: username to login to Panorama
        :param password: password to login to Panorama
        :return: API Client
        """
        try:
            pan_api = pan.xapi.PanXapi(
                api_username=username,
                api_password=password,
                hostname=hostname
            )
            return pan_api
        except pan.xapi.PanXapiError as msg:
            print('pan.xapi.PanXapi:', msg)
            sys.exit(1)

    @staticmethod
    def _colors():
        colors = {
            'red': 'color1',
            'green': 'color2',
            'blue': 'color3',
            'yellow': 'color4',
            'copper': 'color5',
            'orange': 'color6',
            'purple': 'color7',
            'gray': 'color8',
            'light green': 'color9',
            'cyan': 'color10',
            'light gray': 'color11',
            'blue gray': 'color12',
            'lime': 'color13',
            'black': 'color14',
            'gold': 'color15',
            'brown': 'color16',
            'army green': 'color17'
        }
        return colors

    def _create_tag_element(self, tag):
        """
        Create formatted tag element.  if Tag doesn't exist then create it
        :param tag:
        :return:
        """

        element = ''
        if not self.shared_tags:
            self.shared_tags = self.get_shared_tags()

        if isinstance(tag, list):
            for x in tag:
                valid = False
                for item in self.shared_tags:
                    if x == item['@name']:
                        valid = True
                        break
                if not valid:
                    self.add_shared_tag(tagname=x)
            element += '<tag>'
            for x in tag:
                element += '<member>%s</member>' % x
            element += '</tag>'
        elif isinstance(tag, str):
            valid = False
            for item in self.shared_tags:
                if tag == item['@name']:
                    valid = True
                    break
            if not valid:
                self.add_shared_tag(tagname=tag)
            element += '<tag><member>%s</member></tag>' % tag

        return element

    def get_config_by_xpath(self, xpath):
        """
        Get a specific Panorama configuration using the API path
        Use xpaths object to make xpath selection easier
        :param xpath: The configuration URI path
        :return: Dictionary formatted configuration
        """
        try:
            self.api.get(xpath=xpath)
            result = self.api.xml_result()
            if result:
                return xmltodict.parse(result)
            else:
                return None
        except pan.xapi.PanXapiError as msg:
            print('pan.xapi.PanXapi: ', msg)
            sys.exit(1)

    def get_shared_tags(self):
        """
        Returns a list of Tags form the Shared context
        :return:
        """
        tags = self.get_config_by_xpath(self.xpaths['shared']['tags'])
        return tags['tag']['entry']

    def get_device_group(self, devicegroup):
        """
        Returns the device group configuration in a dictionary
        :param devicegroup: the device group name
        :return:
        """
        if self.DEBUG:
            print("Getting device-group: %s" % devicegroup)

        xpath = "%s/entry[@name='%s']" % (self.xpaths['device-group'], devicegroup)
        config = self.get_config_by_xpath(xpath)
        if config:
            return config['entry']
        else:
            return config

    def get_template(self, template):
        """
        Returns the template configuration in a dictionary
        :param template: the device group name
        :return:
        """
        if self.DEBUG:
            print("Getting template: %s" % template)

        xpath = "%s/entry[@name='%s']" % (self.xpaths['template'], template)
        config = self.get_config_by_xpath(xpath)
        if config:
            return config['entry']
        else:
            return config

    def add_shared_addressgroup(self, groupname, addresses, description=None, tag=None):
        """
        Creates an address group in the Shared context
        :param groupname:
        :param addresses:  A list of addresses to add to the group
        :param description:
        :param tag:
        :return:
        """
        if not isinstance(addresses, list):
            if self.DEBUG:
                print("Addresses must be a list")
            sys.exit(1)

        # Get existing address groups and validate the new group name does not exist
        if not self.shared_address:
            self.shared_address_groups = self.get_config_by_xpath(self.xpaths['shared']['address-groups'])
            for groups in self.shared_address_groups['address-group']['entry']:
                if groupname == groups['@name']:
                    if self.DEBUG:
                        print("Group already exists: ", groupname)
                    return

        # Create the group
        xpath = self.xpaths['shared']['address-groups'] + "/entry[@name='%s']" % groupname
        element = '<static>'
        for address in addresses:
            element = element + '<member>%s</member>' % address
        element = element + '</static>'

        if tag:
            tag_element = self._create_tag_element(tag)
            element += tag_element

        if description:
            element += '<description>%s</description>' % description

        try:
            self.api.set(xpath=xpath, element=element)
            if self.DEBUG:
                print("Group created: ", groupname)
        except pan.xapi.PanXapiError as msg:
            print('pan.xapi.PanXapi: ', msg)

    def add_shared_address(self, addressname, address_type, address, description=None, tag=None):
        """
        Create an address object
        :param name: Address object name: string
        :param address_type: ip-netmask, ip-range, fqdn: string
        :param address: ip address, range or fqdn: string
        :param description: Description of the address object: string
        :param tag: Tag for the address object: string || list of strings
        :return:
        """
        if address_type not in self.address_types:
            if self.DEBUG:
                print("Invalid address type: ", address_type)
            return

        if not self.shared_address:
            self.shared_address = self.get_config_by_xpath(self.xpaths['shared']['address'])

        # validate if the object already exists
        for item in self.shared_address['address']['entry']:
            if addressname == item['@name']:
                if self.DEBUG:
                    print("Address already exists: ", addressname)
                return

        # Create the address object
        xpath = self.xpaths['shared']['address'] + "/entry[@name='%s']" % addressname
        element = "<%s>%s</%s>" % (address_type, address, address_type)

        if tag:
            tag_element = self._create_tag_element(tag)
            element += tag_element

        if description:
            element += '<description>%s</description>' % description

        try:
            self.api.set(xpath=xpath, element=element)
            if self.DEBUG:
                print('Created Address Object: ', addressname)
        except pan.xapi.PanXapiError as msg:
            print('pan.xapi.PanXapi: ', msg)

    def add_shared_tag(self, tagname, comments=None, color=None):
        """
        Create a shared tag.  Use Colors object to easily specify the tag color
        :param tagname:
        :param comments:
        :param color:
        :return:
        """
        if not self.shared_tags:
            self.shared_tags = self.get_shared_tags()

        for item in self.shared_tags:
            if tagname == item['@name']:
                if self.DEBUG:
                    print("Tag already exists: ", tagname)
                return

        # Create the address object
        xpath = self.xpaths['shared']['tags'] + "/entry[@name='%s']" % tagname
        element = ''

        if color:
            if color in self.colors.keys():
                element += "<color>%s</color>" % self.colors[color]

        if comments:
            element += "<comments>%s</comments>" % comments

        if not element:
            element = "<comments></comments>"
        try:
            self.api.set(xpath=xpath, element=element)
            if self.DEBUG:
                print('Created Tag: ', tagname)
        except pan.xapi.PanXapiError as msg:
            print('pan.xapi.PanXapi: ', msg)
