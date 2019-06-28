#!/usr/bin/env python
import time
import random
import logging
import ipaddress
from shutil import copyfile
import os
import re
import binascii

from configs import *
from csr_cloud.csr_cloud import csr_cloud as cloud

try:
    import cli
    guestshell = True
except IOError:
    guestshell = False
except ImportError:
    guestshell = False

feature = "tvnet"
log = logging.getLogger(feature)
tvnet_home = '/home/guestshell/' + feature
tvnet_sentinel = tvnet_home + "/.tvnet_configured"


def setup_directory(directory):
    '''
    This function will help with setting up directory structure.
    '''
    folder_list = ['logs', 'data', 'bin']
    if not os.path.exists(directory):
        os.makedirs(directory)
    for folder in folder_list:
        folder_path = os.path.join(directory, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


def copy_custom_data_file(file):
    dest = os.path.join(tvnet_home, 'customdata.txt')

    if not os.path.exists(dest):
        if os.path.exists(file):
            copyfile(file, dest)
        else:
            log.error('FATAL ERROR: No custom data file found!')
            return False
    return dest


class csr_transit():
    def __init__(self, customDataFileName,
                 configure_pubkey=False,
                 username_pubkey='automate',
                 private_storage_account=None,
                 private_storage_key=None):  # pragma: no cover
        self.section_dict = {}
        setup_directory(tvnet_home)

        self.cd_file = copy_custom_data_file(customDataFileName)
        if not self.cd_file:
            raise IOError("Failed to load Custom Data File")

        if not self.parse_decoded_custom_data():
            raise IOError("Failed to parse Custom Data File")

        self.cloud = cloud(
            feature,
            self.section_dict['strgacctname'],
            self.section_dict['strgacckey'])

        if private_storage_account and private_storage_key:
            self.section_dict['privatestrgacctname'] = private_storage_account
            self.section_dict['privatestrgacckey'] = private_storage_key

        self.section_dict['configure_pubkey'] = configure_pubkey
        self.section_dict['username_pubkey'] = username_pubkey
        self.setup_file_dict()
        status = self.get_all_files()
        if not status:
            log.exception("""[ERROR] Failed to retrieve files from Storage account. 
            Please check Storage Account name, Storage Key and Transit VNET Name""")
            self.cmd_execute(
                "send log [ERROR] [CSRTransitVNET] Failed to retrieve files")
            self.cmd_execute(
                "send log [ERROR] [CSRTransitVNET] Please check Storage Account name, Storage Key and Transit VNET Name")
            raise Exception("Incorrect Storage name or Transit VNET Name")
        self.setup_default_dict()

    def cmd_execute(self, command):
        '''
        Note: for some reason initial pull/show always results in broken or non existent result.
        Hence execute show commands TWICE always.
        '''
        if guestshell:
            output = cli.execute(command)
        else:
            output = command
        # output = commands
        log.info(output)
        return output

    def cmd_configure(self, config):
        log.info(config)
        if guestshell:
            output = cli.configure(config)
        else:
            output = config
        log.info(output)
        return output

    def remove_eem_applet(self):
        log.info("Configured DMVPN Transit Vnet configuration. Removing Transit VnetEEM applet configuration.")
        self.cmd_configure(remove_eem_applet)

    def configure_tunnel(self, tunn_addr):
        cmd = ''
        role = self.section_dict['role'].lower()

        if 'hub' in role:
            if 'eigrp' in self.section_dict['dmvpn']["RoutingProtocol"].lower(
            ):
                cmd = hub_tunnel_config_eigrp
                cmd = cmd.format(
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr),
                    RoutingProtocolASN=str(
                        self.section_dict['dmvpn']["RoutingProtocolASN"]),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    AuthString=self.section_dict['dmvpn']["NHRPAuthString"],
                    NHRPNetworkId=str(
                        self.section_dict['dmvpn']["NHRPNetworkId"]),
                    TunnelKey=str(
                        self.section_dict['dmvpn']["TunnelKey"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"])
            elif 'bgp' in self.section_dict['dmvpn']["RoutingProtocol"].lower():
                cmd = hub_tunnel_config_bgp
                cmd = cmd.format(
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    AuthString=self.section_dict['dmvpn']["NHRPAuthString"],
                    NHRPNetworkId=str(
                        self.section_dict['dmvpn']["NHRPNetworkId"]),
                    TunnelKey=str(
                        self.section_dict['dmvpn']["TunnelKey"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"])
        else:
            nbmaconfig = ''
            for key, value in self.section_dict.items():
                if 'hub-' in key:
                    if nbmaconfig != '':
                        nbmaconfig += '\n'
                    nbmaconfig += self.get_tunnel_nhsnbma_config_base(value['nbma'], value['pip'])
            cmd = spoke_tunnel_config_general
            cmd = cmd.format(
                TunnelId=self.section_dict['dmvpn']["TunnelID"],
                TunnelIP=str(tunn_addr),
                DMVPNTunnelIpMask=str(
                    self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                AuthString=self.section_dict['dmvpn']["NHRPAuthString"],
                nbmaconfig=nbmaconfig,
                NHRPNetworkId=str(
                    self.section_dict['dmvpn']["NHRPNetworkId"]),
                TunnelKey=str(
                    self.section_dict['dmvpn']["TunnelKey"]),
                ConnName=self.section_dict['dmvpn']["ConnectionName"])
        output = self.cmd_configure(cmd)
        log.info(output)
        self.cmd_execute(
            "send log [INFO] [CSRTransitVNET] Configured {} tunnel ".format(role))
        return output

    def get_tunnel_nhsnbma_config_base(self, DMVPNHubTunnelIp, DMVPNHubIp):
        cmd = spoke_tunnel_nhsnbma_config_base
        cmd = cmd.format(
            DMVPNHubTunnelIp=str(DMVPNHubTunnelIp),
            DMVPNHubIp=DMVPNHubIp)
        return cmd

    def configure_tunnel_nhsnbma(self, DMVPNHubTunnelIp, DMVPNHubIp):
        cmd = spoke_tunnel_nhsnbma_config
        cmd = cmd.format(
            TunnelId=self.section_dict['dmvpn']["TunnelID"],
            DMVPNHubTunnelIp=str(DMVPNHubTunnelIp),
            DMVPNHubIp=DMVPNHubIp)
        output = self.cmd_configure(cmd)
        log.info(output)
        self.cmd_execute(
            "send log [INFO] [CSRTransitVNET] Configured tunnel's NBMA and \
            connected to Hub at {} IP ".format(DMVPNHubIp))
        return output

    def configure_routing(self, tunn_addr):

        role = self.section_dict['role'].lower()

        if 'eigrp' in self.section_dict['dmvpn']["RoutingProtocol"].lower():
            if 'hub' in role:
                cmd = routing_eigrp_vrf
                cmd = cmd.format(
                    RoutingProtocolASN=str(
                        self.section_dict['dmvpn']["RoutingProtocolASN"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"],
                    DMVPNTunnelIpNetworkNum=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpNetworkNum"]),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr))
            else:
                cmd = routing_eigrp
                cmd = cmd.format(
                    RoutingProtocolASN=str(
                        self.section_dict['dmvpn']["RoutingProtocolASN"]),
                    DMVPNTunnelIpNetworkNum=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpNetworkNum"]),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr))
        elif 'bgp' in self.section_dict['dmvpn']["RoutingProtocol"].lower():
            if 'hub' in role:
                cmd = routing_bgp_vrf
                cmd = cmd.format(
                    RoutingProtocolASN=str(
                        self.section_dict['dmvpn']["RoutingProtocolASN"]),
                    ConnName=self.section_dict['dmvpn']["ConnectionName"],
                    DMVPNTunnelIpNetworkNum=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpNetworkNum"]),
                    DMVPNTunnelIpPrefixLen=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpPrefixLen"]),
                    DMVPNTunnelIpMask=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpMask"]),
                    TunnelId=self.section_dict['dmvpn']["TunnelID"],
                    TunnelIP=str(tunn_addr))
            else:
                # TODO Change the router neighbours
                cmd = routing_bgp
                cmd = cmd.format(
                    RoutingProtocolASN=str(self.section_dict['dmvpn']["RoutingProtocolASN"]),
                    DMVPNTunnelIpNetworkNum=str(
                        self.section_dict['dmvpn']["DMVPNTunnelIpNetworkNum"]),
                    TunnelIP=str(tunn_addr))

        output = self.cmd_configure(cmd)
        log.info("cfg routing output = %s" % output)

        self.cmd_execute(
            "send log [INFO] [CSRTransitVNET] Configured {} {} routing.".format(
                role, self.section_dict['dmvpn']["RoutingProtocol"].lower()))
        return output

    def configure_routing_nbma(self, DMVPNHubTunnelIp):
        cmd = routing_bgp_nbma
        cmd = cmd.format(
            RoutingProtocolASN=str(self.section_dict['dmvpn']["RoutingProtocolASN"]),
            DMVPNHubTunnelIp=str(DMVPNHubTunnelIp))
        output = self.cmd_configure(cmd)
        log.info("cfg routing output = %s" % output)
        return output

    def configure_crypto_policy(self):
        '''
        This functions is responsible for configuring the router with appropriate Crypto Policy.
        Right now, we will be configuring the general crypto policy (See py variable crypto_policy_general)
        The config string is appended accordingly with fields from self.section_dict
        Args:
            ROLE, SECTION_DICT
        Returns:
            None
        '''
        role = self.section_dict['role'].lower()

        if 'hub' in role:
            vrf_config = hub_vrf_config.format(
                ConnName=self.section_dict['dmvpn']["ConnectionName"],
                TunnelId=self.section_dict['dmvpn']["TunnelID"],
                RoutingProtocolASN=str(
                    self.section_dict['dmvpn']["RoutingProtocolASN"]))
            output = self.cmd_configure(vrf_config)
            log.info("[INFO] [CSRTransitVNET] Configured HUB VRF successfully")
            log.info("output = %s" % output)
            self.cmd_execute(
                "send log [INFO] [CSRTransitVNET] Configured HUB VRF successfully")

        crypto_config = crypto_policy_general.format(
            ConnName=self.section_dict['dmvpn']["ConnectionName"],
            TunnelId=self.section_dict['dmvpn']["TunnelID"],
            SharedKey=self.section_dict['dmvpn']["SharedKey"],
            IpsecCipher=self.section_dict['dmvpn']["IpsecCipher"],
            IpsecAuthentication=self.section_dict['dmvpn']["IpsecAuthentication"])

        output = self.cmd_configure(crypto_config)
        log.info(
            '[INFO] [CSRTransitVNET] Configured crypto policy general successfully')
        log.info("crypto policy output = %s" % output)

        self.cmd_execute(
            "send log [INFO] [CSRTransitVNET] Configured crypto policy general successfully")
        return output

    def get_tunnel_addr(self):
        tunn_addr = None
        role = self.section_dict['role'].lower()
        tunnel_network = self.section_dict['DMVPNTunnelIpCidr']
        if 'hub' in role:
            log.info('[INFO] Configuring router as {}'.format(role))
            hub_dict = {}
            hub_dict['pip'] = self.cloud.tvnet.get_pip()
            self.section_dict['spoke'] = {'count': 0}
            tunn_addr = tunnel_network.network_address + int(self.section_dict['hub_number'])
            hub_dict['nbma'] = str(tunn_addr)
            self.section_dict[role] = hub_dict
        elif role == 'spoke':
            log.info('[INFO] Configuring router as SPOKE')
            try:
                dmvpn_address_count = tunnel_network.num_addresses
                spoke_vmid = self.cloud.tvnet.get_vmid()
                spoke_pip = self.cloud.tvnet.get_pip()
                random.seed(spoke_vmid)
                rand_tunn_offset = random.randint(10, dmvpn_address_count)
                self.section_dict['spoke']['count'] = int(
                    self.section_dict['spoke']['count'])
                self.section_dict['spoke']['count'] += 1
                tunn_addr = tunnel_network.network_address + rand_tunn_offset
                self.section_dict['spoke'][spoke_vmid] = {
                    'pip': str(spoke_pip), 'tunnel_address': str(tunn_addr)}
            except KeyError:
                log.info(
                    '[ERROR] Spoke count is not found in spoke file contents.')
                return None
        else:
            log.info('[ERROR] Unrecognized role is assigned to the router!')

        return tunn_addr

    def configure_transit_vnet(self):
        """
        This method is responsible for:

        1. Munch the data from custom data.
        2. Get inputs from storage account or write storage account
        3. Configure required IOS CLIs,
        4. Get a PEM Key data
        5. Configure automate username
        6. Push the PEM key to private storage account.
        """
        if not os.path.exists(tvnet_sentinel):
            # Get the tunnel address to be used for this device.
            tunn_addr = self.get_tunnel_addr()

            # Check if files and details are written to storage account.
            # If not bail configuring.
            if not self.write_all_files():
                log.error("Could not write files to storage account. Exiting out!")
                self.cmd_execute(
                    "send log [ERROR] [CSRTransitVNET] Failed to write files to storage account. Exiting out!")
                return False

            self.configure_crypto_policy()
            self.configure_tunnel(tunn_addr)
            self.configure_routing(tunn_addr)
            role = self.section_dict['role'].lower()
            if 'spoke' in role.lower():
                for key, value in self.section_dict.items():
                    if 'hub-' in key:
                        # self.configure_tunnel_nhsnbma(value['nbma'], value['pip'])
                        if 'bgp' in self.section_dict['dmvpn']["RoutingProtocol"].lower():
                            self.configure_routing_nbma(value['nbma'])
            self.cmd_execute(
                "send log [INFO] [CSRTransitVNET] Success. Configured all the required IOS configs for role: {}.".format(
                    self.section_dict['role'].lower()))
            if self.section_dict['configure_pubkey']:
                self.cmd_execute(
                        "send log [INFO] [CSRTransitVNET] Configuring the public key for username {}.".format(
                            self.section_dict['username_pubkey']
                        ))
                self.configure_pub_key()
            if not os.path.exists(tvnet_home):
                os.makedirs(tvnet_home)
            else:
                if not os.path.exists(tvnet_sentinel):
                    with open(tvnet_sentinel, 'w') as f:
                        f.write("success")
        else:
            log.info("Transit Vnet configured sentinel found. returning.")


    def configure_pub_key(self):
        fingerprint = binascii.hexlify(self.cloud.tvnet.create_pem_file(filename='privatekey'))
        cmd = username_pubkey_config.format(
            username=str(self.section_dict['username_pubkey']),
            fingerprint=str(fingerprint)
        )

        # Save the private key in the storage account
        priv_keys_folder = self.section_dict['folder'] + '/privatekeys'

        self.cloud.tvnet.create_directory(self.section_dict['file_share'],
                                          priv_keys_folder)

        vmid = self.cloud.tvnet.get_vmid()

        if 'privatestrgacctname' in self.section_dict and 'privatestrgacckey' in self.section_dict:
            private_cloud = cloud(feature,
                                  self.section_dict['privatestrgacctname'],
                                  self.section_dict['privatestrgacckey'])
            private_cloud.tvnet.create_share(self.section_dict['file_share'])
            private_cloud.tvnet.create_directory(self.section_dict['file_share'],
                                                 self.section_dict['folder'])
            private_cloud.tvnet.create_directory(self.section_dict['file_share'],
                                                 priv_keys_folder)
            private_cloud.tvnet.copy_local_file_to_remote(self.section_dict['file_share'],
                                                          priv_keys_folder,
                                                          vmid + '.pem',
                                                          os.getcwd() + '/privatekey.pem')
        else:
            self.cloud.tvnet.copy_local_file_to_remote(self.section_dict['file_share'],
                                                       priv_keys_folder,
                                                       vmid + '.pem',
                                                       os.getcwd() + '/privatekey.pem')

        output = self.cmd_configure(cmd)
        log.info("cfg ssh key output = %s" % output)
        return output

    def setup_dmvpn_dict(self):
        param_list = ['TunnelKey', 'RoutingProtocol', 'transitvnetname']
        dmvpn_dict = {}
        for param in param_list:
            dmvpn_dict[param] = self.section_dict[param]
        return dmvpn_dict

    # todo: make keyword generic
    def parse_decoded_custom_data(self, keyword='AzureTransitVNET'):
        section_flag = False
        try:
            with open(self.cd_file) as filecontents:
                for line in filecontents:
                    if 'section:' in line:
                        if keyword.lower() in line.lower():
                            section_flag = True
                        else:
                            section_flag = False

                    if section_flag:
                        split_line = line.split(' ')

                        if len(split_line) == 2:
                            self.section_dict[split_line[0].strip(
                            )] = split_line[1].strip()

                        else:
                            log.info(
                                '[ERROR] command parsing failed for %s' %
                                str(split_line))
        except IOError as e:
            log.exception('[ERROR] %s' % e)
            return False

        log.info(self.section_dict)

        return True

    def write_all_files(self):
        file_list = []
        if 'hub' in self.section_dict['role']:
            file_list = ['spoke', self.section_dict['role'], 'dmvpn']
        elif 'spoke' in self.section_dict['role']:
            file_list = ['spoke']

        for file_content in file_list:
            try:
                file_contents = self.section_dict[file_content]
                try:
                    file_name = self.section_dict['file_names'][file_content]
                except KeyError:
                    temp = file_content
                    file_name = temp.replace('-', '') + '.json'
                log.info(
                    '[INFO] Savings contents for {} in {} with {}'.format(
                        file_content, file_name, str(file_contents)))

                role = self.section_dict['role'].lower()
                if 'hub' in role and file_content == 'spoke':
                    if self.cloud.tvnet.file_exists(
                            self.section_dict['file_share'],
                            self.section_dict['folder'],
                            file_name):
                        log.info("Role hub. Spokes.json exists. skipping update.")
                        continue

                status = self.cloud.tvnet.write_file_contents(
                    self.section_dict['file_share'],
                    self.section_dict['folder'],
                    file_name,
                    file_contents)
                if not status:
                    log.error(
                        '[ERROR] Failed to save contents for {} in {} with {}'.format(
                            file_content, file_name, str(file_contents)))
                    return False

            except KeyError:
                log.info(
                    '[ERROR] could not save file for {}'.format(file_content))
        return True

    def get_all_files(self):
        if 'spoke' in self.section_dict['role']:
            file_list = ['spoke', 'dmvpn']
            folder_contents = self.cloud.tvnet.get_list_directories_and_files(
                self.section_dict['file_share'],
                self.section_dict['folder'])
            if not folder_contents:
                log.error("[ERROR] Either Storage account is not present or Transit VNET name is incorrect!")
                return False
            for item in folder_contents:
                if 'hub' in item['name']:
                    result = re.search('(\d+)', item['name'])
                    hub_number = int(result.groups()[0])
                    if item['type'] == 'File':
                        hubname = 'hub-' + str(hub_number)
                        file_list.append(hubname)
                        try:
                            hubfile_name = self.section_dict['file_names'][hubname]
                            if hubfile_name != item['name']:
                                self.section_dict['file_names'][hubname] = item['name']
                        except KeyError:
                            self.section_dict['file_names'][hubname] = item['name']
        else:
            file_list = ['dmvpn']

        hub_flag = False
        if 'hub' in self.section_dict['role']:
            hub_flag = True

        for file_content in file_list:
            contents = None
            tries = 0
            while contents is None:
                log.info(
                    '{} {} {}'.format(
                        self.section_dict['file_share'],
                        self.section_dict['folder'],
                        self.section_dict['file_names'][file_content]))
                contents = self.cloud.tvnet.get_file_contents_json(
                    self.section_dict['file_share'],
                    self.section_dict['folder'],
                    self.section_dict['file_names'][file_content])
                if contents:
                    log.info(
                        '[INFO] Retrieved file contents for {}: {}'.format(
                            file_content, str(contents)))
                else:
                    if hub_flag:
                        break
                    log.info(
                        '[ERROR] Error while retrieving {}. Try num: {}'.format(
                            file_content, str(tries)))
                    time.sleep(50)
                    tries += 1
            if contents:
                self.section_dict[file_content] = contents

        return self.section_dict

    def setup_file_dict(self):
        self.section_dict['folder'] = 'config'
        self.section_dict['file_names'] = {
            'hub-1': 'hub1.json',
            'hub-2': 'hub2.json',
            'spoke': 'spokes.json',
            'dmvpn': 'dmvpn.json'}
        role = self.section_dict['role']
        if 'hub' in role.lower():
            result = re.search('hub-(\d+)', role)
            if result is not None:
                self.section_dict['hub_number'] = int(result.groups()[0])
            else:
                result = re.search('(\d+)', role)
                self.section_dict['hub_number'] = int(result.groups()[0])
                role = 'hub-' + str(int(result.groups()[0]))
                self.section_dict['role'] = role

            if role not in self.section_dict['file_names'].keys():
                self.section_dict['file_names'][role] = role.replace('-', '') + '.json'
        try:
            file_share = self.section_dict['transitvnetname'].lower()
            self.section_dict['file_share'] = file_share
        except KeyError:
            file_share = 'new'
            self.section_dict['file_share'] = file_share

    def setup_default_dict(self):

        if 'dmvpn' not in self.section_dict:
            self.section_dict['dmvpn'] = {}
        '''
        Below double KeyError is essential for the sequence of where we take 
        in DMVPN tunnel Ipaddress from.
        3. Get CIDR from custom data.
        2. if not found replace with 1.1.1.0/24
        1. Override previous two if data is present in Storage accounts 'dmvpn.json'
        '''
        try:
            DMVPNTunnelIpCidrStr = self.section_dict['DMVPNTunnelIpCidr']

        except KeyError:
            DMVPNTunnelIpCidrStr = u'1.1.1.0/24'
        try:
            DMVPNTunnelIpCidrStr = self.section_dict['dmvpn']['DMVPNTunnelIpCidr']
        except KeyError:
            pass

        try:
            DMVPNTunnelIpCidr = ipaddress.IPv4Network(DMVPNTunnelIpCidrStr.decode('utf-8'))
        except AttributeError:
            DMVPNTunnelIpCidr = ipaddress.IPv4Network(DMVPNTunnelIpCidrStr)

        self.section_dict['DMVPNTunnelIpCidr'] = DMVPNTunnelIpCidr

        default_dict = {
            "ConnectionName": "tvnet",
            "RoutingProtocol": "EIGRP",
            "TunnelID": 11,
            "TunnelKey": 12210,
            "SharedKey": 'ciscokey',
            "IpsecCipher": "esp-aes",
            "IpsecAuthentication": "esp-sha-hmac",
            "RoutingProtocolASN": 64512,
            "NHRPAuthString": 'cisco',
            "NHRPNetworkId": 1024
        }

        for key, value in default_dict.items():
            try:
                self.section_dict[key]
                self.section_dict['dmvpn'][key] = self.section_dict[key]
            except KeyError:
                try:
                    self.section_dict['dmvpn'][key]
                    self.section_dict[key] = self.section_dict['dmvpn'][key]
                except KeyError:
                    self.section_dict[key] = value
                    self.section_dict['dmvpn'][key] = value

        tunnel_addressing_dict = {
            "DMVPNTunnelIpCidr": DMVPNTunnelIpCidr,
            "DMVPNHubTunnelIp1": DMVPNTunnelIpCidr.network_address + 1,
            "DMVPNHubTunnelIp2": DMVPNTunnelIpCidr.network_address + 2,
            "DMVPNTunnelIpMask": DMVPNTunnelIpCidr.netmask,
            "DMVPNTunnelIpNetworkNum": DMVPNTunnelIpCidr.network_address,
            "DMVPNTunnelIpHostMask": DMVPNTunnelIpCidr.hostmask,
            "DMVPNTunnelIpPrefixLen": DMVPNTunnelIpCidr.prefixlen
        }

        for key, value in tunnel_addressing_dict.items():
            self.section_dict[key] = value
            self.section_dict['dmvpn'][key] = value
