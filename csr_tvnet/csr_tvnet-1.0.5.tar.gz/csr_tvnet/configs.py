#!/usr/bin/env python
# -*- coding: utf-8 -*-

username_pubkey_config = '''
username {username} privilege 15
ip ssh pubkey-chain
username {username}
key-hash ssh-rsa {fingerprint}
'''

'''
crypto_policy_general

This crypto config can be used for either flavors of DMVPN.
BGP/EIGRP will utilize this crypto policy

'''

remove_eem_applet = '''
no event manager applet after-boot
no event manager applet after-guestshell-tvnet
'''

hub_vrf_config = '''
ip vrf {ConnName}-Tun-{TunnelId}
rd {RoutingProtocolASN}:{TunnelId}
route-target export {RoutingProtocolASN}:{TunnelId}
route-target import {RoutingProtocolASN}:{TunnelId}
'''

crypto_policy_general = '''
crypto keyring keyring-{ConnName}-Tun-{TunnelId}
local-address GigabitEthernet1
pre-shared-key address 0.0.0.0 0.0.0.0 key {SharedKey}
crypto isakmp policy 300
encr aes
authentication pre-share
group 5
crypto isakmp keepalive 60 5
crypto ipsec security-association replay window-size 1024
!
crypto ipsec transform-set transform-{ConnName}-Tun-{TunnelId} {IpsecCipher} {IpsecAuthentication}
mode transport
!
crypto ipsec profile profile-{ConnName}-Tun-{TunnelId}
set transform-set transform-{ConnName}-Tun-{TunnelId}
'''

'''
hub_tunnel_config_eigrp

This below config is specific for DMVPN over EIGRP.
It can be used for both HUB1 and HUB2
'''
hub_tunnel_config_eigrp = '''
interface Tunnel{TunnelId}
ip vrf forwarding {ConnName}-Tun-{TunnelId}
ip address {TunnelIP} {DMVPNTunnelIpMask}
no ip redirects
no ip next-hop-self eigrp {RoutingProtocolASN}
no ip split-horizon eigrp {RoutingProtocolASN}
ip nhrp authentication {AuthString}
ip nhrp network-id {NHRPNetworkId}
ip nhrp redirect
load-interval 30
tunnel source GigabitEthernet1
tunnel mode gre multipoint
tunnel key {TunnelKey}
tunnel protection ipsec profile profile-{ConnName}-Tun-{TunnelId}
ip mtu 1400
'''

'''
hub_tunnel_config_bgp

This below config is specific for DMVPN over BGP.
It can be used for both HUB1 and HUB2
'''
hub_tunnel_config_bgp = '''
interface Tunnel{TunnelId}
ip vrf forwarding {ConnName}-Tun-{TunnelId}
ip address {TunnelIP} {DMVPNTunnelIpMask}
no ip redirects
ip mtu 1400
ip nhrp redirect
ip nhrp authentication {AuthString}
ip nhrp network-id {NHRPNetworkId}
load-interval 30
ip tcp adjust-mss 1360
tunnel source GigabitEthernet1
tunnel mode gre multipoint
tunnel key {TunnelKey}
tunnel protection ipsec profile profile-{ConnName}-Tun-{TunnelId}
'''

'''
spoke_tunnel_config_general

This config will used for both flavors of DMVPN.
This below Spoke tunnel config will be able to connect to two Hubs.

'''
spoke_tunnel_config_general = '''
interface Tunnel{TunnelId}
ip address {TunnelIP} {DMVPNTunnelIpMask}
no ip redirects
ip mtu 1400
ip nhrp authentication {AuthString}
ip nhrp network-id {NHRPNetworkId}
{nbmaconfig}
ip tcp adjust-mss 1360
tunnel source GigabitEthernet1
tunnel mode gre multipoint
tunnel key {TunnelKey}
tunnel protection ipsec profile profile-{ConnName}-Tun-{TunnelId}
'''

spoke_tunnel_nhsnbma_config = '''
interface Tunnel{TunnelId}
ip nhrp nhs {DMVPNHubTunnelIp} nbma {DMVPNHubIp} multicast
'''

