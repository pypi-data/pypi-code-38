from kubernetes import client as k8s

class SpecFactory(object):
	'''
	Provides functionality for creating common spec objects for the Kubernetes client API.
	'''
	
	
	# Network Policy Specs
	
	@staticmethod
	def network_policy_dns_only(selector):
		'''
		Creates a NetworkPolicy spec for only allowing DNS resolution egress traffic.
		
		- `selector` provides the selector that matches the pods to which the network policy will apply.
		'''
		return k8s.V1beta1NetworkPolicySpec(
			egress = [
				k8s.V1beta1NetworkPolicyEgressRule(
					ports = [
						k8s.V1beta1NetworkPolicyPort(
							port = 53,
							protocol = 'TCP'
						),
						k8s.V1beta1NetworkPolicyPort(
							port = 53,
							protocol = 'UDP'
						)
					]
				)
			],
			pod_selector = selector,
			policy_types = ['Egress']
		)
	
	@staticmethod
	def network_policy_pods_only(selector, destination):
		'''
		Creates a NetworkPolicy spec for only allowing egress traffic to other pods.
		
		- `selector` provides the selector that matches the pods to which the network policy will apply.
		- `destination` provides the selector that matches the destination pods to which traffic will be allowed.
		'''
		return k8s.V1beta1NetworkPolicySpec(
			egress = [
				k8s.V1beta1NetworkPolicyEgressRule(
					to = [
						k8s.V1beta1NetworkPolicyPeer(
							pod_selector = destination
						)
					]
				)
			],
			pod_selector = selector,
			policy_types = ['Egress']
		)
	
	
	# Port specs
	
	@staticmethod
	def service_ports_from_container_ports(ports):
		'''
		Creates a list of ServicePort objects from a list of ContainerPort objects.
		'''
		return [
			k8s.V1ServicePort(
				port = containerPort.container_port,
				protocol = containerPort.protocol
			)
			
			for containerPort in ports
		]
