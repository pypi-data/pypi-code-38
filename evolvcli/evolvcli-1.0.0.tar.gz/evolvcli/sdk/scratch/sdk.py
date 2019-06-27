from evolvclient.config import EvolvConfig
from evolvclient.client import EvolvClient

domain = "experiments-stg.evolv.ai"
api_key = "6mo6kQhceT8YGl59lvBEW9vfGSrcD2gp89jq127I"

evolv_config = EvolvConfig(domain, api_key)
evolv_client = EvolvClient(evolv_config)

result = evolv_client.get_account()

print(result)
