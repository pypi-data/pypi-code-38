__author__ = 'rcj1492'
__created__ = '2018.05'
__license__ = 'MIT'

def extract_domains(certbot_text):
    
    domain_list = []
    
    import re
    from labpack.records.time import labDT
    cert_pattern = re.compile('(\s\sCertificate Name:\s)(.*?)(\n\s+Domains:\s)(.*?)(\n\s+Expiry Date:\s)(.*?)(\s\()', re.S)
    cert_search = cert_pattern.findall(certbot_text)
    if cert_search:
        for cert_tuple in cert_search:
            cert_name = cert_tuple[1]
            cert_expire = labDT.fromISO(cert_tuple[5]).epoch()
            cert_domains = cert_tuple[3].split(' ')
            for domain in cert_domains:
                domain_list.append({'cert': cert_name, 'domain': domain, 'expires': cert_expire})
    
    return domain_list

if __name__ == '__main__':
    
    signup_a = "Enter email address (used for urgent renewal and security notices) (Enter 'c' to cancel):"
    signup_b = "(A)gree/(C)ancel:"
    signup_c = "(Y)es/(N)o:"

    cert_text = 'Found the following certs:\n  Certificate Name: collectiveacuity.com\n    Domains: collectiveacuity.com www.collectiveacuity.com\n    Expiry Date: 2018-08-29 20:45:08+00:00 (VALID: 89 days)\n    Certificate Path: /etc/letsencrypt/live/collectiveacuity.com/fullchain.pem\n    Private Key Path: /etc/letsencrypt/live/collectiveacuity.com/privkey.pem'
    
    certbot_domains = extract_domains(cert_text)
    print(certbot_domains)
