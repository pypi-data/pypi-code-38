from zope import interface as zope_interface
from slapos.grid.promise import interface
from slapos.grid.promise.generic import GenericPromise, TestResult
import re
import time
from slapos.networkbench.ping import ping, ping6

class RunPromise(GenericPromise):

  zope_interface.implements(interface.IPromise)

  def __init__(self, config):
    GenericPromise.__init__(self, config)
    # set periodicity to run the promise twice per day
    self.custom_frequency = int(self.getConfig('frequency', 720))
    self.setPeriodicity(self.custom_frequency)
    # Skip test check on this promise
    self.setTestLess()

  def sense(self):
    """
      Check re6st optimal status
    """
    # promise ipv6 and ipv4 address to compare.
    ipv4 = self.getConfig('ipv4')
    ipv6 = self.getConfig('ipv6')
    count = int(self.getConfig('count', 10))
    if not ipv4:
      raise ValueError("'ipv4' was not set in promise parameters.")
    if not ipv6:
      raise ValueError("'ipv6' was not set in promise parameters.")

    result_ipv4 = ping(ipv4, count=count)
    result_ipv6 = ping6(ipv6, count=count)
    # push into to the log file
    self.logger.info("%s host=%s code=%s, result=%s, packet_lost_ratio=%s msg=%s" % result_ipv4)
    self.logger.info("%s host=%s code=%s, result=%s, packet_lost_ratio=%s msg=%s" % result_ipv6)

    if result_ipv4[3] == "failed" and result_ipv6[3] != "failed":
      # IPv4 is unreacheable
      self.logger.info("OK: IPv4 unreachable, IPv6 reachable")
      return

    if result_ipv6[3] == "failed":
      # IPv6 is unreacheable
      self.logger.error("FAILED: IPv4 reachable, IPv6 unreachable")
      return

    latency4 = float(result_ipv4[3])
    latency6 = float(result_ipv6[3])
    # We can consider that at worst 1ms is added to
    # ipv4 response, due the usage of openvpn.
    acceptable_delay = int(self.getConfig('acceptable-delay', 1))
    # We can consider that we accept a certain increase
    # on latency, if we are on a bit congested link.
    # So 10% is reseonable enough.
    acceptable_lost = int(self.getConfig('acceptable-lost', 0.10))
    # Increase latency with the value.
    latency4 += acceptable_delay + latency4 * acceptable_lost
    if latency4 < latency6:
      self.logger.error("FAIL %s (latency4) > %s (latence6)" % (latency4, latency6))
    else:
      # Compare if both has Same working rate
      self.logger.info("OK: IPv4 reachable, IPv6 reachable")

  def anomaly(self):
    # only check the result of the two latest sense call
    return self._test(result_count=2, failure_amount=2, latest_minute=self.custom_frequency*3)
