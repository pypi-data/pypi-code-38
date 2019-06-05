#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from ezdnsbl.classes import DNSBLResults

# To-Do:
# add http://www.barracudacentral.org/rbl/
# add http://wiki.ctyme.com/index.php/Spam_DNS_Lists
# add everything in https://github.com/vincecarney/dnsbl/blob/master/providers.py


def main():
    if len(sys.argv) > 1:
        print(DNSBLResults(sys.argv[1], auth_tokens={'HTTPBL': sys.argv[2]}))
    else:
        import code
        code.interact(local=dict(globals(), **locals()))


if __name__ == '__main__':
    main()
