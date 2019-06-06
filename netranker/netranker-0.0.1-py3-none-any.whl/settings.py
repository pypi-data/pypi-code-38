from secrets import token_hex

import netranker.storage
import netranker.samplers

HMAC_KEY = token_hex(256)
RESTFUL_JSON = {'ensure_ascii': False}
CARD_STORAGE = netranker.storage.InMemoryCardStorage()
RESULT_STORAGE = netranker.storage.InMemoryResultStorage()
SAMPLER = netranker.samplers.SimpleRandom(CARD_STORAGE)
