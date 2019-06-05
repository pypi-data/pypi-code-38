REGISTERED_RESOURCES = []

""" Decorator to add resources to client """


def reg_resource(cls):
    REGISTERED_RESOURCES.append(cls)
    return cls
