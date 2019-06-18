import yaml


def copy_and_replace(file_in, file_out, mapping, **kwargs):
    '''
    Copy a file and replace some placeholders with new values.
    '''
    separator = '@@'
    if 'separator' in kwargs:
        separator = kwargs['separator']
    file_in = open(file_in, 'r')
    file_out = open(file_out, 'w')
    s = file_in.read()
    for find, replace in mapping:
        find = separator + find + separator
        print(u'Replacing {0} with {1}'.format(find, replace))
        s = s.replace(find, replace)
    file_out.write(s)


def get_yaml(file_in):
    yamlfile = ''
    with open(file_in, 'r') as stream:
        try:
            yamlfile = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return yamlfile


def get_wildcards(file_in):
    wildcards = get_yaml(file_in)
    mapping = []
    for category in wildcards['variables']:
        categories = wildcards['variables'][category]
        for var in categories:
            a = var
            b = categories[var]
            wtuple = (a, b)
            mapping.append(wtuple)
    return mapping


def append_extension(file_in, file_out, extension):
    a = 0

    with open(file_in, "r") as in_file:
        buf = in_file.readlines()

    with open(file_out, "w") as out_file:
        for line in buf:
            if 'egg' in line and a == 0:
                line = line + "\n" + extension
                a += 1
            out_file.write(line)
