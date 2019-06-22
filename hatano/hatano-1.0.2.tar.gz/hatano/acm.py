from hatano.util import HatanoError

import boto3


class Cert:
    def __init__(self, domainname):
        self.acm = boto3.client('acm', region_name='us-east-1')
        self.arn = ""
        certs = self.acm.list_certificates()['CertificateSummaryList']
        for c in certs:
            if c["DomainName"] == domainname:
                self.arn = c["CertificateArn"]
                break
        else:
            raise HatanoError("Cert not found")


