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
    s.settimeout(3000)
    s.connect((host, port))

    queries = b"""!!
!aAS-10021ARCSTAR
!aAS-10099NTT
!aAS-10204
!aAS-11114
!aAS-131248-CUST
!aAS-132132-TRANSIT
!aAS-132876
!aAS-133045-TRANSIT
!aAS-134842
!aAS-135377
!aAS-16524
!aAS-17534
!aAS-17666
!aAS-17958
!aAS-18149ARCSTAR
!aAS-18683-MWFN-TRANSIT
!aAS-19016
!aAS-19303
!aAS-1AND1
!aAS-20264
!aAS-20394-CUSTOMERS
!aAS-21VIANET
!aAS-23655-ALL
!aAS-24413
!aAS-2500-2914
!aAS-25766-DOWNSTREAM
!aAS-26167
!aAS-29802
!aAS-30517-ASSOCIATED
!aAS-30640
!aAS-31515ARCSTAR
!aAS-33606
!aAS-35916-TRANSIT
!aAS-38566
!aAS-395412-TRANSIT
!aAS-395662
!aAS-3TCOM
!aAS-3W-INFRA
!aAS-40676
!aAS-45903
!aAS-46043
!aAS-4628
!aAS-46475
!aAS-4648-Customers
!aAS-46652
!aAS-46844
!aAS-4693ARCSTAR
!aAS-4761
!aAS-48196
!aAS-4D-DC
!aAS-50010
!aAS-5009
!aAS-52551
!aAS-55532ARCSTAR
!aAS-55805
!aAS-55967
!aAS-5713
!aAS-57344
!aAS-58463
!aAS-58682
!aAS-59318-AS-KH
!aAS-60917
!aAS-61832-clientes
!aAS-62833-ny4
!aAS-63916
!aAS-7552
!aAS-7562
!aAS-9268ARCSTAR
!aAS-9381
!aAS-9416-TRANSIT
!aAS-9908VERIO
!aAS-9929ARCSTAR
!aAS-A2B
!aAS-AA
!aAS-AAMRA-ATL-BD
!aAS-ACCELERATED
!aAS-ACCESSFORALL
!aAS-ACCRETIVE
!aAS-ACESSO10
!aAS-ACORUS
!aAS-ADAM-EU
!aAS-ADAMOEU
!aAS-ADAMS
!aAS-ADHOST-PEERING
!aAS-ADNC-SAN
!aAS-ADNET
!aAS-ADNET-DC
!aAS-ADNET-DC6
!aAS-ADNET6
!aAS-AEG
!aAS-AFILIAS-FULLMONTY
!aAS-AGARTO
!aAS-AGARTO6
!aAS-AGILIT
!aAS-AGODA
!aAS-AI
!aAS-AIE
!aAS-AIRBANDUK
!aAS-AIRBANDUK-IPV6
!aAS-AIRWIRE
!aAS-AKAMAI
!aAS-ALCOM
!aAS-ALHAMBRA
!aAS-ALLIED_TELECOM
!aAS-ALTECOM
!aAS-AMATIS
!aAS-AMAZON
!aAS-AMC
!aAS-AMCL-BB
!aAS-AMERICANET-BR
!aAS-AMERIDOTCA
!aAS-AMERIDOTCA6
!aAS-AMPERSAND
!aAS-ANEXIA
!aAS-ANIN
!aAS-ANJOS
!aAS-ANTEL-ALL
!aAS-ANX
!aAS-ANYCAST
!aAS-AOFEI-Intl
!aAS-AOI
!aAS-AORTA
!aAS-AORTA6
!aAS-APPLE
!aAS-APPNOR
!aAS-ARENAONE
!aAS-ARI
!aAS-ARIN-NTT-SILICON-VALLEY
!aAS-ARIN-SERVICE-EAST
!aAS-ARMSTRONGPXY
!aAS-ARPNETWORKS
!aAS-AS29550
!aAS-AS29550-V6
!aAS-ASAHI-NET
!aAS-ASK4
!aAS-ASTRALUS
!aAS-ATOM86
!aAS-AUTOMATTIC
!aAS-AVIRADE
!aAS-AXNE
!aAS-AYERA
!aAS-AZERSATMEMBERS
!aAS-BANDWIDTH
!aAS-BBC
!aAS-BBCONNECT
!aAS-BBOI
!aAS-BDRV
!aAS-BEANFIELD
!aAS-BELBONEMEMBERS
!aAS-BELCLOUD
!aAS-BELCLOUD-V6
!aAS-BELNET
!aAS-BENDTEL
!aAS-BERTRAMWIRELESS
!aAS-BESTPATH
!aAS-BGCOM
!aAS-BGL
!aAS-BGPNET
!aAS-BIDSTRADING
!aAS-BIGPIPE
!aAS-BIH
!aAS-BINCNET
!aAS-BIT
!aAS-BIT6
!aAS-BKNIX
!aAS-BKVG
!aAS-BLACKNIGHT
!aAS-BLIZZARD
!aAS-BLRS
!aAS-BOGONS
!aAS-BORWOOD
!aAS-BOUYGTEL-ISP
!aAS-BRIDGEFIBRE
!aAS-BROADASPECT
!aAS-BSKYB-BROADBAND
!aAS-BT-GLOBAL
!aAS-BTC-UP
!aAS-BTC-UP-V6
!aAS-BTELOUT
!aAS-BTELOUT-V6
!aAS-BTS
!aAS-BTS-GLOBAL
!aAS-BULSATCOM
!aAS-BURSTFIRE-NTT
!aAS-BWFN
!aAS-BXI
!aAS-BYTEMARK
!aAS-BatBlue
!aAS-C4L
!aAS-CACHENETWORKS
!aAS-CADENCE
!aAS-CAIS
!aAS-CALL27
!aAS-CAMBRIUM
!aAS-CAMPAIGNMONITOR
!aAS-CANAR-TRANSIT
!aAS-CAPENET
!aAS-CAPITALONLINEDATAgit 
!aAS-CARPATHIA
!aAS-CATALYST2
!aAS-CATALYST2-V6
!aAS-CAVEO
!aAS-CBCCOM
!aAS-CBJAYABBAND
!aAS-CCCN
!aAS-CCI
!aAS-CCI-FL-CUST
!aAS-CCI-KS-CUST
!aAS-CCSLEEDS
!aAS-CDNETWORKS
!aAS-CELESTE
!aAS-CENTERPRESTADORA
!aAS-CENTRILOGIC
!aAS-CESNET
!aAS-CESNET6
!aAS-CETIN
!aAS-CHAOS
!aAS-CHIEF-TRANSIT
!aAS-CHOOPA
!aAS-CIFNET
!aAS-CIPHERKEY-TRANSIT
!aAS-CITIZENSCOOP
!aAS-CJH
!aAS-CLEARIP
!aAS-CLOUDFLARE
!aAS-CLOUDHELIX
!aAS-CLOUDMERGE
!aAS-CLOUVIDER
!aAS-CMI-ALL
!aAS-CN2
!aAS-CNA
!aAS-CNHAT
!aAS-CNHAT-V6
!aAS-CODETEL
!aAS-COLO-AU
!aAS-COLOAT
!aAS-COLOCLUE
!aAS-COLT
!aAS-COLT6
!aAS-COMSAVE
!aAS-COMVIVE
!aAS-CONNETU
!aAS-CONTINENT8-ASIA
!aAS-CORALNET
!aAS-COREIX
!aAS-CORESPACE-DAL
!aAS-COREXCHANGE-US
!aAS-CORPORATIVATELCOM
!aAS-COX-TRANSIT
!aAS-CPNET
!aAS-CPRM
!aAS-CRITEO-AP
!aAS-CSF
!aAS-CSLOXINFO-TRANSIT
!aAS-CTCX
!aAS-CTI-Telecom
!aAS-CTMTELEONE
!aAS-CUSTDC
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
