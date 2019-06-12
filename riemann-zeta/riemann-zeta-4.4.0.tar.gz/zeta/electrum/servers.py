# flake8: noqa

import os

from typing import Any, Dict, List

null = None  # NB: I copied the list from elsewhere

SERVERS: Dict[str, List[Dict[str, Any]]] = {
    'bitcoin_test': [
        {
         "nickname": null,
         "hostname": "testnet.qtornado.com",
         "ip_addr": null,
         "ports": [
          "s51002"
         ],
         "version": "1.4",
         "pruning_limit": 0,
         "seen_at": 1533670768.8676639
        }
        # {
        #  "nickname": null,
        #  "hostname": "testnet.hsmiths.com",
        #  "ip_addr": null,
        #  "ports": [
        #   "s53012"
        #  ],
        #  "version": "1.4",
        #  "pruning_limit": 0,
        #  "seen_at": 1533670768.8676639
        # }
      ],
    'bitcoin_main': [
      {
       "nickname": null,
       "hostname": "104.250.141.242",
       "ip_addr": null,
       "ports": [
        "s50002"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.8676639
      },
      {
       "nickname": null,
       "hostname": "134.119.179.55",
       "ip_addr": null,
       "ports": [
        "s50002"
       ],
       "version": "1.0",
       "pruning_limit": 0,
       "seen_at": 1533670768.731586
      },
      {
       "nickname": null,
       "hostname": "139.162.14.142",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.8676212
      },
      {
       "nickname": null,
       "hostname": "165.227.22.180",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.867455
      },
      {
       "nickname": null,
       "hostname": "3smoooajg7qqac2y.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867671
      },
      {
       "nickname": null,
       "hostname": "3tm3fjg3ds5fcibw.onion",
       "ip_addr": null,
       "ports": [
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867779
      },
      {
       "nickname": "electroli",
       "hostname": "46.166.165.18",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.945237
      },
      {
       "nickname": null,
       "hostname": "4cii7ryno5j3axe4.onion",
       "ip_addr": null,
       "ports": [
        "t50001"
       ],
       "version": "1.2",
       "pruning_limit": 0,
       "seen_at": 1533670768.86764
      },
      {
       "nickname": null,
       "hostname": "4yi77lkjgy4bwtj3.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.86769
      },
      {
       "nickname": null,
       "hostname": "7jwtirwsaogb6jv2.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.2",
       "pruning_limit": 0,
       "seen_at": 1533670768.8675048
      },
      {
       "nickname": null,
       "hostname": "abc1.hsmiths.com",
       "ip_addr": "76.174.26.91",
       "ports": [
        "s60002",
        "t60001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.584984
      },
      {
       "nickname": null,
       "hostname": "alviss.coinjoined.com",
       "ip_addr": "94.130.136.185",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.867656
      },
      {
       "nickname": "antumbra",
       "hostname": "antumbra.se",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.022753
      },
      {
       "nickname": "j_fdk_b",
       "hostname": "b.1209k.com",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.020474
      },
      {
       "nickname": null,
       "hostname": "bauerjda5hnedjam.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867549
      },
      {
       "nickname": null,
       "hostname": "Bitcoin-node.nl",
       "ip_addr": "82.217.214.215",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.867786
      },
      {
       "nickname": null,
       "hostname": "bitcoin.corgi.party",
       "ip_addr": "176.223.139.65",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867529
      },
      {
       "nickname": null,
       "hostname": "bitcoin.grey.pw",
       "ip_addr": "173.249.8.197",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.8676748
      },
      {
       "nickname": null,
       "hostname": "bitcoin3nqy3db7c.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867647
      },
      {
       "nickname": null,
       "hostname": "btc.cihar.com",
       "ip_addr": "78.46.177.74",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.759933
      },
      {
       "nickname": null,
       "hostname": "btc.gravitech.net",
       "ip_addr": "37.187.167.132",
       "ports": [
        "s50002"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.86759
      },
      {
       "nickname": "mustyoshi",
       "hostname": "btc.mustyoshi.com",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.945437
      },
      {
       "nickname": null,
       "hostname": "btc.outoftime.co",
       "ip_addr": "121.44.121.158",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867712
      },
      {
       "nickname": "selavi",
       "hostname": "btc.smsys.me",
       "ip_addr": null,
       "ports": [
        "t110",
        "s995"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.021612
      },
      {
       "nickname": "cplus",
       "hostname": "btc1.commerce-plus.com",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.96599
      },
      {
       "nickname": "clueless",
       "hostname": "cluelessperson.com",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.021714
      },
      {
       "nickname": "condor1003",
       "hostname": "condor1003.server4you.de",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.945338
      },
      {
       "nickname": null,
       "hostname": "currentlane.lovebitco.in",
       "ip_addr": "88.198.91.74",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.8676338
      },
      {
       "nickname": null,
       "hostname": "daedalus.bauerj.eu",
       "ip_addr": "84.200.105.74",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.8677042
      },
      {
       "nickname": null,
       "hostname": "dxm.no-ip.biz",
       "ip_addr": "78.51.123.122",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.628011
      },
      {
       "nickname": null,
       "hostname": "e-1.claudioboxx.com",
       "ip_addr": "37.61.209.146",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.8677719
      },
      {
       "nickname": null,
       "hostname": "e-2.claudioboxx.com",
       "ip_addr": "37.61.209.147",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867769
      },
      {
       "nickname": null,
       "hostname": "e-4.claudioboxx.com",
       "ip_addr": "134.119.179.67",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.8678012
      },
      {
       "nickname": null,
       "hostname": "E-X.not.fyi",
       "ip_addr": "170.130.28.174",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.86766
      },
      {
       "nickname": "ECDSA",
       "hostname": "ecdsa.net",
       "ip_addr": null,
       "ports": [
        "t",
        "s110"
       ],
       "version": "1.0",
       "pruning_limit": 100,
       "seen_at": 1465686119.02029
      },
      {
       "nickname": "fydel",
       "hostname": "ele.einfachmalnettsein.de",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.022509
      },
      {
       "nickname": "Luggs",
       "hostname": "elec.luggs.co",
       "ip_addr": "95.211.185.14",
       "ports": [
        "s443"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867761
      },
      {
       "nickname": "Pielectrum",
       "hostname": "ELEC.Pieh0.co.uk",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.022244
      },
      {
       "nickname": "trouth_eu",
       "hostname": "electrum-europe.trouth.net",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.040206
      },
      {
       "nickname": null,
       "hostname": "electrum-unlimited.criptolayer.net",
       "ip_addr": "188.40.93.205",
       "ports": [
        "s50002"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.696258
      },
      {
       "nickname": "molec",
       "hostname": "electrum.0x0000.de",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.966419
      },
      {
       "nickname": "anonymized1",
       "hostname": "electrum.anonymized.io",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.020339
      },
      {
       "nickname": null,
       "hostname": "electrum.dk",
       "ip_addr": "92.246.24.225",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.867573
      },
      {
       "nickname": "DragonZone",
       "hostname": "electrum.dragonzone.net",
       "ip_addr": null,
       "ports": [
        "t",
        "h",
        "s",
        "g"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.966315
      },
      {
       "nickname": null,
       "hostname": "electrum.eff.ro",
       "ip_addr": "185.36.252.200",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867525
      },
      {
       "nickname": null,
       "hostname": "electrum.festivaldelhumor.org",
       "ip_addr": "173.212.247.250",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.8674629
      },
      {
       "nickname": "hsmiths",
       "hostname": "electrum.hsmiths.com",
       "ip_addr": "76.174.26.91",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867747
      },
      {
       "nickname": null,
       "hostname": "electrum.infinitum-nihil.com",
       "ip_addr": "192.30.120.110",
       "ports": [
        "s50002"
       ],
       "version": "1.0",
       "pruning_limit": 0,
       "seen_at": 1533670768.73193
      },
      {
       "nickname": "JWU42",
       "hostname": "ELECTRUM.jdubya.info",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 1000,
       "seen_at": 1465686119.022112
      },
      {
       "nickname": null,
       "hostname": "electrum.leblancnet.us",
       "ip_addr": "69.27.173.238",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867794
      },
      {
       "nickname": "RMevaere",
       "hostname": "electrum.mevaere.fr",
       "ip_addr": null,
       "ports": [
        "t0",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.945171
      },
      {
       "nickname": "neocrypto",
       "hostname": "electrum.neocrypto.io",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.021477
      },
      {
       "nickname": "netpros",
       "hostname": "electrum.netpros.co",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.020614
      },
      {
       "nickname": "NOIP",
       "hostname": "electrum.no-ip.org",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.020677
      },
      {
       "nickname": "Online",
       "hostname": "Electrum.Online",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.020231
      },
      {
       "nickname": null,
       "hostname": "electrum.qtornado.com",
       "ip_addr": "88.99.162.199",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.8676858
      },
      {
       "nickname": "faro",
       "hostname": "electrum.site2.me",
       "ip_addr": null,
       "ports": [
        "t40001",
        "s40002"
       ],
       "version": "1.0",
       "pruning_limit": 100,
       "seen_at": 1465686119.020781
      },
      {
       "nickname": "Snipa",
       "hostname": "electrum.snipanet.com",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.021272
      },
      {
       "nickname": "stoff-sammlung",
       "hostname": "electrum.stoff-sammlung.de",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.966188
      },
      {
       "nickname": "gORlECTRUM",
       "hostname": "ELECTRUM.top-master.com",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.020941
      },
      {
       "nickname": "trouth",
       "hostname": "electrum.trouth.net",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.02263
      },
      {
       "nickname": "dogydins",
       "hostname": "electrum.villocq.com",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.040277
      },
      {
       "nickname": "eniac",
       "hostname": "electrum0.snel.it",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.94539
      },
      {
       "nickname": null,
       "hostname": "electrumx.bot.nu",
       "ip_addr": "173.91.90.62",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867776
      },
      {
       "nickname": null,
       "hostname": "electrumx.nmdps.net",
       "ip_addr": "109.61.102.5",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867459
      },
      {
       "nickname": "Pielectrum_TOR",
       "hostname": "electrumx67xeros.onion",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.944136
      },
      {
       "nickname": null,
       "hostname": "electrumxhqdsmlu.onion",
       "ip_addr": null,
       "ports": [
        "t50001"
       ],
       "version": "1.2",
       "pruning_limit": 0,
       "seen_at": 1533670768.628143
      },
      {
       "nickname": "j_fdk_b_tor",
       "hostname": "fdkbwjykvl2f3hup.onion",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.020525
      },
      {
       "nickname": "j_fdk_h_tor",
       "hostname": "fdkhv2bb7hqel2e7.onion",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.021149
      },
      {
       "nickname": "electron",
       "hostname": "gh05.geekhosters.com",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.945288
      },
      {
       "nickname": "j_fdk_h",
       "hostname": "h.1209k.com",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.020997
      },
      {
       "nickname": null,
       "hostname": "helicarrier.bauerj.eu",
       "ip_addr": "178.32.88.133",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867583
      },
      {
       "nickname": null,
       "hostname": "hsmiths4fyqlw5xw.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867569
      },
      {
       "nickname": null,
       "hostname": "hsmiths5mjk6uijs.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.86774
      },
      {
       "nickname": "DEVV",
       "hostname": "ilikehuskies.no-ip.org",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.022576
      },
      {
       "nickname": null,
       "hostname": "ip101.ip-54-37-91.eu",
       "ip_addr": "54.37.91.101",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.696357
      },
      {
       "nickname": null,
       "hostname": "ip119.ip-54-37-91.eu",
       "ip_addr": "54.37.91.119",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.867723
      },
      {
       "nickname": null,
       "hostname": "ip120.ip-54-37-91.eu",
       "ip_addr": "54.37.91.120",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.867553
      },
      {
       "nickname": null,
       "hostname": "ip239.ip-54-36-234.eu",
       "ip_addr": "54.36.234.239",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.867719
      },
      {
       "nickname": "fydel_tor",
       "hostname": "ixxdq23ewy77sau6.onion",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.02234
      },
      {
       "nickname": null,
       "hostname": "iy5jbpzok4spzetr.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867765
      },
      {
       "nickname": "JWU42[b]",
       "hostname": "jwu42.hopto.org",
       "ip_addr": null,
       "ports": [
        "t50003",
        "s50004"
       ],
       "version": "1.0",
       "pruning_limit": 1000,
       "seen_at": 1465686119.022186
      },
      {
       "nickname": null,
       "hostname": "kirsche.emzy.de",
       "ip_addr": "78.47.61.83",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867726
      },
      {
       "nickname": null,
       "hostname": "liyqfqfsiewcsumb.onion",
       "ip_addr": null,
       "ports": [
        "s50003",
        "t50001"
       ],
       "version": "1.2",
       "pruning_limit": 0,
       "seen_at": 1533670768.867557
      },
      {
       "nickname": null,
       "hostname": "luggscoqbymhvnkp.onion",
       "ip_addr": null,
       "ports": [
        "t80"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.8674839
      },
      {
       "nickname": "j_fdk_mash_tor",
       "hostname": "mashtk6hmnysevfj.onion",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.021092
      },
      {
       "nickname": null,
       "hostname": "ndnd.selfhost.eu",
       "ip_addr": "217.233.81.39",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.86773
      },
      {
       "nickname": null,
       "hostname": "ndndword5lpb7eex.onion",
       "ip_addr": null,
       "ports": [
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867682
      },
      {
       "nickname": null,
       "hostname": "orannis.com",
       "ip_addr": "50.35.67.146",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867517
      },
      {
       "nickname": "selavi_tor",
       "hostname": "ozahtqwp25chjdjd.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.628438
      },
      {
       "nickname": null,
       "hostname": "qtornadoklbgdyww.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.628462
      },
      {
       "nickname": null,
       "hostname": "rbx.curalle.ovh",
       "ip_addr": "176.31.252.219",
       "ports": [
        "s50002"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867744
      },
      {
       "nickname": "cplus_tor",
       "hostname": "rvm6c7kj63mtztgn.onion",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.965912
      },
      {
       "nickname": null,
       "hostname": "ryba-btc.noip.pl",
       "ip_addr": "109.199.70.182",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.86748
      },
      {
       "nickname": null,
       "hostname": "rybabtcmltnlykbd.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867521
      },
      {
       "nickname": null,
       "hostname": "s7clinmo4cazmhul.onion",
       "ip_addr": null,
       "ports": [
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867476
      },
      {
       "nickname": null,
       "hostname": "such.ninja",
       "ip_addr": "163.172.61.154",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.867708
      },
      {
       "nickname": null,
       "hostname": "tardis.bauerj.eu",
       "ip_addr": "51.15.138.64",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.867758
      },
      {
       "nickname": "ulrichard",
       "hostname": "ulrichard.ch",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 10000,
       "seen_at": 1465686119.020178
      },
      {
       "nickname": "ECO",
       "hostname": "ultra-ecoelectrum.my-gateway.de",
       "ip_addr": null,
       "ports": [
        "t",
        "s"
       ],
       "version": "1.0",
       "pruning_limit": 100,
       "seen_at": 1465686119.020727
      },
      {
       "nickname": "US",
       "hostname": "us.electrum.be",
       "ip_addr": "208.110.73.107",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.494337
      },
      {
       "nickname": "hsmiths2",
       "hostname": "VPS.hsmiths.com",
       "ip_addr": "51.15.77.78",
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.8675961
      },
      {
       "nickname": null,
       "hostname": "wsw6tua3xl24gsmi264zaep6seppjyrkyucpsmuxnjzyt3f3j6swshad.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.4",
       "pruning_limit": 0,
       "seen_at": 1533670768.86779
      },
      {
       "nickname": null,
       "hostname": "y4td57fxytoo5ki7.onion",
       "ip_addr": null,
       "ports": [
        "s50002",
        "t50001"
       ],
       "version": "1.1",
       "pruning_limit": 0,
       "seen_at": 1533670768.867754
      }
     ]
}
