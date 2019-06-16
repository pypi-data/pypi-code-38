from __future__ import print_function
from CherwellAPI import CherwellClient
import pickle
from CherwellAPI import Filter

#########################################################################################
# This example demonstrates how the CherwellAPI Connection object can be used to
# search for and retrieve one or more business objects matching a search query
###########################################################################################

#############################################
# Change the following to suit your instance
#############################################

base_uri = "http://52.63.131.135"
username = "CSDAdmin"
password = "CSDAdmin"
api_key = "b24526ea-a86a-4eae-b3de-ec2107c4cfe9"

# Create a new Cherwellclient connection
cherwell_client = CherwellClient.Connection(base_uri, api_key, username, password)

# Create a new AdhocFilter object - (passing True as the 2nd parameter will cause all fields to be returned)
search_filter = Filter.AdHocFilter("ConfigComputer")

# add a search filter where you are looking for a specific customer
search_filter.add_search_fields("FriendlyName", "contains", "Aaron")

# Specify the fields you want returned - (We didn't pass True as 2nd parameter when initialising the AdHocFilter)
search_filter.add_fields("RecID")

# Pass the AdhocFilter object to the CherwellClient's get_business_records
num_records, business_objects = cherwell_client.get_business_records(search_filter)

# Print number of records returned
print("Number of records: {}".format(num_records))

# Loop through the records returned
for business_object in business_objects:
    print(business_object)

