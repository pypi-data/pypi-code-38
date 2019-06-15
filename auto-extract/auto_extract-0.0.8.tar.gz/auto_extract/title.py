from auto_extract.utils import normalize
from auto_extract.utils import get_text_and_tail


def fscore(x, y):
    try:
        z = sum([w in y for w in x]) / len(x)
        z2 = sum([w in x for w in y]) / len(y)
        return (2 * z * z2) / (z + z2)
    except ZeroDivisionError:
        return 0


def generate_rule_dictionary():
    headers = ["h{}".format(i) for i in range(1, 5)]
    # tags = ['strong', 'b', 'div']
    tags = []
    atts = ["id", "class", ""]
    res = {k: {kk: {} for kk in atts} for k in headers + tags}
    it = 0
    for h in headers:
        for k in atts:
            it += 1
            res[h][k]["title"] = it
            it += 1
            res[h][k][""] = it
            it += 1
        res[h][""]["title"] = it
        it += 1
        res[h][""][""] = it
    # for t in tags:
    #     for k in atts:
    #         it += 1
    #         res[t][k]['title'] = it
    #         it += 1
    #         res[t][k][''] = 100
    #         it += 1
    #     res[t]['']['title'] = it
    #     it += 1
    #     if t != 'div':
    #         res[t][''][''] = it

    return res


def get_score_from_title_dict(node, dc):
    tag_found = dc.get(node.tag, "")
    if tag_found:
        maxi = 100
        for attribute in node.attrib:
            key_found = dc[node.tag].get(attribute, "")
            if key_found:
                if "title" in node.attrib[attribute]:
                    maxi = min(maxi, dc[node.tag][attribute]["title"])
                else:
                    maxi = min(maxi, dc[node.tag][attribute][""])
        # if maxi == 100:
        # maxi = dc[node.tag]['']['']
        return maxi, node.text_content()
    else:
        return 101, ""


def get_meta_titles(tree):
    res = []
    head = tree.find("head")
    if head is not None:
        for xp in [
            ".//title/text()",
            './/meta[contains(@name, "title")]/@content',
            './/meta[contains(@property, "title")]/@content',
        ]:
            res.extend(head.xpath(xp))
    return res


def sorted_title_candidates(tree, rule_dict):
    mins = []
    for node in tree.iter():
        score, ele = get_score_from_title_dict(node, rule_dict)
        stripped_ele = ele.strip()
        if stripped_ele and score != 101:
            mins.append((score, stripped_ele))

    return [x[1] for x in sorted(mins)]


rule_dc = generate_rule_dictionary()


def get_title(tree, url, rule_dict=rule_dc):
    texts = sorted_title_candidates(tree, rule_dict)
    metas = get_meta_titles(tree)
    # meta based on url
    url = url or "./"
    proposed = url.rstrip("/").split("/")[-1].split(".")[0]
    proposed = proposed.replace("-", " ").strip()
    proposed = " ".join([x if x.upper() == x else x.title() for x in proposed.split(" ")])
    if proposed:
        metas.append(proposed)
    maxs = 0
    title = ""
    for x in texts:
        xs = x.lower().split()
        for y in metas:
            ys = y.lower().split()
            newm = fscore(xs, ys)
            if newm > maxs:
                maxs = newm
                title = x
    if maxs < 0.3 and metas:
        title = metas[0]
    return title.split("|")[0].strip()


def get_title_index(tree, title):
    title_index = None
    for num, node in enumerate(tree.iter()):
        if normalize(get_text_and_tail(node)) == title:
            title_index = num
    if title_index is None:
        # fuzzy token text / title matching
        title_set = set(title.split())
        for num, node in enumerate(tree.iter()):
            text_content = get_text_and_tail(node)
            if text_content and len(text_content) < 500:
                text_set = set(text_content.split())
                if fscore(title_set, text_set) > 0.5:
                    title_index = num
                    break
    return title_index
