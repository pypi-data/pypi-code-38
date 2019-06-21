from connection import api_post


def add_port(port, protocol):
    return api_post('/port/add', data={"port": port, "protocol": protocol})


def remove_port(port, protocol):
    return api_post('/port/remove', data={"port": port, "protocol": protocol})
