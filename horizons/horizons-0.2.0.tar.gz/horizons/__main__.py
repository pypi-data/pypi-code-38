from horizons import Horizons, BodyResult
import json
import logging


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
horizons_log = logging.getLogger(__name__)
horizons_log.setLevel(logging.INFO)
horizons_log.propagate = True

fh = logging.FileHandler('horizons.log')
fh.setLevel(logging.DEBUG)
logging.getLogger().addHandler(fh)


with Horizons() as h:
    bodies = h.get_major_bodies()
    bodies_as_dicts = [body._asdict() for body in bodies]
    with open('bodies.json', 'w+') as f:
        f.write(json.dumps(bodies_as_dicts, indent=2))

    print(h.get_radius('399'))
    print(h.get_mass('399'))

    vector_map = {}
    for body in h.get_planets():
        vectors = h.get_vectors(body.id)
        vector_map[body.id] = vectors._asdict()
    for body in h.get_moons():
        parent_id = f'{body.id[0]}99'
        vectors = h.get_vectors(body.id, center=parent_id)
        vector_map[body.id] = vectors._asdict()
    with open('vectors.json', 'w+') as f:
        f.write(json.dumps(vector_map, indent=2))
