"""
Definitions used throught the program.
"""

BLUEPRINT = 'blueprint'
ROUTINE = 'routine'

FORMAT_OPTIONS = {
	'1'				: '{}',
	'2,'			: '{},{}',
	'{2,}'			: '{{{},{}}}',
	'[2,]'			: '[{},{}]',
	'(2,)'			: '({},{})'
}


"""
General flags blueprint 
"""
GENERAL_SCHEMA = {
	'type'					: 'object',
	'additionalProperties'	: False,
	'required'				: ['settings', 'flags'],
	'properties'			: {
		'settings' : {
			'type' 		 : 'object',
			'additionalProperties'	: False,
			'required'	 : ['required_flags'],
			'properties' : {
				'required_flags': {
					'type': 'array'
				},
				'libraries': {
					'type'	: 'array'
				}
			}
		},
		'flags' : {
			'type' 		 : 'object'
		}
	}
}

"""
Flag schema
"""
FLAG_SCHEMA = {
	'type':'object',
	'required':[  
	    'flag',
	    'unifier',
	    'format'
	],
	'additionalProperties':False,
	'properties':{  
	    'flag':{  
	        'type':[  
	            'null',
	            'string'
	        ]
	    },
	    'unifier':{  
	        'type':[  
	            'null',
	            'string'
	        ]
	    },
	    'format':{  
	        'type':'object',
	        'dependencies': {
			    'match': ['pattern']
			},
	        'properties':{  
	            'preset':{  
	                'type': ['null', 'string', 'object'],
	                'pattern': '(1)|(2,)|((2,))|([2,])|({{2,}})'
	            },
	            'list':{  
	                'type':'object',
	                'required'	 : ['divider'],
	                'properties':{  
	                    'divider':{  
	                        'type':'string'
	                    }
	                }
	            },
	            'pattern': {},
	            'match': {
	            	'type': 'boolean'
	            },
	            'toggle': {
	            	'type': 'boolean'
	            }
	        }
	    }
	}
}