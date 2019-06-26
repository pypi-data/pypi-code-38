from googleapiclient import discovery as gcp_client
from remediate_gcp import utils 

'''
    A simple runbook which does nothing but returns the list of 
    VM resources
'''
def remediate(credentials, resource_details, context):
    debug = ['Starting runbook']
    project_id = resource_details['project_id']
    
    try:
            
        client = gcp_client.build('compute', 'v1', credentials=credentials)

        debug.append('Getting list of instances')
        vms = client.instances().list(project=project_id, zone='us-central1-a').execute()
        debug.append('Getting list of instances - successful\n')

        output = utils.generate_output({
            'total_number_of_instance': len(vms['items'])
            }, debug=debug)

    except Exception as e:
        output = utils.generate_error('Error encountered when running runbook remediate_sample', body=e, debug=debug)
    
    return output