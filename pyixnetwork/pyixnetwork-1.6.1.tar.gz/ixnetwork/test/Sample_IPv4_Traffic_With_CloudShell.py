
import sys
import time

from cloudshell.api.cloudshell_api import CloudShellAPISession


class TestFailedError(Exception):
    pass


class Py:
    pass


def get_reservation_resource(session, reservation_id, model_name):

    reservation_resource = []
    reservation = session.GetReservationDetails(reservation_id).ReservationDescription
    for resource in reservation.Resources:
        if resource.ResourceModelName == model_name:
            reservation_resource.append(resource)
    return reservation_resource


def reserve_abstract_blueprint():
    global reservation_id
    reservation = session.CreateImmediateTopologyReservation('Ixia demo for regression', 'admin', 60, False, False, 0,
                                                             'Ixia demo for regression', [], [], [])
    reservation_id = reservation.Reservation.Id
    ports = get_reservation_resource(session, reservation_id, 'Generic Traffic Generator Port')
    controller = session.GetReservationDetails(reservation_id).ReservationDescription.Services[0]
    return controller, ports


session = CloudShellAPISession('localhost', 'admin', 'admin', 'Global')

py = Py()
controller, ports = reserve_abstract_blueprint()
py.ports = [ports[0].FullAddress.replace('/M', ' ').replace('/P', ' ').split(),
            ports[1].FullAddress.replace('/M', ' ').replace('/P', ' ').split()]
py.ixInstallPath = controller.Attributes[0].Value
py.ixTclServer = controller.Attributes[1].Value if controller.Attributes[1].Value else 'localhost'
py.ixTclPort = controller.Attributes[2].Value if controller.Attributes[2].Value else 8009

################################################################################
# Import the IxNet library based on requested version.
################################################################################
sys.path.append(py.ixInstallPath + '/API/Python')
from IxNetwork import IxNet  # nopep8


################################################################################
# Connect to IxNet client
################################################################################
ixNet = IxNet()
ixNet.connect(py.ixTclServer, '-port', py.ixTclPort, '-version', '8.01')

################################################################################
# Cleaning up IxNetwork
################################################################################
print "Cleaning up IxNetwork..."
ixNet.execute('newConfig')

################################################################################
# Adding ports to configuration
################################################################################
print "Adding ports to configuration"
root = ixNet.getRoot()
ixNet.add(root, 'vport')
ixNet.add(root, 'vport')
ixNet.commit()
vPorts = ixNet.getList(root, 'vport')
vport1 = vPorts[0]
vport2 = vPorts[1]

################################################################################
# Configuring IPv4 Endpoints
################################################################################
print "Add topologies"
ixNet.add(root, 'topology')
ixNet.add(root, 'topology')
ixNet.commit()

topo1 = ixNet.getList(root, 'topology')[0]
topo2 = ixNet.getList(root, 'topology')[1]

print "Add ports to topologies"
ixNet.setAttribute(topo1, '-vports', vport1)
ixNet.setAttribute(topo2, '-vports', vport2)
ixNet.commit()

print "Add device groups to topologies"
ixNet.add(topo1, 'deviceGroup')
ixNet.add(topo2, 'deviceGroup')
ixNet.commit()

dg1 = ixNet.getList(topo1, 'deviceGroup')[0]
dg2 = ixNet.getList(topo2, 'deviceGroup')[0]

print "Add ethernet stacks to device groups"
ixNet.add(dg1, 'ethernet')
ixNet.add(dg2, 'ethernet')
ixNet.commit()

mac1 = ixNet.getList(dg1, 'ethernet')[0]
mac2 = ixNet.getList(dg2, 'ethernet')[0]

print "Add ipv4 stacks to Ethernets"
ixNet.add(mac1, 'ipv4')
ixNet.add(mac2, 'ipv4')
ixNet.commit()

ipv4_1 = ixNet.getList(mac1, 'ipv4')[0]
ipv4_2 = ixNet.getList(mac2, 'ipv4')[0]

print "Setting multi values for ipv4 addresses"
ixNet.setMultiAttribute(ixNet.getAttribute(ipv4_1, '-address') + '/counter', '-start', '22.1.1.1', '-step', '0.0.1.0')
ixNet.setMultiAttribute(ixNet.getAttribute(ipv4_1, '-gatewayIp') + '/counter', '-start', '22.1.1.2', '-step', '0.0.1.0')  # nopep8
ixNet.setMultiAttribute(ixNet.getAttribute(ipv4_1, '-resolveGateway') + '/singleValue', '-value', 'true')
ixNet.setMultiAttribute(ixNet.getAttribute(ipv4_2, '-address') + '/counter', '-start', '22.1.1.2', '-step', '0.0.1.0')
ixNet.setMultiAttribute(ixNet.getAttribute(ipv4_2, '-gatewayIp') + '/counter', '-start', '22.1.1.1', '-step', '0.0.1.0')  # nopep8
ixNet.setMultiAttribute(ixNet.getAttribute(ipv4_2, '-resolveGateway') + '/singleValue', '-value', 'true')
ixNet.commit()

