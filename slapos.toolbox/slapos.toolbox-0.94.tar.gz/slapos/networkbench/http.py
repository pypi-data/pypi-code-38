import sys
import pycurl
from StringIO import StringIO

def get_curl(buffer, url):
  curl = pycurl.Curl()
  curl.setopt(curl.URL, url)
  curl.setopt(curl.CONNECTTIMEOUT, 10)
  curl.setopt(curl.TIMEOUT, 30)
  curl.setopt(curl.WRITEDATA, buffer)
  curl.setopt(curl.SSL_VERIFYPEER, False)
  curl.setopt(curl.SSL_VERIFYHOST, False)
  result = "OK"
  try:
    curl.perform()
  except:
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    result = "FAIL"
  return curl, result

def request(url, expected_dict):
  
  buffer = StringIO()
  curl, result = get_curl(buffer, url)

  body = buffer.getvalue()
  
  rendering_time = "%s;%s;%s;%s;%s" % \
    (curl.getinfo(curl.NAMELOOKUP_TIME),
     curl.getinfo(curl.CONNECT_TIME),
     curl.getinfo(curl.PRETRANSFER_TIME),
     curl.getinfo(curl.STARTTRANSFER_TIME),
     curl.getinfo(curl.TOTAL_TIME))
  
  response_code = curl.getinfo(pycurl.HTTP_CODE)

  expected_response = expected_dict.get("expected_response", None)
  if expected_response is not None and \
      expected_response != response_code:
    result = "UNEXPECTED (%s != %s)" % (expected_response, response_code)

  expected_text = expected_dict.get("expected_text", None)
  if expected_text is not None and \
      str(expected_text) not in str(body):
    result = "UNEXPECTED (%s not in page content)" % (expected_text)

  curl.close()

  info_list = ('GET', url, response_code, rendering_time, result)

  return info_list

