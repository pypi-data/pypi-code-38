from eeve.variable import Variable


def init(*args, **kwargs):
    print('initialization args:', args, kwargs)


def run(*args, index=0, **kwargs):
    index_is_var = hasattr(index, 'value')
    idx = index.value if index_is_var else index
    print(f'run args ({idx}):', args, kwargs, end='    ')
    try:
        if index_is_var:
            index.value += 1
        else:
            index += 1
    except Exception as e:
        print(e, end='')
        index = 1

    print()
    return {'index': index}


actions = {'test action': {'init': init, 'run': run}}
