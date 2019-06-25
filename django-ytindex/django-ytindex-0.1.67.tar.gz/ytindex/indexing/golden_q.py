# This seems like a reasonable query for right now.
# TODO: make better (Google has been working on theirs since 1994)

def GOLDENQ(query, inner_hit_size=10):
    return {
        'query': {
            'bool': {
                'should': [
                    {
                        'nested': {
                            'path': 'captions',
                            'query': {
                                'match': {
                                    'captions.content': query
                                }
                            },
                            'inner_hits': {
                                'size': inner_hit_size,
                                'highlight': {
                                    'fields': {
                                        'captions.content': {}
                                    }
                                }
                            }
                        }
                    },
                    {
                        'match': {
                            'description': query
                        }
                    }
                ]
            }
        },
        'highlight': {
            'fields': {
                'description': {}
            }
        }
    }
