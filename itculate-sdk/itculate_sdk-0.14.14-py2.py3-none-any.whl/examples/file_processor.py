import json
import argparse

import itculate_sdk as itsdk

itsdk.init(provider="Print",
           api_key="b8NgSwETBuaFR30L3a8JP0F5NwJ55Ale",
           api_secret="zVZYK-w-UEP_aqFUSN7AWvsEFmYffnbaT_sHRcSamit73pZVJWy0eS2lrny6sC7c")


def process_file(file_path):
    print("Upload file {}".format(file_path))
    with open(file_path) as f:
        model = json.load(f)

    collector_id = model["collector_id"]
    tenant_id = model["tenant_id"]

    for vertex in model["vertices"]:  # type: dict
        vertex_type = vertex["_type"]
        vertex_name = vertex["_name"]
        vertex_keys = vertex["_keys"]
        vertex_data = {k: vertex[k] for k in vertex.keys() if k[0] != "_"}
        itsdk.add_vertex(
            collector_id=collector_id,
            vertex_type=vertex_type,
            name=vertex_name,
            keys=vertex_keys,
            data=vertex_data,
        )

    for edge in model["edges"]:
        source_keys = edge["_source_keys"]
        target_keys = edge["_target_keys"]
        edge_type = edge["_type"]
        itsdk.connect(
            collector_id=collector_id,
            topology=edge_type,
            source=source_keys,
            target=target_keys
        )

    itsdk.flush_all()


parser = argparse.ArgumentParser("file_path")
parser.add_argument("-p", dest="path", help="A path to the file.", type=str)
args = parser.parse_args()
process_file(args.path)
