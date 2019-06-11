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
!aAS-CWASIA
!aAS-CWCI
!aAS-CWCS-PS
!aAS-CYBERLYNK
!aAS-CYPRESSTEL
!aAS-CYSO
!aAS-Comporium-Transit
!aAS-Cybercon
!aAS-D-NET
!aAS-DACOM
!aAS-DAILYMOTION
!aAS-DALENYS
!aAS-DATA393-INV01
!aAS-DATAHOP
!aAS-DATAPIPE
!aAS-DCI
!aAS-DCLUX
!aAS-DDOS-GUARD
!aAS-DEFENSE
!aAS-DELTA
!aAS-DENIC
!aAS-DEVCLIC
!aAS-DGINET
!aAS-DIALTELECOM
!aAS-DIDICHUXING
!aAS-DIMENOC
!aAS-DINAMICA-BR
!aAS-DIRECT_PEERS
!aAS-DIYIXIAN
!aAS-DLIVE
!aAS-DMITINC
!aAS-DOCLER
!aAS-DOTRO
!aAS-DRUKNET-TRANSIT
!aAS-DSTORAGE
!aAS-DSTORAGE-V6
!aAS-DTN
!aAS-DUMARCA
!aAS-DUOCAST
!aAS-DWNI
!aAS-DXNET
!aAS-DXTLTECH
!aAS-DYNINC
!aAS-EASYNET
!aAS-EBT
!aAS-EC-MI
!aAS-EDGECAST
!aAS-EDION
!aAS-EDISON-CARRIER-SOLUTIONS
!aAS-EDXNETWORK
!aAS-EFAR
!aAS-EHIME-CATV
!aAS-EIGI
!aAS-EIGI-SC
!aAS-EIRCOM
!aAS-EISCO
!aAS-EISON-LTD
!aAS-EITC-DU
!aAS-EL-K-STIL
!aAS-ELASTX
!aAS-ELI
!aAS-ELIAS
!aAS-ELLIJAY
!aAS-EMAILVISION
!aAS-EMIX
!aAS-ENTELBOLIVIA
!aAS-ENTER
!aAS-ENTER-V6
!aAS-EONIX
!aAS-EQUANT-ASIA
!aAS-EQUINIX-AP
!aAS-EQUINIX-EC
!aAS-EQUINIX-EU
!aAS-EQUINIX-OS
!aAS-ESH
!aAS-ESNET
!aAS-ETHEROUTE
!aAS-ETOP
!aAS-EUNETWORKS
!aAS-EUTELSAT-TH2
!aAS-EVERESTDATA
!aAS-EXA
!aAS-EXASCALE
!aAS-EXATEL-INT
!aAS-EXN
!aAS-EXPEDIENT
!aAS-EXPONENTIAL-e
!aAS-EXPONENTIAL-e-6
!aAS-EnergyGroupNetworks
!aAS-Expedient6
!aAS-FARSIGHT
!aAS-FASTNET
!aAS-FBDC
!aAS-FHE3NET
!aAS-FHL
!aAS-FIBERHUB
!aAS-FIBERRING
!aAS-FIDONET
!aAS-FIRSTCOLO
!aAS-FLAGT
!aAS-FLUENCY
!aAS-FOBUL
!aAS-FOBUL-V6
!aAS-FORCEPOINT-CLOUD
!aAS-FOREMOST
!aAS-FORTEX
!aAS-FORTEX6
!aAS-FPP
!aAS-FPT
!aAS-FREECOMM
!aAS-FREENETDE
!aAS-FREENETDE6
!aAS-FROM-JP-FTMNET
!aAS-FSYS
!aAS-FUSE
!aAS-FUSIX
!aAS-FUZENET
!aAS-G8
!aAS-GAMMATELECOM
!aAS-GBLX
!aAS-GBXS
!aAS-GBXS6
!aAS-GCI
!aAS-GCNET
!aAS-GCNETV6
!aAS-GCOM-MD
!aAS-GCONNECT
!aAS-GCORE
!aAS-GCTR-JP
!aAS-GDG
!aAS-GENCAT
!aAS-GENESISADAPTIVE
!aAS-GFSB
!aAS-GIGAINFRA
!aAS-GIGAINFRA-V6
!aAS-GIGANEWS-ALL
!aAS-GIPNET
!aAS-GITS
!aAS-GLIDE
!aAS-GLOBAL
!aAS-GLOBALNOC
!aAS-GLOBALNOC6
!aAS-GLOBEINTERNET
!aAS-GLOBEINTERNET-IPv6
!aAS-GMO
!aAS-GNT
!aAS-GOOGLE
!aAS-GORILLASERVERS
!aAS-GOSCOMB
!aAS-GOSCOMB-V6
!aAS-GRAFIX-TRANSIT
!aAS-GRAJAUNET
!aAS-GRU
!aAS-GSVNET
!aAS-GTLD
!aAS-GVA
!aAS-GVM
!aAS-GVM6
!aAS-GXT
!aAS-GYRON
!aAS-GigaDefence
!aAS-HANABI
!aAS-HANABI4-MDDOS
!aAS-HANOITELECOM
!aAS-HARGRAY-TRANSIT
!aAS-HEAS
!aAS-HELINET-V4
!aAS-HELINET-V6
!aAS-HETZNER
!aAS-HGC-INTL
!aAS-HIBERNIA
!aAS-HIGE
!aAS-HIGHWINDS
!aAS-HKBN
!aAS-HKNET
!aAS-HOPONE
!aAS-HOSTIT-MK
!aAS-HOSTIT-NN
!aAS-HOSTMY
!aAS-HOSTSERVER
!aAS-HOSTWAY
!aAS-HOTnet-HOTCN
!aAS-HPC-MVM
!aAS-HURRICANE
!aAS-HURRICANEv6
!aAS-HUTCHCITY
!aAS-I-NET
!aAS-I123
!aAS-I3-BGP-CUSTOMERS
!aAS-IBGC
!aAS-IBMNET-JP
!aAS-IBOSS
!aAS-ICANN
!aAS-ICANN6
!aAS-ICNC
!aAS-ICTX
!aAS-IDAQ
!aAS-IDC
!aAS-IDC6
!aAS-IDNET
!aAS-IGNEMEA
!aAS-IGUANE
!aAS-IGW-SET
!aAS-IHENDERSON
!aAS-II-OKINAWA
!aAS-IIJ
!aAS-IIJ6
!aAS-IMGIX
!aAS-IN2NET
!aAS-INCAPSULA
!aAS-INCOMM
!aAS-INETBONE
!aAS-INETBONE-V6
!aAS-INETC
!aAS-INFOPACT
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
