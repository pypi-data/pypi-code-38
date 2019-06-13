import socket
import time
import dns.resolver

def resolve(name, expected_list=None):
  """ Resolve name using standard system name resolution.
  """
  begin = time.time()
  try:
    ip_list = [i.to_text() for i in dns.resolver.query(name, "A")]
    resolution = 200
    status = "OK"
  except dns.resolver.NXDOMAIN:
    resolution = 600
    status = "Cannot resolve the hostname"
    ip_list = []

  resolving_time = time.time() - begin
  # Out put is:
  # TEST IDENTIFIER, NAME, RESOLUTION (200 or 600), Time for resolve,
  # status ("OK" or "Cannot resolve the hostname"), Resolved IP.
  if expected_list is not None and set(expected_list) != set(ip_list):
    status = "UNEXPECTED"
    ip_list = "%s (expected) != %s (found)" % (expected_list, ip_list)
  return ('DNS', name, resolution, resolving_time, status, ip_list)


