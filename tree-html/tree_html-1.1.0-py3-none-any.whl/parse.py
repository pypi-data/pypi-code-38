import json


def parse_links(external_link):
    links = []
    for pair_string in external_link:
        url = pair_string.split()[0]
        text = " ".join(pair_string.split()[1:])  # text includes everything after url
        links.append({url: text})

    return links


def parse_tree(input_json):
    with open(input_json, "r") as f:
        tree = json.loads(f.read())

    tree = [node for node in tree if node["type"] != "report"]  # remove metadata
    top_level = tree[0]["name"]  # capture name of the top-level directory for display
    tree = tree[0]["contents"]  # remove top-level from tree for more useful display

    return tree, top_level
