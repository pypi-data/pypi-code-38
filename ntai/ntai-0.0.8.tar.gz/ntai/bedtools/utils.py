def bed_str_to_list(bed:list):
    return [line.split('\t') for line in bed.rstrip('\n').split('\n')]

def bed_list_to_str(bed:str):
    return '\n'.join(['\t'.join([str(el) for el in sub]) for sub in bed])
