from ..person_pb2 import Person

q = [Person][0]()

types = {
    'my_person': Person,
}

p = types['my_person']()
