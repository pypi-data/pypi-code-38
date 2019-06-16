import json
import re


def build_latlon(raw_string):
    lat, lon = raw_string.split(",")
    return (float(lat), float(lon))


def parse_ao_json(dom, key):
    json_script = (
        dom.find("script", text=re.compile(r"AtlasObscura\." + key))
        .get_text(strip=True)
        .split(" = ", 1)[1]
        .split(";")[0]
    )
    return json.loads(json_script)
