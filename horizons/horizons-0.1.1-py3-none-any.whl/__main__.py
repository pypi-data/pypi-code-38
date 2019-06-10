from horizons import Horizons, BodyResult
import json
import logging


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
horizons_log = logging.getLogger(__name__)
horizons_log.setLevel(logging.INFO)
horizons_log.propagate = True


with Horizons() as h:
    vector_map = {}
    for body in h.get_planets():
        vectors = h.get_vectors(body.id)
        vector_map[body.id] = vectors.__dict__
    for body in h.get_moons():
        parent_id = f'{body.id[0]}99'
        vectors = h.get_vectors(body.id, center=parent_id)
    with open('vectors.json', 'w+') as f:
        f.write(json.dumps(vector_map, indent=2))
