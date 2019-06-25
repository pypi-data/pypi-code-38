# --------------------------------------------------------
# PyTorchCaffe
# Licensed under The MIT License [see LICENSE for details]
# Written by xiaohang 2017.12.16
# --------------------------------------------------------
from __future__ import print_function
from collections import OrderedDict


def parse_caffemodel(caffemodel):
    try:
        import ptcaffe.proto.caffe_pb2 as caffe_pb2
    except ImportError:
        import proto.caffe_pb2 as caffe_pb2
    model = caffe_pb2.NetParameter()
    print('Loading caffemodel: %s' % caffemodel)
    with open(caffemodel, 'rb') as fp:
        model.ParseFromString(fp.read())

    return model


def replace_block_macro(props, block):
    for key, value in block.items():
        if isinstance(value, OrderedDict):
            replace_block_macro(props, value)
        elif isinstance(value, (list, tuple)) and isinstance(value[0], OrderedDict):
            for v in value:
                replace_block_macro(props, v)
        elif len(value) > 0 and value[0] == '@':
            block[key] = props[value[1:]]


def replace_prototxt_macro(net_info):
    props = net_info['props']
    layers = net_info['layers']
    for layer in layers:
        replace_block_macro(props, layer)


def parse_key_value(line):
    def parse_key(line):
        pos = line.find(':')
        key = line[0:pos]
        key = key.strip()
        rest_line = line[pos + 1:]
        return key, rest_line

    def parse_value(line):
        line = line.strip()
        value = line
        if line[0] == '"':
            assert(line[-1] == '"')
            return line[1:-1]
        elif line[0] == "'":
            assert(line[-1] == "'")
            return line[1:-1]
        else:
            return value
    key, rest_line = parse_key(line)
    value = parse_value(rest_line)
    return key, value


debug_line_num = 0
debug_protofile = ""

def debug_position():
    return "%s:%d" % (debug_protofile, debug_line_num+1)


def parse_prototxt(protofile, replace_macro=True):
    global debug_protofile
    debug_protofile = protofile

    def update_line_num(c):
        global debug_line_num
        if c == "\n":
            debug_line_num += 1

    def get_content_until(fp, *stop_chars):
        if not isinstance(stop_chars, tuple):
            stop_chars = [stop_chars]
        c = fp.read(1)  # .decode('ascii')
        update_line_num(c)
        buf = []
        while c not in stop_chars:
            buf += c
            c = fp.read(1)  # .decode('ascii')
            update_line_num(c)
        return ''.join(buf), c

    def parse_python_param_str(param_str):
        block = OrderedDict()
        lines = param_str.split("\\n")
        for line in lines:
            key, value = line.split(':')
            key = key.strip()
            value = value.strip()
            if key[0] in ['"', "'"] and key[0] == key[-1]:
                key = key[1:-1]
            if value[0] in ['"', "'"] and value[0] == value[-1]:
                value = value[1:-1]
            if value.find('python/tuple') >= 0:
                value = value.split('[')[1].rstrip(']')
            block[key] = value
        return block

    keywords = [':', '{', '}', ',', '[', ']', '(', ')']
    blankchars = [' ', "\n", "\t", "\r"]
    def get_one_token(fp):
        c = fp.read(1)  # .decode('ascii')
        update_line_num(c)
        # string with quotes
        if c == '"' or c == "'":
            result, last = get_content_until(fp, c)
            return result, "str"
        # comment
        elif c == '#':
            result, last = get_content_until(fp, "\n", "\r")
            return result, "#"
        # EOF
        elif c == '':
            return '', "eof"
        # skip chare
        elif c in blankchars: #[' ', "\n", "\t", "\r"]:
            return c, "blank"
        # key char
        elif c in keywords: # [':', '{', '}', ',', '[', ']']:
            return c, "keyword"
        # string without quotes
        else:
            fp.seek(fp.tell() - 1)  # fp.seek(-1, 1)
            result, last = get_content_until(fp, *(blankchars+keywords))
            if last in keywords: # shift back one char
                fp.seek(fp.tell() - 1)  # fp.seek(-1, 1)
            return result, "str"

    # to avoid recursive explosion
    def get_next_token(fp):
        result, result_type = get_one_token(fp)
        while result_type not in ['str', 'eof', 'keyword']:
            result, result_type = get_one_token(fp)
        return result

    def parse_list(fp, stop_char):
        output = []
        next_token = get_next_token(fp)
        while next_token != stop_char:
            assert next_token != ',', '%s parse list error, uncessary ","' % debug_position()
            output.append(next_token)
            next_token = get_next_token(fp)
            if next_token == stop_char: break
            assert next_token == ',' , '%s parse list error, next_token should be ","' % debug_position()
            next_token = get_next_token(fp)
        return output


    def parse_block(fp, stop_char):
        block = OrderedDict()
        next_token = get_next_token(fp)
        while next_token != stop_char:
            key = next_token
            assert key not in keywords, '%s unknown key "%s"' % (debug_position(), key)

            sep = get_next_token(fp)
            assert sep in [':', '{'], '%s unknown seperation' % debug_position()
            if sep == ':':
                value = get_next_token(fp)
                if value == '{':
                    print('Warning: unnecessary : before {')
                    block_value = parse_block(fp, '}')
                    value = block_value
                elif value == '[':
                    value = parse_list(fp, ']')
                elif value == '(':
                    value = parse_list(fp, ')')
                else:
                    pass
            elif sep == '{':
                value = parse_block(fp, '}')
                if key == "python_param" and 'param_str' in value:
                    value['param_str'] = parse_python_param_str(value['param_str'])
            if key == 'layer' and sep == '{':
                if stop_char != '':
                    lname = value['name']
                    assert False, '%s parse layer %s error which should not be included' % (debug_position(), lname)
            if key in block:
                if isinstance(block[key], list):
                    block[key].append(value)
                else:
                    block[key] = [block[key], value]
            else:
                block[key] = value
            next_token = get_next_token(fp)
        return block

    fp = open(protofile, 'r')
    props = parse_block(fp, '')  # parse until the end of file
    if 'layer' in props:
        net_info = OrderedDict()
        net_info['props'] = props
        if isinstance(props['layer'], list):
            net_info['layers'] = props['layer']
        else:
            net_info['layers'] = [props['layer']]
        del props['layer']
        if 'solver' in props:
            net_info['solver'] = props.pop('solver')
        if 'server' in props:
            net_info['server'] = props.pop('server')
        if replace_macro:
            replace_prototxt_macro(net_info)
        return net_info
    else:
        return props


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_all_upper(s):
    is_alpha_exist = False
    for i in s:
        if i.isalpha():
            is_alpha_exist = True
            break
    return is_alpha_exist and s == s.upper()


