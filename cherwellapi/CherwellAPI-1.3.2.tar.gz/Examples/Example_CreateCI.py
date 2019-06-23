from __future__ import print_function
from CherwellAPI import CherwellClient
import pickle

#########################################################################################
# This example demonstrates how the CherwellAPI Connection object can be used to
# create a new business object
###########################################################################################

#############################################
# Change the following to suit your instance
#############################################

base_uri = "http://52.63.131.135"
username = "CSDAdmin"
password = "CSDAdmin"
api_key = "b24526ea-a86a-4eae-b3de-ec2107c4cfe9"

# Create a new CherwellClient connection
cherwell_client = CherwellClient.Connection(base_uri, api_key, username, password)

# Get a template for a incident object
ci_computer = cherwell_client.get_new_business_object("ConfigComputer")

#Set some attributes
ci_computer.FriendlyName = "Davids Test Computer"

# Save the new CI
ci_computer.Save()




