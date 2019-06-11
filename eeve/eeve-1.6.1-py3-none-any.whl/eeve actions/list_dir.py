import os


def run(path, return_full_path=False):
    result = os.listdir(path)
    if return_full_path:
        for i, f in enumerate(result):
            result[i] = os.path.join(path, f)
    return {'file_list': result}


actions = {"list dir": {'run': run}}
