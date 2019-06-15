from .errors import *


def parse_export_rule(destination, filters):
    return {"destination": str(destination), "filters": list(filters)}
def parse_anchors(start, end):
    return {"start": str(start), "end": str(end)}
def parse_format(js, css):
    return {"js": str(js), "css": str(css)}
