_cram_to_word_net_object_ = {'bowl': 'bowl.n.01',
                             'cup': 'cup.n.01',
                             'spoon': 'spoon.n.01',
                             'breakfast-cereal': 'cereal.n.03',
                             'drawer': 'drawer.n.01',
                             'milk': 'box.n.01'
                             }


def map_cram_object_type_to_word_net_instance(cram_object_type):
    return _cram_to_word_net_object_.get(cram_object_type.lower(), 'object.n.01')