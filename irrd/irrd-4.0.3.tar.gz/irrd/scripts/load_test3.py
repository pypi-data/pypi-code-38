#!/usr/bin/env python
# flake8: noqa: E402

"""
A simple load tester for IRRd.
Sends random !g queries.
"""
import time

import argparse
import random
import socket


def main(host, port, count):
    queries = [b'!!\n']
    for i in range(count):
        asn = random.randrange(1, 50000)
        query = f'!gAS{asn}\n'.encode('ascii')
        queries.append(query)
    queries.append(b'!q\n')

    s = socket.socket()
    s.settimeout(600)
    s.connect((host, port))

    queries = b"""!!
!aAS-RAGINGWIRE
!aAS-RAINBOW
!aAS-RAKUTEN-RBN
!aAS-RATIONAL-CUS
!aAS-RBLHST
!aAS-RDSNET
!aAS-REBACOM
!aAS-REDIRIS
!aAS-RETELIT
!aAS-RETN
!aAS-RETN6
!aAS-RG-DFW
!aAS-RG-IAD
!aAS-RG-SEA
!aAS-RHTEC
!aAS-RHTEC6
!aAS-RICHTOPEC
!aAS-RINGCENTRAL
!aAS-RIOT
!aAS-RKOM
!aAS-RMI
!aAS-RMIFL
!aAS-RNP-TRANSIT
!aAS-ROCKISLAND
!aAS-ROKA
!aAS-ROSITE
!aAS-ROSITE6
!aAS-RPS
!aAS-RTD
!aAS-RUBICONPROJECT
!aAS-RWTS-DS
!aAS-SAKURA
!aAS-SALESFORCE
!aAS-SANNET
!aAS-SARENET
!aAS-SARGASSO-UK
!aAS-SAVVISJP
!aAS-SBN-IIG
!aAS-SCIS
!aAS-SDT
!aAS-SDT-V6
!aAS-SEABONE
!aAS-SEABONE-V6
!aAS-SECARMA
!aAS-SECBUBWC
!aAS-SECH-EAT
!aAS-SECURA
!aAS-SEEDNET
!aAS-SEMAPHORE
!aAS-SERVERCENTRAL
!aAS-SERVEREL
!aAS-SERVERSCOM
!aAS-SET-40356
!aAS-SET-9930
!aAS-SET-AFRIX
!aAS-SET-ANTAMEDIAKOM
!aAS-SET-BIGBAND
!aAS-SET-BSCCL
!aAS-SET-GTI
!aAS-SET-IPDC
!aAS-SET-SEACOM
!aAS-SET-TELBRU-APNIC
!aAS-SET-XLCG-GLOBAL
!aAS-SET6-38566
!aAS-SETPTCL
!aAS-SGGS
!aAS-SHARKS
!aAS-SHARKS6
!aAS-SHENTEL
!aAS-SINET4
!aAS-SINGTEL
!aAS-SIOL
!aAS-SIOL6
!aAS-SIP
!aAS-SKBroadband
!aAS-SKYCABLE
!aAS-SKYVISION
!aAS-SLF-13760-DOWNSTREAM
!aAS-SLINC
!aAS-SLT-GLOBAL
!aAS-SMAID
!aAS-SO-NET6
!aAS-SOFIA-CONNECT
!aAS-SOFIA-CONNECT-V6
!aAS-SOFTLAYER
!aAS-SOHONET-UK
!aAS-SOLCON
!aAS-SOLCON6
!aAS-SOLNET
!aAS-SOMEADDRESS
!aAS-SONY-CGEI
!aAS-SOTACONNECT
!aAS-SOUTHEAST-TEXAS-GIGAPOP-VERIO
!aAS-SOVAM
!aAS-SPACENET
!aAS-SPACENET-V6
!aAS-SPACENETWORK
!aAS-SPNET
!aAS-SPOTIFY
!aAS-SRT
!aAS-SSCNETWORKS
!aAS-STACKPATH
!aAS-STARHUBINTERNET
!aAS-STARTNIX-EU
!aAS-STARTOUCH
!aAS-STCN
!aAS-STEADFAST
!aAS-STEALTH
!aAS-STRATUS-DOWNSTREAM
!aAS-STS-RO
!aAS-SUITABLETECH
!aAS-SUPERINTERNET
!aAS-SUPRANET
!aAS-SURETEC
!aAS-SURFNET
!aAS-SWCMGLOBAL
!aAS-SWIPNET
!aAS-SWITCHCO
!aAS-SYMC
!aAS-SYSELEVEN
!aAS-SZARANET
!aAS-So-Net
!aAS-TABOOLA
!aAS-TANGO
!aAS-TASHICELL
!aAS-TCTWest
!aAS-TDATANET
!aAS-TDCNET
!aAS-TDCNET-IPV6
!aAS-TDDE
!aAS-TECHNO
!aAS-TECHNO-V6
!aAS-TECNOCRATICA
!aAS-TELAPPLIANT
!aAS-TELCONET-TRANSIT-AS
!aAS-TELE2
!aAS-TELENET
!aAS-TELEPAK-C
!aAS-TELETRANS
!aAS-TELIKO
!aAS-TELMEX
!aAS-TELSTRA-INTL-CUSTOMERS
!aAS-TERTIARY
!aAS-TFN-TRANSIT1
!aAS-TGW
!aAS-THEGIGABIT
!aAS-THINFACTORY
!aAS-THIX
!aAS-THRESHINC
!aAS-TICGW
!aAS-TIG-GROUP
!aAS-TIGGEE
!aAS-TIMICO
!aAS-TIPNETIT
!aAS-TKPSA-UP
!aAS-TMHK
!aAS-TMNET-CUSTOMERS
!aAS-TMR
!aAS-TMX-PERU-TRANSIT
!aAS-TOTALUPTIME
!aAS-TOUCHTONE
!aAS-TOWARDEX
!aAS-TRANSIP
!aAS-TRANSIT-GLOBE
!aAS-TRANSITOS
!aAS-TRANSIX-E
!aAS-TRANSIX-W
!aAS-TREML-STURM
!aAS-TRIPLETNET
!aAS-TROYC-01
!aAS-TRUE
!aAS-TRUNKNETWORKS
!aAS-TTK
!aAS-TTK6
!aAS-TTNET
!aAS-TURN
!aAS-TVC
!aAS-TWIG
!aAS-TWITTER
!aAS-TWTIT
!aAS-Tecnocratica
!aAS-Telx
!aAS-Transit-NetNam
!aAS-U-NETSURF
!aAS-UCC
!aAS-UKBB6
!aAS-UKSERVERS
!aAS-ULTRACOM
!aAS-UNBELIEVABLE
!aAS-UNILINK
!aAS-UNILINK-V6
!aAS-UNILOGICNET
!aAS-UNISERVER
!aAS-UNITAS
!aAS-VAIONI
!aAS-VALVE
!aAS-VDC
!aAS-VECTANT
!aAS-VELIANET
!aAS-VELIANET-V6
!aAS-VERIO-65029
!aAS-VERIO-65031
!aAS-VERIO-65052
!aAS-VERIO-65053
!aAS-VERIO-65056
!aAS-VERIO-65061
!aAS-VERIO-65072
!aAS-VERIO-65073
!aAS-VERIO-65301
!aAS-VERIO-65304
!aAS-VERIXI
!aAS-VERSATEL-V6
!aAS-VIANET
!aAS-VIAWEST-TRANSIT
!aAS-VIPNETNTT
!aAS-VIRTELA-COMM
!aAS-VKONTAKTE
!aAS-VORBOSS
!aAS-VORBOSS6
!aAS-VOXILITY-SET
!aAS-VRNETZE-FRA
!aAS-WBTSJP-NET
!aAS-WEBAIR
!aAS-WEBDISCOUNT
!aAS-WEBEX
!aAS-WEBNX
!aAS-WERADIO
!aAS-WERITECH
!aAS-WIFIRST
!aAS-WIKIMEDIA
!aAS-WILDCARD
!aAS-WIMANX
!aAS-WINDSTREAM
!aAS-WINKY
!aAS-WINSPEED-TRANSIT
!aAS-WOLCOMM
!aAS-WOW
!aAS-WPT
!aAS-WWN
!aAS-WZ-EU
!aAS-WZ-US
!aAS-XEPHION
!aAS-XFERNET
!aAS-XMISSION
!aAS-XO
!aAS-XPNTI
!aAS-XTOM
!aAS-XTRAORDINARY
!aAS-ZAYO-ZCLOUD-ATL01
!aAS-ZEN
!aAS-ZENEDGE
!aAS-ZENLAYER
!aAS-ZILLO1
!aAS-anch-global
!aAS-enjoyvc-Kwai
!aAS-eo
!aAS-fnetlink
!aAS-globalfrag
!aAS-iTSCOM
!aAs-simwood
!aas-30666
!aas-AS19905
!aas-NewEdge
!aas-Peak10
!aas-cdn77
!aas-comms365
!aas-ebaymtbb
!aas-freethought
!aas-gorannet
!aas-gtld
!aas-gtt
!aas-infinitytelecom
!aas-iwonco-default
!aas-pldt
!aas-portlane
!aas-roblox
!aas-set-ipserverone
!q""".splitlines()

    queries_str = b'\n'.join(queries) + b'\n'
    s.sendall(queries_str)

    start_time = time.perf_counter()
    while 1:
        data = s.recv(1024*1024)
        if not data:
            break

    count = len(queries) - 1
    elapsed = time.perf_counter() - start_time
    time_per_query = elapsed / count * 1000
    qps = int(count / elapsed)
    print(f'Ran {count} queries in {elapsed}s, time per query {time_per_query} ms, {qps} qps')


if __name__ == '__main__':  # pragma: no cover
    description = """A simple load tester for IRRd. Sends random !g queries."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--count', dest='count', type=int, default=5000,
                        help=f'number of queries to run (default: 5000)')
    parser.add_argument('host', type=str,
                        help='hostname of instance')
    parser.add_argument('port', type=int,
                        help='port of instance')
    args = parser.parse_args()

    main(args.host, args.port, args.count)