def print_prototxt(net_info):
    # whether add double quote
    def format_value(value):
        #str = u'%s' % value
        # if str.isnumeric():
        if is_number(value):
            return value
        elif value in ['true', 'false']:
            return value
        elif is_all_upper(value):
            return value
        else:
            return '\"%s\"' % value

    def print_block(block_info, prefix, indent):
        blanks = ''.join([' '] * indent)
        print('%s%s {' % (blanks, prefix))
        for key, value in block_info.items():
            if isinstance(value, OrderedDict):
                print_block(value, key, indent + 4)
            elif isinstance(value, list):
                for v in value:
                    print('%s    %s: %s' % (blanks, key, format_value(v)))
            else:
                print('%s    %s: %s' % (blanks, key, format_value(value)))
        print('%s}' % blanks)

    props = net_info['props']
    layers = net_info['layers']
    print('name: \"%s\"' % props['name'])
    print('input: \"%s\"' % props['input'])
    print('input_dim: %s' % props['input_dim'][0])
    print('input_dim: %s' % props['input_dim'][1])
    print('input_dim: %s' % props['input_dim'][2])
    print('input_dim: %s' % props['input_dim'][3])
    print('')
    for layer in layers:
        print_block(layer, 'layer', 0)


def save_prototxt(net_info, protofile):
    fp = open(protofile, 'w')
    # whether add double quote

    def format_value(value):
        #str = u'%s' % value
        # if str.isnumeric():
        if is_number(value):
            return value
        elif value in ['true', 'false']:
            return value
        elif is_all_upper(value):
            return value
        else:
            return '\"%s\"' % value

    def print_block(block_info, prefix, indent):
        blanks = ''.join([' '] * indent)
        print('%s%s {' % (blanks, prefix), file=fp)
        import sys
        for key, value in block_info.items():
            if isinstance(value, OrderedDict):
                print_block(value, key, indent + 4)
            elif isinstance(value, list) and (isinstance(value[0], OrderedDict)):
                for v in value:
                    print_block(v, key, indent + 4)
            elif isinstance(value, list) and (\
                (sys.version_info[0]!=3 and (isinstance(value[0], (str, unicode)))) or \
                (sys.version_info[0]==3 and (isinstance(value[0], str))) \
                ):
                for v in value:
                    print('%s    %s: %s' % (blanks, key, format_value(v)), file=fp)
            else:
                print('%s    %s: %s' % (blanks, key, format_value(value)), file=fp)
        print('%s}' % blanks, file=fp)

    props = net_info['props']
    print('name: \"%s\"' % props['name'], file=fp)
    if 'input' in props:
        if isinstance(props['input'], str):
            print('input: \"%s\"' % props['input'], file=fp)
            if 'input_dim' in props:
                print('input_dim: %s' % props['input_dim'][0], file=fp)
                print('input_dim: %s' % props['input_dim'][1], file=fp)
                print('input_dim: %s' % props['input_dim'][2], file=fp)
                print('input_dim: %s' % props['input_dim'][3], file=fp)
            else:
                print_block(props['input_shape'], 'input_shape', 0)
        else:
            for idx, input in enumerate(props['input']):
                print('input: \"%s\"' % input, file=fp)
                print_block(props['input_shape'][idx], 'input_shape', 0)

    print('', file=fp)
    layers = net_info['layers']
    for layer in layers:
        print_block(layer, 'layer', 0)
    fp.close()


def parse_solver(solverfile):
    solver = OrderedDict()
    lines = open(solverfile).readlines()
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0] == '#':
            continue
        if line.find('#') >= 0:
            line = line.split('#')[0]
        key, value = parse_key_value(line)
        if key not in solver:
            solver[key] = value
        elif not isinstance(solver[key], list):
            solver[key] = [solver[key], value]
        else:
            solver[key].append(value)
    return solver


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: python prototxt.py model.prototxt')
        exit()

    net_info = parse_prototxt(sys.argv[1])
    print_prototxt(net_info)
    save_prototxt(net_info, 'tmp.prototxt')
