"""
Network
=======
"""

from fabric.api import hide, run, settings, sudo

from burlap.files import file # pylint: disable=redefined-builtin

is_file = file.is_file


def interfaces():
    """
    Get the list of network interfaces. Will return all datalinks on SmartOS.
    """
    with settings(hide('running', 'stdout')):
        if is_file('/usr/sbin/dladm'):
            res = run('/usr/sbin/dladm show-link')
        else:
            res = sudo('/sbin/ifconfig -s')
    return [line.split(' ')[0] for line in res.splitlines()[1:]]


def address(interface):
    """
    Get the IPv4 address assigned to an interface.

    Example::

        import burlap

        # Print all configured IP addresses
        for interface in burlap.network.interfaces():
            print(burlap.network.address(interface))

    """
    with settings(hide('running', 'stdout')):
        res = (sudo("/sbin/ifconfig %(interface)s | grep 'inet '" % locals()) or '').split('\n')[-1].strip()
    if 'addr' in res:
        return res.split()[1].split(':')[1]
    return res.split()[1]


def nameservers():
    """
    Get the list of nameserver addresses.

    Example::

        import burlap

        # Check that all name servers are reachable
        for ip in burlap.network.nameservers():
            run('ping -c1 %s' % ip)

    """
    with settings(hide('running', 'stdout')):
        res = run(r"cat /etc/resolv.conf | grep 'nameserver' | cut -d\  -f2")
    return res.splitlines()
