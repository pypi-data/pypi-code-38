import game


def get_variants(macro_name):
    if macro_name == 'unit_name':
        return game.get_units_list()
    return []
