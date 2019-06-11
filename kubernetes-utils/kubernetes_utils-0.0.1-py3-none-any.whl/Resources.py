from kubernetes import client as k8s

class Resources(object):
	'''
	Provides functionality for managing resources on a Kubernetes cluster.
	'''
	
	
	# Namespaces
	
	@staticmethod
	def create_namespace(name):
		'''
		Creates a new Kubernetes namespace.
		'''
		
		# Create a Namespace object
		namespace = k8s.V1Namespace(
			metadata = k8s.V1ObjectMeta(
				name = name
			)
		)
		
		# Submit the namespace to the Kubernetes master
		return k8s.CoreV1Api().create_namespace(body=namespace)
	
	@staticmethod
	def delete_namespace(name):
		'''
		Deletes an existing Kubernetes namespace.
		'''
		return k8s.CoreV1Api().delete_namespace(name)
	
	
	# Jobs
	
	@staticmethod
	def create_job(namespace, name, spec):
		'''
		Creates and submits a new Kubernetes Batch API Job object.
		
		- `namespace` specifies the namespace in which the job should be created.
		- `name` specifies the name of the job.
		- `spec` provides the Pod specification for the job.
		'''
		
		# Create a Job object
		job = k8s.V1Job(
			metadata = k8s.V1ObjectMeta(
				name = name
			),
			spec = k8s.V1JobSpec(
				template = k8s.V1PodTemplateSpec(
					metadata = k8s.V1ObjectMeta(
						
						# Prevent cluster autoscaling from interrupting the job
						annotations = {
							'cluster-autoscaler.kubernetes.io/safe-to-evict': 'false'
						},
						
						# Explicitly label the pod(s) for the job with the job name
						# (Note that recent versions of Kubernetes automatically provide the `job-name` label with this value)
						labels = {
							'name': name
						}
					),
					
					spec = spec
				)
			)
		)
		
		# Submit the job to the Kubernetes master
		return k8s.BatchV1Api().create_namespaced_job(namespace=namespace, body=job)
	
	
	# Network Policies
	
	@staticmethod
	def create_network_policy(namespace, name, spec):
		'''
		Creates and submits a new Kubernetes NetworkPolicy object.
		
		- `namespace` specifies the namespace in which the network policy should be created.
		- `name` specifies the name of the network policy.
		- `spec` provides the specification for the network policy.
		'''
		
		# Create a NetworkPolicy object
		policy = k8s.V1beta1NetworkPolicy(
			metadata = k8s.V1ObjectMeta(
				name = name
			),
			spec = spec
		)
		
		# Submit the network policy to the Kubernetes master
		return k8s.ExtensionsV1beta1Api().create_namespaced_network_policy(namespace=namespace, body=policy)
	
	
	# Services
	
	@staticmethod
	def create_headless_service(namespace, name, selector, ports=None):
		'''
		Creates a Kubernetes headless service for the specified pod selector.
		
		- `namespace` specifies the namespace in which the service should be created.
		- `name` specifies the name of the service, which will be used for DNS resolution.
		- `selector` specifies the Pod selector that the service will match.
		- `ports` optionally specifies a list of ports to expose. Defaults to TCP port 80.
		'''
		
		# If the user didn't specify a list of ports then default to TCP port 80
		if ports is None:
			ports = [
				k8s.V1ServicePort(
					port = 80,
					protocol = 'TCP'
				)
			]
		
		# Create a Service object
		service = k8s.V1Service(
			metadata = k8s.V1ObjectMeta(
				name = name
			),
			spec=k8s.V1ServiceSpec(
				cluster_ip = 'None',
				ports = ports,
				selector = selector
			)
		)
		
		# Submit the service to the Kubernetes master
		return k8s.CoreV1Api().create_namespaced_service(namespace=namespace, body=service)
