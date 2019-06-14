from google.cloud import container_v1 as gke
from kubernetes import client as k8s
import google.auth

class Configuration(object):
	'''
	Provides functionality for configuring the Kubernetes client API.
	'''
	
	@staticmethod
	def configure_for_gke(zone, name):
		'''
		Configures the Kubernetes client API to communicate with a cluster running on Google Kubernetes Engine (GKE).
		
		- `zone` specifies the GCP zone of the Kubernetes cluster
		- `name` specifies the name of the Kubernetes cluster
		'''
		
		# Retrieve our credentials from the environment
		credentials, project = google.auth.default()
		
		# Verify that we were able to automatically detect the project ID
		if project is None:
			raise RuntimeError('could not auto-detect GCP project ID')
		
		# Create a GKE cluster management client using our credentials
		gkeClient = gke.ClusterManagerClient(credentials=credentials)
		
		# Retrieve the details for our GKE cluster so we can extract the Kubernetes master endpoint
		# (Note that this call will also populate our credentials with the bearer token needed to authenticate with the master)
		cluster = gkeClient.get_cluster(project, zone, name)
		
		# Populate our Kubernetes API client configuration
		# (Based on the example from here: <https://stackoverflow.com/a/52082629>)
		config = k8s.Configuration()
		config.api_key = {'authorization': 'Bearer ' + credentials.token}
		config.host = 'https://{}:443'.format(cluster.endpoint)
		config.verify_ssl = False
		k8s.Configuration.set_default(config)
