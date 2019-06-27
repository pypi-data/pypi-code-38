from __future__ import print_function

import os
import sys
import re
from datetime import datetime, date

import dateutil.parser
import pytz

from burlap import ServiceSatchel
from burlap.constants import *
from burlap.decorators import task
#from burlap import common

# import dateutil.parser
# import pytz
from fabric.api import runs_once, hide

class SSLSatchel(ServiceSatchel):

    name = 'ssl'

    def set_defaults(self):
        self.env.country = '?'
        self.env.state = '?'
        self.env.city = '?'
        self.env.organization = '?'
        self.env.common_name = '?'
        self.env.days = 365
        self.env.length = 4096
        self.env.domain = ''

    @task
    def generate_self_signed_certificate(self, domain='', r=None):
        """
        Generates a self-signed certificate for use in an internal development
        environment for testing SSL pages.

        http://almostalldigital.wordpress.com/2013/03/07/self-signed-ssl-certificate-for-ec2-load-balancer/
        """
        r = self.local_renderer
        r.env.domain = domain or r.env.domain
        assert r.env.domain, 'No SSL domain defined.'
        role = r or self.genv.ROLE or ALL
        ssl_dst = 'roles/%s/ssl' % (role,)
        if not os.path.isdir(ssl_dst):
            os.makedirs(ssl_dst)
        r.env.base_dst = '%s/%s' % (ssl_dst, r.env.domain)
        r.local('openssl req -new -newkey rsa:{ssl_length} '
            '-days {ssl_days} -nodes -x509 '
            '-subj "/C={ssl_country}/ST={ssl_state}/L={ssl_city}/O={ssl_organization}/CN={ssl_domain}" '
            '-keyout {ssl_base_dst}.key -out {ssl_base_dst}.crt')

    @task
    @runs_once
    def generate_csr(self, domain='', r=None):
        """
        Creates a certificate signing request to be submitted to a formal
        certificate authority to generate a certificate.

        Note, the provider may say the CSR must be created on the target server,
        but this is not necessary.
        """
        r = r or self.local_renderer
        r.env.domain = domain or r.env.domain
        role = self.genv.ROLE or ALL
        site = self.genv.SITE or self.genv.default_site
        print('self.genv.default_site:', self.genv.default_site, file=sys.stderr)
        print('site.csr0:', site, file=sys.stderr)
        ssl_dst = 'roles/%s/ssl' % (role,)
        print('ssl_dst:', ssl_dst)
        if not os.path.isdir(ssl_dst):
            os.makedirs(ssl_dst)
        for site, site_data in self.iter_sites():
            print('site.csr1:', site, file=sys.stderr)
            assert r.env.domain, 'No SSL domain defined.'
            r.env.ssl_base_dst = '%s/%s' % (ssl_dst, r.env.domain.replace('*.', ''))
            r.env.ssl_csr_year = date.today().year
            r.local('openssl req -nodes -newkey rsa:{ssl_length} '
                '-subj "/C={ssl_country}/ST={ssl_state}/L={ssl_city}/O={ssl_organization}/CN={ssl_domain}" '
                '-keyout {ssl_base_dst}.{ssl_csr_year}.key -out {ssl_base_dst}.{ssl_csr_year}.csr')

    def get_expiration_date(self, fn):
        """
        Reads the expiration date of a local crt file.
        """
        r = self.local_renderer
        r.env.crt_fn = fn
        with hide('running'):
            ret = r.local('openssl x509 -noout -in {ssl_crt_fn} -dates', capture=True)
        matches = re.findall('notAfter=(.*?)$', ret, flags=re.IGNORECASE)
        if matches:
            return dateutil.parser.parse(matches[0])

    @task
    def list_expiration_dates(self, base='roles/all/ssl'):
        """
        Scans through all local .crt files and displays the expiration dates.
        """
        max_fn_len = 0
        max_date_len = 0
        data = []
        for fn in os.listdir(base):
            fqfn = os.path.join(base, fn)
            if not os.path.isfile(fqfn):
                continue
            if not fn.endswith('.crt'):
                continue
            expiration_date = self.get_expiration_date(fqfn)
            max_fn_len = max(max_fn_len, len(fn))
            max_date_len = max(max_date_len, len(str(expiration_date)))
            data.append((fn, expiration_date))
        print('%s %s %s' % ('Filename'.ljust(max_fn_len), 'Expiration Date'.ljust(max_date_len), 'Expired'))
        now = datetime.now().replace(tzinfo=pytz.UTC)
        for fn, dt in sorted(data):

            if dt is None:
                expired = '?'
            elif dt < now:
                expired = 'YES'
            else:
                expired = 'NO'
            print('%s %s %s' % (fn.ljust(max_fn_len), str(dt).ljust(max_date_len), expired))

    @task
    def verify_certificate_chain(self, base=None, crt=None, csr=None, key=None):
        """
        Confirms the key, CSR, and certificate files all match.
        """
        from burlap.common import get_verbose, print_fail, print_success

        r = self.local_renderer

        if base:
            crt = base + '.crt'
            csr = base + '.csr'
            key = base + '.key'
        else:
            assert crt and csr and key, 'If base not provided, crt and csr and key must be given.'

        assert os.path.isfile(crt)
        assert os.path.isfile(csr)
        assert os.path.isfile(key)

        csr_md5 = r.local('openssl req -noout -modulus -in %s | openssl md5' % csr, capture=True)
        key_md5 = r.local('openssl rsa -noout -modulus -in %s | openssl md5' % key, capture=True)
        crt_md5 = r.local('openssl x509 -noout -modulus -in %s | openssl md5' % crt, capture=True)

        match = crt_md5 == csr_md5 == key_md5

        if self.verbose or not match:
            print('crt:', crt_md5)
            print('csr:', csr_md5)
            print('key:', key_md5)

        if match:
            print_success('Files look good!')
        else:
            print_fail('Files no not match!')
            raise Exception('Files no not match!')

    @task
    def configure(self):
        pass

ssl = SSLSatchel()
