import json
from dotmap import DotMap


azure_config_json = "/mnt/users/qinglong/json/azure.json"

jf = open(azure_config_json)
jf_str = jf.read()

AzureConfig = DotMap(json.loads(jf_str))


# from .base import Config
#
#
# class Azure(Config):
#     _BATCH_ACCOUNT_NAME = "pibatch"
#     _BATCH_ACCOUNT_KEY = "Lk+yTKzFVsbLS87xIppHGr/tpGM/bBvUTOdA+h7O59MOoZ4laHgwROUdi3JWteN9+uQLFpz3N/p0CNTlQvAthQ=="
#     _BATCH_ACCOUNT_URL = "https://pibatch.eastus2.batch.azure.com"
#     _STORAGE_ACCOUNT_NAME = "pitechstorage"
#     _STORAGE_ACCOUNT_KEY = "NZCHgnrm69WTxqC4yHY7+/HdNODCTIP18S5OStKiWUv17OOiZgwvs1Zvpmoknit4J1dQ6RnF/rB/kJlEDpmJrQ=="
#
#     _POOL_ID = "DockerGate"
#     _POOL_NODE_COUNT = 2
#     _POOL_VM_SIZE = "STANDARD_A1_v2"
#     _JOB_ID = "DockerGateJob"
#     _STANDARD_OUT_FILE_NAME = "stdout.txt"
#     _NODE_AGENT_SKU_ID = "batch.node.ubuntu 16.04"
#
#     _IMAGE_NAME = "opengatecollaboration/gate:8.2"
