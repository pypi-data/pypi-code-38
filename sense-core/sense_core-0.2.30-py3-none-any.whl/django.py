
def build_model_list(items, type='list'):
    return list(map(lambda item:item.to_json(type),items))
