import json

""" haliot resources are inherently kept closely aligned to the format of application/hal+json to minimize costly
    manipulations and serialization to json. We make no assumptions about the structure of the body
    of a haliot resource; any python resource that can resolve to valid json is allowed. """
class Resource:
    _links = None

    """ Adds an object's attributes verbatim to a haliot resource """
    def __init__(self, model):
        self._links = {}
        for key, value in vars(model).items():
            setattr(self, key, value)

    """ Adds a link to the current haliot resource while maintaining its inherently well structured hal+json like form.
        the link to provide is a haliot link and rel its associated link relation"""
    def addLink(self, rel, link):
        if link != None:
            if rel == "self":
                self._links[rel]=link
            if rel != "self":
                l = self._links.get(rel)
                if l:
                    self._links[rel].append(link)
                else:
                    self._links[rel]=[]
                    self._links[rel].append(link)


    """ Serializes an inherently well structured haliot resource to application/hal+json """
    def serialize(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
                          sort_keys=True,
                          indent=4)

""" Allows for the creation of a haliot link with any quantity of properties, including properties that
    would not be supported directly by the hal specification. Projects are responsible for providing
    mandatory attributes as the hal spec requires haliot links do not include the rel, which must be provided
    as part of addLink. """
class Link:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
