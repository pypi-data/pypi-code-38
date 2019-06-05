#coding:utf-8
'''
01, 20150626, add function <toDerFmt> to support certificate file encoding format base64 to der.
'''
from __future__ import (print_function, unicode_literals)
import base64

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Util import number
from utilityhelper.common.util.CertUil import Codeutil
from pyasn1.codec.der import decoder, encoder
from pyasn1_modules import rfc2459


class ValueOnlyBitStringEncoder(encoder.encoder.BitStringEncoder):
    # These methods just do not encode tag and length fields of TLV
    def encodeTag(self, *args): return ''
    def encodeLength(self, *args): return ''
    def encodeValue(*args):
        substrate, isConstructed = encoder.encoder.BitStringEncoder.encodeValue(*args)
        # OCSP-specific hack follows: cut off the "unused bit count"
        # encoded bit-string value.
        return substrate[1:], isConstructed

    def __call__(self, bitStringValue):
        return self.encode(None, bitStringValue, defMode=1, maxChunkSize=0)

valueOnlyBitStringEncoder = ValueOnlyBitStringEncoder()

id = {
    rfc2459.id_at_commonName : 'commonName',                #2.5.4.3  通用名(CN)，设备名称、域名或IP、厂商名称等
    rfc2459.id_at_countryName : 'countryName',              #2.5.4.6  国家(C)  
    rfc2459.id_at_organizationName : 'organizationName',    #2.5.4.10 单位(O)，颁发机构
    rfc2459.id_at_organizationalUnitName : 'organizationalUnitName',  #2.5.4.11 机构名称(OU)，证书类型(OU)           
    rfc2459.id_at_givenName : 'givenName',                  #2.5.4.42
    rfc2459.id_at_stateOrProvinceName: "stateOrProvinceName",
    rfc2459.id_at_localityName : 'localityName',
    
    # Algorithm OIDs and parameter structures
    rfc2459.pkcs_1 : "pkcs_1",                                  #('1.2.840.113549.1.1')
    rfc2459.rsaEncryption: "rsaEncryption",                     #= univ.ObjectIdentifier('1.2.840.113549.1.1.1')
    rfc2459.md2WithRSAEncryption : "md2WithRSAEncryption",      #= univ.ObjectIdentifier('1.2.840.113549.1.1.2')
    rfc2459.md5WithRSAEncryption : "md5WithRSAEncryption",      #= univ.ObjectIdentifier('1.2.840.113549.1.1.4')
    rfc2459.sha1WithRSAEncryption : "sha1WithRSAEncryption",    #= univ.ObjectIdentifier('1.2.840.113549.1.1.5')
    rfc2459.id_dsa_with_sha1 : "id_dsa_with_sha1",               #= univ.ObjectIdentifier('1.2.840.10040.4.3')    
}
        
class Cert(object):
    
    def __init__(self, cert, isfile=False):
        if isfile:
            f = open(cert, "rb")
            cert = f.read()
            f.close()
        certType = rfc2459.Certificate()
        self.cert, rest = decoder.decode(cert, asn1Spec=certType)
        