################################################################################
# Creating Traffic for IPv4
################################################################################
print ''
print "Creating Traffic for IPv4"

ixNet.add(ixNet.getRoot() + '/traffic', 'trafficItem')
ixNet.commit()
ti1 = ixNet.getList(ixNet.getRoot() + '/traffic', 'trafficItem')[0]
ixNet.setMultiAttribute(ti1,
                        '-name', 'Traffic IPv4',
                        '-trafficType', 'ipv4',
                        '-allowSelfDestined', False,
                        '-trafficItemType', 'l2L3',
                        '-mergeDestinations', True,
                        '-egressEnabled', False,
                        '-srcDestMesh', 'manyToMany',
                        '-enabled', True,
                        '-routeMesh', 'fullMesh',
                        '-transmitMode', 'interleaved',
                        '-biDirectional', True,
                        '-hostsPerNetwork', 1)
ixNet.commit()
ixNet.setAttribute(ti1, '-trafficType', 'ipv4')
ixNet.commit()
ixNet.add(ti1, 'endpointSet',
          '-sources', ipv4_1,
          '-destinations', ipv4_2,
          '-name', 'ep-set1',
          '-sourceFilter', '',
          '-destinationFilter', '')
ixNet.commit()
ixNet.setMultiAttribute(ti1 + "/configElement:1/frameSize",
                        '-type', 'fixed',
                        '-fixedSize', 128)
ixNet.setMultiAttribute(ti1 + "/configElement:1/frameRate",
                        '-type', 'percentLineRate',
                        '-rate', 10)
ixNet.setMultiAttribute(ti1 + "/configElement:1/transmissionControl",
                        '-duration', 1,
                        '-iterationCount', 1,
                        '-startDelayUnits', 'bytes',
                        '-minGapBytes', 12,
                        '-frameCount', 10000,
                        '-type', 'fixedFrameCount',
                        '-interBurstGapUnits', 'nanoseconds',
                        '-interBurstGap', 0,
                        '-enableInterBurstGap', False,
                        '-interStreamGap', 0,
                        '-repeatBurst', 1,
                        '-enableInterStreamGap', False,
                        '-startDelay', 0,
                        '-burstPacketCount', 1,)
ixNet.setMultiAttribute(ti1 + "/tracking", '-trackBy', ['sourceDestValuePair0'])
ixNet.commit()

################################################################################
# Assign ports
################################################################################
vports = ixNet.getList(ixNet.getRoot(), 'vport')
print "Assigning ports " + str(vports) + " to " + str(py.ports)
assignPorts = ixNet.execute('assignPorts', py.ports, [], ixNet.getList("/", "vport"), True)
if assignPorts != vports:
    raise TestFailedError("FAILED assigning ports. Got %s" % assignPorts)
else:
    print("PASSED assigning ports. Got %s" % assignPorts)

################################################################################
# Start All Protocols
################################################################################
print "Starting All Protocols"
ixNet.execute('startAllProtocols')
print "Sleep 30sec for protocols to start"
time.sleep(30)

################################################################################
# Generate, apply and start traffic
################################################################################
r = ixNet.getRoot()
ixNet.execute('generate', ti1)
ixNet.execute('apply', r + '/traffic')
ixNet.execute('start', r + '/traffic')
print "Sleep 30sec to send all traffic"
time.sleep(30)

################################################################################
# Checking Stats to see if traffic was sent OK
################################################################################
print "Checking Stats to see if traffic was sent OK"
print "Getting the object for view Traffic Item Statistics"
viewName = "Traffic Item Statistics"
views = ixNet.getList('/statistics', 'view')
viewObj = ''
editedViewName = '::ixNet::OBJ-/statistics/view:\"' + viewName + '\"'
for view in views:
    if editedViewName == view:
        viewObj = view
        break
print "Getting the Tx/Rx Frames values"
txFrames = ixNet.execute('getColumnValues', viewObj, 'Tx Frames')
rxFrames = ixNet.execute('getColumnValues', viewObj, 'Rx Frames')
for txStat, rxStat in zip(txFrames, rxFrames):
    if txStat != rxStat:
        print "Rx Frames (%s) != Tx Frames (%s)" % (txStat, rxStat)
        raise TestFailedError('Fail the test')
    else:
        print "No loss found: Rx Frames (%s) = Tx Frames (%s)" % (txStat, rxStat)


session.EndReservation(reservation_id)
print "Sleep 10sec for reservation to end"
time.sleep(10)
session.DeleteReservation(reservation_id)
