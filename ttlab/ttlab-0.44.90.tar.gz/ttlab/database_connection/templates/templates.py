class Templates:
    master = {
        'owner': None,
        'identifier': None,
        'batch_nr': None,
        'name': None,
        'history': None,
        'description': None,
        'extra': None
    }

    crucial_key_values = ['owner', 'name', 'history', 'description']

    alloy = {
        'substrate': {
            'material': None,
            'dimensions': None
        },
        'materials': {
            'material': [],
            'composition': []
        },
        'dimensions': {
            'diameter': None,
            'height': None
        }
    }

    @staticmethod
    def get_alloy_template(self):
        template = Templates.master.copy()
        template.description = {
            'type': 'alloy',
            'sample_info': Templates.alloy.copy()
        }
        return template

    @staticmethod
    def sample_has_neccessary_keys(sample):
        for key in Templates.master.keys():
            if key not in sample.keys():
                return False
        return True


    @staticmethod
    def is_valid_sample(sample):
        return Templates.sample_has_neccessary_keys(sample) and Templates.sample_has_neccessary_values(sample)

    @staticmethod
    def sample_has_neccessary_values(sample):
        for key in Templates.crucial_key_values:
            if sample[key] is None:
                return False
        return True