#         print "===========GetSubjectDN=============="
#         self.GetSubjectDN()
#         print "===========GetSubjectOU=============="
#         print "OU=",self.GetSubjectOU()
#         print "===========GetIssuerX500Principal============"
#         print "Issuer:",self.GetIssuerX500Principal()
        
    def AnalysisRDNSequence(self, RDNSequence):
        psList = {}
        OUCount = 0
        for RelativeDistinguishedName in RDNSequence:
            RDN = RelativeDistinguishedName[0]  #类实例，pyasn1_modules.rfc2459.AttributeTypeAndValue
            AttributeType = RDN['type']         #类实例，pyasn1_modules.rfc2459.AttributeType
            AttributeValue = RDN['value']       #类实例，pyasn1_modules.rfc2459.AttributeValue
            valList = decoder.decode(AttributeValue)
            ps = str(valList[0])    # pyasn1.type.char.PrintableString
            av = valList[1]         # pyasn1_modules.rfc2459.AttributeValue
            #print "ps=", ps
            #print "av=", av
            if(AttributeType == rfc2459.id_at_organizationalUnitName):
                OUCount += 1
                if(OUCount == 1):
                    psList['OU1'] = ps
                    continue
                elif(OUCount == 2):
                    psList['OU2'] = ps
                    continue
            psList[id[AttributeType]] = ps
        return psList        
        
    def GetVersion(self):
        version = self.cert['tbsCertificate']['version']
        return version
    
    def GetSerialNumber(self):
        serialNumberInt = self.cert['tbsCertificate']['serialNumber']
        serialNumberBytes = number.long_to_bytes(serialNumberInt)
        serialNumberHex = Codeutil.toHexString(serialNumberBytes)
        return serialNumberHex

    def GetIssuerX500Principal(self):
        IssuerDic = {}
        RDNSequence = self.cert['tbsCertificate']['issuer'][0]
        IssuerDic = self.AnalysisRDNSequence(RDNSequence)
        return IssuerDic
        
    def GetTbsCertificate(self):
        return encoder.encode(self.cert['tbsCertificate'])
    
    def GetCertSign(self):
        SigAlgDic = {}
        signatureAlgorithm = self.cert['signatureAlgorithm']
        algorithm = signatureAlgorithm['algorithm']
        signatureValue = self.cert['signatureValue']
        SigAlgDic['oid'] = str(algorithm)   #获取证书的签名算法 OID 字符串
        SigAlgDic['name'] = id[algorithm]   #获取证书签名算法的签名算法名
        SigAlgDic['value'] = Codeutil.toHexString(valueOnlyBitStringEncoder(signatureValue))
        return SigAlgDic
        
    def GetSignature(self):
        return valueOnlyBitStringEncoder(self.cert['signatureValue'])
    
    def GetSignatureValue(self):
        return encoder.encode(self.cert['signatureValue'])
        
    def GetSubjectPublicKeyInfo(self):
        SPKIDic = {}
        spki = self.cert['tbsCertificate']['subjectPublicKeyInfo']
        algorithmTupe = spki['algorithm']
        pubkey = spki['subjectPublicKey']
        
        algType = algorithmTupe[0]
        SPKIDic['algorithm'] = id[algType]  #加密算法
        
        pk = valueOnlyBitStringEncoder(pubkey)
        pkSeqenceTuple = decoder.decode(pk)
        modulus = number.long_to_bytes(pkSeqenceTuple[0][0])        #n
        publicExponent = number.long_to_bytes(pkSeqenceTuple[0][1]) #e
        SPKIDic['n'] = Codeutil.toHexString(modulus)
        SPKIDic['e'] = Codeutil.toHexString(publicExponent)
        return SPKIDic
        
    def GetPublicKey(self):
        spki = self.cert['tbsCertificate']['subjectPublicKeyInfo']
        return valueOnlyBitStringEncoder(spki['subjectPublicKey'])
    
    def GetSubjectDN(self):
        RDNSequence = self.cert['tbsCertificate']['subject'][0]
        DNDic = {}
        DNDic = self.AnalysisRDNSequence(RDNSequence)
        return DNDic 
    
    def GetSubjectOU(self):
        DNDic = self.GetSubjectDN()
        return DNDic['OU1']
        
    def VerifyCert(self, CACert):
        ohash = SHA.new(self.GetTbsCertificate()).digest()
        cakey = RSA.importKey(CACert.GetSubjectPublicKeyInfo())
        shash = cakey.encrypt(self.GetSignature(),'')[0]
        if ohash == shash[-20:]:
            return True
            
        return False
    
def toDerFmt(input):
    '''@input --certficate file data to be transfer
        base64-->der
    '''
    
    file_start_flag = "-----BEGIN CERTIFICATE-----"
    file_end_flag = "-----END CERTIFICATE-----"
    
    #base64 format
    s_index = input.find(file_start_flag)
    if s_index == 0:
        e_index = input.find(file_end_flag)
        if(e_index != -1):
            data = input[s_index + len(file_start_flag) : e_index]
            output = base64.decodestring(data)
        else:
            return None
    else:
    #not base64 format
        output = input
    return output
    