spoke_tunnel_nhsnbma_config_base = 'ip nhrp nhs {DMVPNHubTunnelIp} nbma {DMVPNHubIp} multicast'

'''
routing_eigrp

This config is for EIGRP routing. This config can be used in HUBS and SPOKES.
It will very specific to DMVPN over EIGRP.

'''
routing_eigrp_vrf = '''
router eigrp {RoutingProtocolASN}
address-family ipv4 vrf {ConnName}-Tun-{TunnelId}
network {DMVPNTunnelIpNetworkNum} {DMVPNTunnelIpMask}
eigrp router-id {TunnelIP}
redistribute connected
passive-interface default
no passive-interface Tunnel{TunnelId}
autonomous-system {RoutingProtocolASN}
no auto-summary
exit-address-family
'''
routing_eigrp = '''
router eigrp {RoutingProtocolASN}
network {DMVPNTunnelIpNetworkNum} {DMVPNTunnelIpMask}
eigrp router-id {TunnelIP}
redistribute connected
passive-interface default
no passive-interface Tunnel{TunnelId}
no auto-summary
'''

routing_bgp_vrf = '''
router bgp {RoutingProtocolASN}
bgp log-neighbor-changes
bgp listen range {DMVPNTunnelIpNetworkNum}/{DMVPNTunnelIpPrefixLen} peer-group spokes
!
address-family ipv4 vrf {ConnName}-Tun-{TunnelId}
bgp listen limit 10000
network {DMVPNTunnelIpNetworkNum}
bgp router-id {TunnelIP}
neighbor spokes peer-group
neighbor spokes remote-as {RoutingProtocolASN}
neighbor spokes route-reflector-client
no auto-summary
exit-address-family
'''

routing_bgp = '''
router bgp {RoutingProtocolASN}
bgp log-neighbor-changes
network {DMVPNTunnelIpNetworkNum}
bgp router-id {TunnelIP}
redistribute connected
no auto-summary
'''
routing_bgp_nbma = '''
router bgp {RoutingProtocolASN}
neighbor {DMVPNHubTunnelIp} remote-as {RoutingProtocolASN}
no auto-summary
'''

'''

THese configs are for STATIC inputs and for test purposes only.

'''

hub_tunnel_config_static = '''
interface Tunnel1
ip address {} 255.255.255.0
no ip redirects
no ip next-hop-self eigrp 1
no ip split-horizon eigrp 1
ip nhrp authentication cisco
ip nhrp network-id 1
load-interval 30
tunnel source GigabitEthernet1
tunnel mode gre multipoint
tunnel key 0
tunnel protection ipsec profile vti-1
ip mtu 1400
'''


crypto_policy_aes256_static = '''
crypto isakmp policy 1
encr aes 256
authentication pre-share
crypto isakmp key cisco address 0.0.0.0
crypto ipsec transform-set uni-perf esp-aes 256 esp-sha-hmac
mode transport
crypto ipsec profile vti-1
set security-association lifetime kilobytes disable
set security-association lifetime seconds 86400
set transform-set uni-perf
set pfs group2
'''

routing_eigrp_static = '''
router eigrp 1
network 1.1.1.0 0.0.0.255
network {} {}
passive-interface default
no passive-interface Tunnel1
'''

spoke_tunnel_config_static = '''
interface Tunnel1
ip address {} 255.255.255.0
no ip redirects
ip nhrp authentication cisco
ip nhrp network-id 1
ip nhrp nhs 1.1.1.1 nbma {} multicast
ip nhrp nhs 1.1.1.2 nbma {} multicast
load-interval 30
tunnel source GigabitEthernet1
tunnel mode gre multipoint
tunnel key 0
tunnel protection ipsec profile vti-1
'''

spoke_tunnel_config_single_static = '''
interface Tunnel1
ip address {} 255.255.255.0
no ip redirects
ip nhrp authentication cisco
ip nhrp network-id 1
ip nhrp nhs 1.1.1.1 nbma {} multicast
load-interval 30
tunnel source GigabitEthernet1
tunnel mode gre multipoint
tunnel key 0
tunnel protection ipsec profile vti-1
'''
