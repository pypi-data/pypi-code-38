import bashlex
import itertools


def proc_line(line):
    parts = bashlex.parse(line)
    assert len(parts) == 1
    ast = parts[0]
    return ast


def find_recursive_words(ast):
    if not hasattr(ast, 'parts'):
        return []
    else:
        ret_from_children = list(itertools.chain.from_iterable(
            find_recursive_words(part) for part in ast.parts))

        if ast.kind == 'word' and ast.parts:
            ret_from_children.append(ast)

        return ret_from_children


def validate_parser(f):
    err_lines = []
    for i, line in enumerate(f):
        try:
            ast = proc_line(line)
        except:
            err_lines.append(i)
    return err_lines


def find_all_rec_words(f):
    result = {}
    for i, line in enumerate(f):
        try:
            ast = proc_line(line)
            nodes = find_recursive_words(ast)
            if nodes:
                result[i] = nodes
        except:
            pass
    return result


def find_the_kinds(d):
    kinds = set()
    for key, node_list in d.items():
        for i, node in enumerate(node_list):
            for part in node.parts:
                kinds.add(part.kind)
    return kinds


def examine_hypo(d):
    err_list = []
    for key, node_list in d.items():
        for i, node in enumerate(node_list):
            for part in node.parts:
                if part.kind not in ['parameter', 'commandsubstitution', 'tilde', 'processsubstitution']:
                    err_list.append((key, i))
                    break
    return err_list


def find_code_indices_for_kind(d, kind):
    found_list = []
    for key, node_list in d.items():
        for i, node in enumerate(node_list):
            for part in node.parts:
                if part.kind == kind:
                    found_list.append((key, i))
                    break
    return found_list


def find_nodes_for_kind(d, indices):
    nodes = []
    for i, j in indices:
        node = d[i][j]
        nodes.append(node)
    return nodes


def find_words_for_kind(d, indices):
    words = []
    for i, j in indices:
        node = d[i][j]
        words.append(node.word)
    return words


def determine_cst_type(cst_str):
    if cst_str.startswith('$(') and cst_str.endswith(')'):
        cst_type = 'dollar'
    elif cst_str.startswith('`') and cst_str.endswith('`'):
        cst_type = 'backtick'
    else:
        cst_type = 'unknown'
    return cst_type


def find_clipped_word_nodes(d):
    err_lines = []
    for line_no, nodes in d.items():
        for node in nodes:
            if len(node.word) != node.pos[1] - node.pos[0] - 2:
                err_lines.append(line_no)
                break
    return err_lines


CST_ERR_TRAIN = [157, 162, 533, 624, 1681, 4694, 4791, 5499]

if __name__ == '__main__':
    train_f = open('/Users/ruoyi/Projects/PycharmProjects/nl2bash/data/bash/test.cm.filtered')
    d = find_all_rec_words(train_f)
    train_f.seek(0)
    lines = train_f.readlines()

    from natlang.format.bashJSON import process_node, CST_KIND, PST_KIND, remap_pos, determine_pst_type

    # children = process_node(d[1][0], lines[1])

    KIND = PST_KIND
    cst_indices = find_code_indices_for_kind(d, KIND)
    err_lines = []
    for i, j in cst_indices:
        line = lines[i]
        node = d[i][j]
        for child in node.parts:
            if child.kind == KIND:
                remapped_pos = remap_pos(node, child, line)
                pst_str = node.word[slice(*remapped_pos)]
                cst_type = determine_pst_type(pst_str)
                if cst_type == 'unknown':
                    err_lines.append(i)
