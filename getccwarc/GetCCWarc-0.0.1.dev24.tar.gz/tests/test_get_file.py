from GetCCWarc import CCWarcGet

# content of test_sample.py
WARC_EXPECTED_OUTPUT = b'WARC/1.0\r\nWARC-Type: response\r\nWARC-Date: 2019-05-20T15:18:57Z\r\nWARC-Record-ID: <urn:uuid:f552da3f-71b1-442b-8dd2-82fbd46c26cd>\r\nContent-Length: 855\r\nContent-Type: application/http; msgtype=response\r\nWARC-Warcinfo-ID: <urn:uuid:3886f7ed-3010-4f4a-895e-f1a191272341>\r\nWARC-Concurrent-To: <urn:uuid:e237a4df-a710-4291-be9f-c61321671cf3>\r\nWARC-IP-Address: 34.192.137.75\r\nWARC-Target-URI: https://developers.owler.com/\r\nWARC-Payload-Digest: sha1:MWHHDAOHYBRTCPUVYMFPFKZHEZEVL2CM\r\nWARC-Block-Digest: sha1:MAB23IWDOORL562O5NJ4JWUQR3NDERIV\r\nWARC-Identified-Payload-Type: text/html\r\n\r\nHTTP/1.1 200 OK\r\nServer: openresty/1.13.6.1\r\nDate: Mon, 20 May 2019 15:18:57 GMT\r\nContent-Type: text/html; charset=utf-8\r\nX-Crawler-Transfer-Encoding: chunked\r\nConnection: keep-alive\r\nCache-Control: max-age=0, private, must-revalidate\r\nX-Crawler-Content-Encoding: gzip\r\nETag: W/"c90ece1cef167d514485413b98b70a2a"\r\nStrict-Transport-Security: max-age=15552000\r\nVary: Accept-Encoding\r\nX-Content-Type-Options: nosniff\r\nX-Frame-Options: DENY\r\nX-Request-Id: 96209e61c31cbbed9990dfe16c0ddf16\r\nX-Runtime: 0.047393\r\nX-Served-By: mt02.va.3sca.net\r\nX-XSS-Protection: 1; mode=block\r\n\r\n\r\n<HTML>\r\n\r\n<HEAD>\r\n<TITLE>I moved!!!</TITLE>\r\n<META HTTP-EQUIV="refresh" CONTENT="0;URL=https://www.owler.com/enterprise/">\r\n</HEAD>\r\n\r\n<BODY>\r\n\r\n\r\nYou are being redirected here <a href="https://www.owler.com/enterprise/">https://www.owler.com/enterprise/</a>\r\n\r\n</BODY>\r\n\r\n</HTML>\r\n\r\n'


def test_get_file():
    # You have this form the index
    offset, length, filename = 437157916, 884, \
                               "crawl-data/CC-MAIN-2019-22/segments/1558232256040.41/warc/" \
                               "CC-MAIN-20190520142005-20190520164005-00160.warc.gz"

    text = CCWarcGet.get_warc_file(filename, length, offset, gzip=False)
    assert text == WARC_EXPECTED_OUTPUT
