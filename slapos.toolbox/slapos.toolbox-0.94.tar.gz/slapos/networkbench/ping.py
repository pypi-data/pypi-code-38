import subprocess
import re

# rtt min/avg/max/mdev = 1.102/1.493/2.203/0.438 ms
ping_re = re.compile(
    ".*"
    "(?P<min>[\d\.]+)/"
    "(?P<avg>[\d\.]+)/"
    "(?P<max>[\d\.]+)/"
    "(?P<mdev>[\d\.]+) ms"
    )

date_reg_exp = re.compile('\d{4}[-/]\d{2}[-/]\d{2}')


def ping(host, timeout=10, protocol="4", count=10):
  if protocol == '4':
    ping_bin = 'ping'
    test_title = 'PING'
  elif protocol == '6':
    ping_bin = 'ping6'
    test_title = 'PING6'

  proc = subprocess.Popen((ping_bin, '-c', str(count), '-w', str(timeout), host),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  out, err = proc.communicate()
  if 'Network is unreachable' in err:
    return (test_title, host, 600, 'failed', 100, "Network is unreachable")
  try:
    packet_loss_line, summary_line = (out.splitlines() or [''])[-2:]
  except:
    return (test_title, host, 600, 'failed', -1, "Fail to parser ping output")
  m = ping_re.match(summary_line)
  match = re.search('(\d*)% packet loss', packet_loss_line)
  packet_lost_ratio = match.group(1)

  info_list = (test_title, host, 600, 'failed', packet_lost_ratio, "Cannot ping host")
  if packet_lost_ratio != 0:
    if m:
      info_list = (test_title, host, 200, m.group('avg'), packet_lost_ratio,
           'min %(min)s max %(max)s avg %(avg)s' % m.groupdict())
  else:
    info_list = (test_title, host, 600, 'failed', packet_lost_ratio,
      "You have package Lost")

  return info_list

def ping6(host, timeout=10, count=10):
  return ping(host, timeout=10, protocol='6', count=count)

